import rdflib
import requests
import io
import re
from rdflib.namespace import XSD, DCTERMS, OWL
import os
import json
import gzip
import itertools
from Database_ressource_version import Database_ressource_version


class Id_mapping:
    def __init__(self, version, namespaces):
        self.ressource_uris = dict()
        self.ressources_ids = dict()
        self.graph_original_uri_prefix = dict()
        self.intra_ids_dict = dict()
        self.uri_MetaNetX = dict()
        self.g_metaNetX = None
        self.namespaces = namespaces
        self.version = version
    
    def download_mapping_from_ftp(self, ressource_1, ressource_2, path_out):
        """
        This function is used to dowload the ressource mapping file from the ftp server
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
        - ressource_uris: a dict containing all the possible ressources uris that may be used. It will be used to choose for which ressource, ids should be extracted to compute intra-uris equivalence.
        Note that keys in the dict must be the same as in the graph_original_uri_prefix dict.
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
        This function is used to create a graph or uri equivalences between different input ressource. Equivalence information are fetch for the WebService of UniChem. 
        Between ressource a skos:closeMatch relation is implemented (to avoid propaging false information)
        Between differents uris of the same ressource (called intra-uris) a skos:exactMatch relation is implemented
        - ressources_ids: a dict containing ressource name as key and ressource id in the UniChem database as values
        - ressource_uris: a dict containing all the possible ressources uris associated to a ressource.
        Note that keys in the dict must be the same as in the graph_original_uri_prefix dict.
        - namespaces: a dict of namespaces
        - path_out: a path to out files
        - version: a version name. if None date is used by default.
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
                all_uris = [rdflib.URIRef(self.ressource_uris[r1][0] + ids_r1[id_index])] + [rdflib.URIRef(self.ressource_uris[r2][0] + ids_r2[id_index])]
                for current_uri, next_uri in zip(all_uris, all_uris[1:]):
                    current_graph.add((current_uri, self.namespaces["skos"]['closeMatch'], next_uri))
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
        ressource_version_UniChem.version_graph.serialize(destination=path_out + "ressource_info_ids_equivalence_UniChem" + ressource_version_UniChem.version + ".ttl", format = 'turtle')
    
    def export_intra_eq(self, path_out):
        ressource_version_intra = Database_ressource_version(ressource = "ressources_id_mapping/Intra", version = self.version)
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
    
    def import_config(self, config_file):
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
        requested_uri = self.uri_MetaNetX[ressource]
        metaNetX_prefix = "https://rdf.metanetx.org/chem/"
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
    
    def create_graph_from_MetaNetX(self, graph_metaNetX, path_out):
        ressource_version_MetaNetX = Database_ressource_version(ressource = "ressources_id_mapping/MetaNetX", version = self.version)
        n_triples = 0
        subjects = set()
        path_out = path_out + ressource_version_MetaNetX.version + "/"
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        selected_ressource = [r for r in self.uri_MetaNetX.keys() if len(self.uri_MetaNetX[r]) > 0]
        for ressource in selected_ressource:
            print("Treating ressource: " + ressource + " ...")
            g_name = ("MetaNetX_" + ressource)
            current_graph = ressource_version_MetaNetX.create_data_graph(namespace_list  = ["skos"], namespace_dict = self.namespaces)
            metaNetX_ids, ressource_ids = self.get_mapping_from_MetanetX(graph_metaNetX, ressource)
            if metaNetX_ids is None or ressource_ids is None:
                print("Impossible to process information for identifiers equivalence between MetaNetX and " + ressource + "\n")
                continue
            n_ids = len(metaNetX_ids)
            for id_index in range(n_ids):
                #  On écrit les équivalence inter-ressource seulement pour une URI de chaque ressource, le liens avec les autres se fera par le biais des équivalence intra-ressource
                all_uris = [rdflib.URIRef(self.ressource_uris["metanetx"][0] + metaNetX_ids[id_index])] + [rdflib.URIRef(self.ressource_uris[ressource][0] + ressource_ids[id_index])]
                for current_uri, next_uri in zip(all_uris, all_uris[1:]):
                    current_graph.add((current_uri, self.namespaces["skos"]['closeMatch'], next_uri))
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
            # On annote le graph :
        ressource_version_MetaNetX.add_version_namespaces(["void"], self.namespaces)
        ressource_version_MetaNetX.add_version_attribute(DCTERMS["description"], rdflib.Literal("Ids correspondances between differents ressources from MetaNetX"))
        ressource_version_MetaNetX.add_version_attribute(DCTERMS["title"], rdflib.Literal("Ids correspondances from MetaNetX"))
        ressource_version_MetaNetX.add_version_attribute(self.namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
        ressource_version_MetaNetX.add_version_attribute(self.namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
        ressource_version_MetaNetX.version_graph.serialize(destination=path_out + "ressource_info_ids_equivalence_MetaNetX" + ressource_version_MetaNetX.version + ".ttl", format = 'turtle')