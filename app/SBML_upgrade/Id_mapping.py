import rdflib
import requests
import io
import re
import os, sys
import json
import gzip
import itertools
import csv
from rdflib.namespace import XSD, DCTERMS, OWL
from app.Database_ressource_version import Database_ressource_version


class Id_mapping:
    def __init__(self, version, namespaces):
        """
        - ressource_uris: a dict with key as ressource name and values representing different URIs that may be associated to the ressource
        - ressources_ids: a dict with key as ressource name and values representing the ressource id in UniChem
        - graph_original_uri_prefix: a dict with key as ressource name and values as the URI used in the SBML graph
        - intra_ids_dict: a dict with key as ressource name and values containing the union of all the ids extracted for this ressource
        - uri_MetaNetX: a dict with key as ressource name and values representing the URI of the ressource in the MetaNetX RDF graph
        - namespaces: a dict of namespaces
        - version: the version of the ressource, if None date is used
        """
        self.ressource_uris = dict()
        self.ressources_ids = dict()
        self.graph_original_uri_prefix = dict()
        self.intra_ids_dict = dict()
        self.uri_MetaNetX = dict()
        self.namespaces = namespaces
        self.version = version
    
    def download_mapping_from_ftp(self, ressource_1, ressource_2, path_out):
        """
        This function is used to dowload the ressource mapping file from the ftp server
        - ressource_1: UniChem id of the ressource 1
        - ressource_2: UniChem id of the ressource 2
        - path_out: path to a directory to export data 
        """
        out = path_out + "data/"
        if not os.path.exists(out):
            os.makedirs(out)
        f_name = "src" + ressource_1 + "src" + ressource_2 + ".txt.gz"
        # One of the main issue is that the mapping between 2 ressources in provided on only one sens, so r1.vs.r2 or r2.vs.r1, wo we need to check if a file was dowloaded from the ftop, if not it's indicated that the mapping is represented in the reverse order.
        isReverse = False
        os.system("wget  -P " + out + " " + "ftp://ftp.ebi.ac.uk/pub/databases/chembl/UniChem/data/wholeSourceMapping/" + "src_id" + ressource_1 + "/" + f_name)
        if not os.path.isfile(out + f_name):
            print(ressource_1 + ' .vs. ' + ressource_2 + " was not found in this order, try in the order : " + ressource_2 + ' .vs. ' + ressource_1)
            isReverse = True
            f_name = "src" + ressource_2 + "src" + ressource_1 + ".txt.gz"
            os.system("wget -P " + out + " " + "ftp://ftp.ebi.ac.uk/pub/databases/chembl/UniChem/data/wholeSourceMapping/" + "src_id" + ressource_2 + "/" + f_name)
        # Parsing file : 
        f_input = gzip.open(out + f_name,'rt')
        header = f_input.readline()
        print(header)
        ids_ressource_1 = list()
        ids_ressource_2 = list()
        for line in f_input:
            columns = line.rstrip().split(sep='\t')
            ids_ressource_1.append(columns[0])
            ids_ressource_2.append(columns[1])
        # If data was found in the reverse order, we also return in the reverse order to keep the initial ids for ressource_1 and ressource_2
        if isReverse:
            return(ids_ressource_2, ids_ressource_1)
        return(ids_ressource_1, ids_ressource_2)
    
    def get_graph_ids_set(self, path_to_graph):
        """
        This function allow to parse an input SMBL RDF graph and get all the actual ids present in the graph ONLY for ressources that may have several uris.
        - path_to_graph: a path to the .ttl file of the SMBL graph
        - graph_original_uri_prefix: a dict with key as ressource name and value as the original root uri (so without the id) used in the graph. Exemple for Chebi : http://purl.obolibrary.org/obo/CHEBI_
        Note that keys in the dict must be the same as in the ressource_uris dict.
        """
        g = rdflib.Graph()
        g.parse(path_to_graph, format = 'turtle')
        query = g.query(
            """
            select distinct ?ref
            where {
                ?species a SBMLrdf:Species .
                ?species bqbiol:is ?ref .
                }
            """)
        uri_list = [uriRef[0].toPython() for uriRef in query]
        keys = [key for key in self.intra_ids_dict.keys() if len(self.graph_original_uri_prefix[key]) > 0]
        for uri in uri_list:
            for key in keys:
                split_uri = uri.split(self.graph_original_uri_prefix[key])
                if len(split_uri) > 1:
                    # Sachant que l'on a fai la requête avec distinct, pas besoin de union, on peut directement add, il n'y aura pas de duplicats
                    self.intra_ids_dict[key].add(split_uri[1])
    
    def create_graph_from_UniChem(self, path_out):
        """
        This function is used to create a graph or uri equivalences between different input ressource. Equivalence information are fetch from the WebService of UniChem. 
        Between ressource a skos:closeMatch relation is implemented (to avoid propaging false information)
        Between differents uris of the same ressource (called intra-uris) a skos:exactMatch relation is implemented
        - path_out: a path to out files
        """
        ressource_version_UniChem = Database_ressource_version(ressource = "ressources_id_mapping/UniChem", version = self.version)
        n_triples = 0
        subjects = set()
        path_out = path_out + ressource_version_UniChem.version + "/"
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        selected_ressource = [r for r in self.ressources_ids.keys() if len(self.ressources_ids[r]) > 0]
        cbn_resource = itertools.combinations(selected_ressource, 2)
        for ressource_pair in cbn_resource:
            r1 = ressource_pair[0]
            r2 = ressource_pair[1]
            g_name = (r1 + "_" + r2)
            print("Treating : " + r1 + " - " + r2 + " ...")
            current_graph = ressource_version_UniChem.create_data_graph(namespace_list  = ["skos"], namespace_dict = self.namespaces)
            # Le WevService semble mal fonctionner ... donc je suis passer par une nouvelle méthode où de download depuis le ftp :
            ids_r1, ids_r2 = self.download_mapping_from_ftp(self.ressources_ids[r1], self.ressources_ids[r2], path_out)
            # Si la requête précédement envoyée à échouée au passe à la paire de ressource suivante
            if ids_r1 is None or ids_r2 is None:
                print("Impossible to process information for identifiers equivalence between ressource " + r1 + " and " + r2 + "\n")
                continue
            n_ids = len(ids_r1)
            for id_index in range(n_ids):
                #  On écrit les équivalence inter-ressource seulement pour une URI de chaque ressource, le liens avec les autres se fera par le biais des équivalence intra-ressource
                uri_1, uri_2 = rdflib.URIRef(self.ressource_uris[r1][0] + ids_r1[id_index]), rdflib.URIRef(self.ressource_uris[r2][0] + ids_r2[id_index])
                current_graph.add((uri_1, self.namespaces["skos"]['closeMatch'], uri_2))
            # On écrit le graph :
            ressource_version_UniChem.add_DataDump(g_name + ".trig")
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            n_triples += len(current_graph)
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
            # Si il y a plusieurs URI pour la ressource, il faut préparer les identifiants pour les correspondances intra-ressource
            if len(self.ressource_uris[r1]) > 1:
                self.intra_ids_dict[r1] = self.intra_ids_dict[r1].union(ids_r1)
            if len(self.ressource_uris[r2]) > 1:
                self.intra_ids_dict[r2] = self.intra_ids_dict[r2].union(ids_r2)
        # On annote le graph :
        ressource_version_UniChem.add_version_namespaces(["void"], self.namespaces)
        ressource_version_UniChem.add_version_attribute(DCTERMS["description"], rdflib.Literal("Ids correspondances between differents ressources from UniChem"))
        ressource_version_UniChem.add_version_attribute(DCTERMS["title"], rdflib.Literal("Ids correspondances from UniChem"))
        ressource_version_UniChem.add_version_attribute(self.namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
        ressource_version_UniChem.add_version_attribute(self.namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
        ressource_version_UniChem.version_graph.serialize(destination=path_out + "ressource_info_ids_equivalence_UniChem_" + ressource_version_UniChem.version + ".ttl", format = 'turtle')
    
    def export_intra_eq(self, path_out):
        """
        This function is used to create a graph or URIs equivalences between the different URIs associated to a given ressource. E
        Between differents URIs of the same ressource (called intra-uris) a skos:exactMatch relation is implemented
        - path_out: a path to out files
        """
        ressource_version_intra = Database_ressource_version(ressource = "ressources_id_mapping/Intra", version = self.version)
        n_triples = 0
        subjects = set()
        path_out = path_out + ressource_version_intra.version + "/"
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        for r_name in self.intra_ids_dict.keys():
            g_name = r_name + "_intra"
            current_graph = ressource_version_intra.create_data_graph(namespace_list  = ["skos"], namespace_dict = self.namespaces)
            intra_ids = list(self.intra_ids_dict[r_name])
            for id in intra_ids:
                intra_uris = [rdflib.URIRef(prefix + id) for prefix in self.ressource_uris[r_name]]
                for current_uri, next_uri in zip(intra_uris, intra_uris[1:]):
                    current_graph.add((current_uri, self.namespaces["skos"]['exactMatch'], next_uri))
            ressource_version_intra.add_DataDump(g_name + ".trig")
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
            n_triples += len(current_graph)
        ressource_version_intra.add_version_namespaces(["void"], self.namespaces)
        ressource_version_intra.add_version_attribute(DCTERMS["description"], rdflib.Literal("URIs equivalence inside a ressource"))
        ressource_version_intra.add_version_attribute(DCTERMS["title"], rdflib.Literal("URIs equivalence inside a ressource"))
        ressource_version_intra.add_version_attribute(self.namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
        ressource_version_intra.add_version_attribute(self.namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
        ressource_version_intra.version_graph.serialize(destination=path_out + "ressource_info_intra_ids_equivalence_" + ressource_version_intra.version + ".ttl", format = 'turtle')
    
    def import_table_infos(self, config_file):
        """
        This function is used to import the configuration file. The configuration file is a tabulated file with columns containing information of each ressource in this order:
        ressource name, ressource UniChem id, all ressource URIs (comma separated), URI used on SBML, URI used in MetaNetX 
        """
        with open(config_file, "r") as config:
            for l in config:
                columns = l.split("\t")
                self.ressources_ids[str(columns[0])] = str(columns[1])
                self.ressource_uris[str(columns[0])] = str(columns[2]).split(',')
                self.graph_original_uri_prefix[str(columns[0])] = str(columns[3])
                # Use rstrip because it's the last column
                self.uri_MetaNetX[str(columns[0])] = str(columns[4]).rstrip()
        self.intra_ids_dict = {key: set() for key in self.ressource_uris.keys() if len(self.ressource_uris[key]) > 1 }
    
    def get_mapping_from_MetanetX(self, graph_metaNetX, ressource):
        """
        This function is used to extract ids equivalence from the MetaNetX graph using a SPARQL query
        - graph_metaNetX: a rdflib.Graph associated to the MetaNetX graph.
        - ressource: a ressource name
        """
        requested_uri = self.uri_MetaNetX[ressource]
        metaNetX_prefix = self.uri_MetaNetX["metanetx"]
        query = graph_metaNetX.query(
        """
        SELECT (strafter(STR(?metabolite),\"""" + metaNetX_prefix + """\") as ?metaNetX_ids) (strafter(STR(?xref),\"""" + requested_uri + """\") as ?ressource_ids)
        WHERE {
            ?metabolite a mnx:CHEM .
            ?metabolite mnx:chemXref ?xref
            FILTER(STRSTARTS(STR(?xref), \"""" + requested_uri + """\"))
        }
        """)
        metaNetX_ids = [id[0].toPython() for id in query]
        ressource_ids = [id[1].toPython() for id in query]
        return metaNetX_ids, ressource_ids
    
    def get_mapping_from_MetanetX_inter_ressource(self, graph_metaNetX, uri_r1, uri_r2):
        query = graph_metaNetX.query(
        """    
        SELECT (strafter(STR(?xref),\"""" + uri_r1 + """\") as ?uri_r1) (strafter(STR(?xref2),\"""" + uri_r2 + """\") as ?uri_r2) 
        WHERE {
            ?metabolite a mnx:CHEM .
            ?metabolite mnx:chemXref ?xref
            FILTER(STRSTARTS(str(?xref), \"""" + uri_r1 + """\"))
            ?metabolite mnx:chemXref ?xref2
            FILTER(STRSTARTS(str(?xref2), \"""" + uri_r2 + """\"))
        }
        """)
        ids_ressource_1 = [id[0].toPython() for id in query]
        ids_ressource_2 = [id[1].toPython() for id in query]
        return ids_ressource_1, ids_ressource_2
    
    def create_graph_from_MetaNetX(self, graph_metaNetX, path_out):
        """
        This function is used to create a graph or uri equivalences between MetaNetX identifiers and other ressources. Equivalence information are fetch from the MetaNetX RDF graph. 
        Between ressource a skos:closeMatch relation is implemented (to avoid propaging false information)
        - path_out: a path to out files
        """
        ressource_version_MetaNetX = Database_ressource_version(ressource = "ressources_id_mapping/MetaNetX", version = self.version)
        n_triples = 0
        subjects = set()
        path_out = path_out + ressource_version_MetaNetX.version + "/"
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        selected_ressource = [r for r in self.uri_MetaNetX.keys() if len(self.uri_MetaNetX[r]) > 0 and r != "metanetx"]
        for ressource in selected_ressource:
            # On crée le graph MetaNetX .vs. ressource
            print("Treating ressource: " + ressource + " with MetaNetX ...")
            g_name = ("MetaNetX_" + ressource)
            current_graph = ressource_version_MetaNetX.create_data_graph(namespace_list  = ["skos"], namespace_dict = self.namespaces)
            metaNetX_ids, ressource_ids = self.get_mapping_from_MetanetX(graph_metaNetX, ressource)
            if metaNetX_ids is None or ressource_ids is None:
                print("Impossible to process information for identifiers equivalence between MetaNetX and " + ressource + "\n")
                continue
            n_ids = len(metaNetX_ids)
            for id_index in range(n_ids):
                #  On écrit les équivalence inter-ressource seulement pour une URI de chaque ressource, le liens avec les autres se fera par le biais des équivalence intra-ressource
                uri_1, uri_2 = rdflib.URIRef(self.ressource_uris["metanetx"][0] + metaNetX_ids[id_index]), rdflib.URIRef(self.ressource_uris[ressource][0] + ressource_ids[id_index])
                current_graph.add((uri_1, self.namespaces["skos"]['closeMatch'], uri_2))
            # On écrit le graph :
            ressource_version_MetaNetX.add_DataDump(g_name + ".trig")
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            n_triples += len(current_graph)
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
            # Si il y a plusieurs URI pour la ressource, il faut préparer les identifiants pour les correspondances intra-ressource
            if len(self.ressource_uris["metanetx"]) > 1:
                self.intra_ids_dict["metanetx"] = self.intra_ids_dict["metanetx"].union(metaNetX_ids)
            if len(self.ressource_uris[ressource]) > 1:
                self.intra_ids_dict[ressource] = self.intra_ids_dict[ressource].union(ressource_ids)
        # On crée les graph inter ressource à partir des infos de MetaNetX :
        print("Creating inter-ressource equivalences from MetaNetX: ")
        cbn_resource = itertools.combinations(selected_ressource, 2)
        for ressource_pair in cbn_resource:
            r1 = ressource_pair[0]
            r2 = ressource_pair[1]
            g_name = ("metanetx_" + r1 + "_" + r2)
            print("Treating : " + r1 + " - " + r2 + " with MetaNetX ...")
            current_graph = ressource_version_MetaNetX.create_data_graph(namespace_list  = ["skos"], namespace_dict = self.namespaces)
            # Le WevService semble mal fonctionner ... donc je suis passer par une nouvelle méthode où de download depuis le ftp :
            ids_r1, ids_r2 = self.get_mapping_from_MetanetX_inter_ressource(graph_metaNetX, self.uri_MetaNetX[r1], self.uri_MetaNetX[r2])
            if ids_r1 is None or ids_r2 is None:
                print("Impossible to process information for identifiers equivalence between ressource " + r1 + " and " + r2 + " with MetaNetX\n")
                continue
            n_ids = len(ids_r1)
            for id_index in range(n_ids):
                #  On écrit les équivalence inter-ressource seulement pour une URI de chaque ressource, le liens avec les autres se fera par le biais des équivalence intra-ressource
                uri_1, uri_2 = rdflib.URIRef(self.ressource_uris[r1][0] + ids_r1[id_index]), rdflib.URIRef(self.ressource_uris[r2][0] + ids_r2[id_index])
                current_graph.add((uri_1, self.namespaces["skos"]['closeMatch'], uri_2))
            # On écrit le graph :
            ressource_version_MetaNetX.add_DataDump(g_name + ".trig")
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            n_triples += len(current_graph)
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
            # Pas besoin de savoir s'il faut les ajouter dans l'intra-dict, car ils y ont nécéssairement été ajouté par le run MetaNetX .vs. ressource  
        ressource_version_MetaNetX.add_version_namespaces(["void"], self.namespaces)
        ressource_version_MetaNetX.add_version_attribute(DCTERMS["description"], rdflib.Literal("Ids correspondances between differents ressources from MetaNetX"))
        ressource_version_MetaNetX.add_version_attribute(DCTERMS["title"], rdflib.Literal("Ids correspondances from MetaNetX"))
        ressource_version_MetaNetX.add_version_attribute(self.namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
        ressource_version_MetaNetX.add_version_attribute(self.namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
        ressource_version_MetaNetX.version_graph.serialize(destination=path_out + "ressource_info_ids_equivalence_MetaNetX_" + ressource_version_MetaNetX.version + ".ttl", format = 'turtle')
    
    def create_graph_from_tab(self, tab_name, path_tab, path_out):
        """
        This function is used to create a graph or uri equivalences between different ressources. Equivalence information are fetch from the tabulated file.
        The tabulated file must a tabulated file with each column representing a ressource, column names must be the same as thoose in the config file. 
        Between ressource a skos:closeMatch relation is implemented (to avoid propaging false information)
        - path_tab: a path to the tabulated file
        - tab_name: the name of the tabulated to implement the ressource
        """ 
        ressource_version_Tab = Database_ressource_version(ressource = "ressources_id_mapping/" + tab_name, version = self.version)
        n_triples = 0
        subjects = set()
        file_content = list()
        path_out = path_out + ressource_version_Tab.version + "/"
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        # Extract associations
        with open(path_tab, "r") as tab_file:
            tab_reader = csv.reader(tab_file, delimiter='\t')
            header = next(tab_reader, None)
            for l in tab_reader:
                file_content.append(l)
        # Build graphs
        cbn_resource = itertools.combinations(header, 2)
        for ressource_pair in cbn_resource:
            r1, r2 = ressource_pair[0], ressource_pair[1]
            print("Treating " + r1 + " and " + r2)
            index_r1, index_r2 = header.index(r1), header.index(r2)
            g_name = (r1 + "_" + r2)
            current_graph = ressource_version_Tab.create_data_graph(namespace_list  = ["skos"], namespace_dict = self.namespaces)
            for id_eq in file_content:
                if (id_eq[index_r1] != '') and (id_eq[index_r2] != ''):
                    uri_1, uri_2 = rdflib.URIRef(self.ressource_uris[r1][0] + id_eq[index_r1]), rdflib.URIRef(self.ressource_uris[r2][0] + id_eq[index_r2])
                    current_graph.add((uri_1, self.namespaces["skos"]['closeMatch'], uri_2))
                    # Si il y a plusieurs URI pour la ressource, il faut préparer les identifiants pour les correspondances intra-ressource
                    if len(self.ressource_uris[r1]) > 1:
                        self.intra_ids_dict[r1].add(id_eq[index_r1])
                    if len(self.ressource_uris[r2]) > 1:
                        self.intra_ids_dict[r2].add(id_eq[index_r2])
            # On écrit le graph :
            ressource_version_Tab.add_DataDump(g_name + ".trig")
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            n_triples += len(current_graph)
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
        ressource_version_Tab.add_version_namespaces(["void"], self.namespaces)
        ressource_version_Tab.add_version_attribute(DCTERMS["description"], rdflib.Literal("Ids correspondances between differents ressources from tabulted file " + tab_name))
        ressource_version_Tab.add_version_attribute(DCTERMS["title"], rdflib.Literal("Ids correspondances from tabulted file " + tab_name))
        ressource_version_Tab.add_version_attribute(self.namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
        ressource_version_Tab.add_version_attribute(self.namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
        ressource_version_Tab.version_graph.serialize(destination=path_out + "ressource_info_ids_equivalence_Tab_" + tab_name + "_" + ressource_version_Tab.version + ".ttl", format = 'turtle')
