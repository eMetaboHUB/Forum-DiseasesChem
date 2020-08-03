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
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version


class Id_mapping:
    def __init__(self, version, namespaces):
        """
        - ressource_uris: a dict with key as ressource name and values representing different URIs that may be associated to the ressource
        - ressources_ids: a dict with key as ressource name and values representing the ressource id in UniChem
        - graph_original_uri_prefix: a dict with key as ressource name and values as the URI used in the SBML graph
        - intra_ids_dict: a dict with key as ressource name and values containing the union of all the ids extracted for this ressource
        - uri_MetaNetX: a dict with key as ressource name and values representing the URI of the ressource present in the MetaNetX RDF graph
        - uri_PubChem: a dict with key as ressource name and values representing the URI of the ressource present in the PubChem type RDF graph
        - sources:  a list of uris representing RDF graph which were used a sources in the process. All the list is exported in metadat when creating Intra-ressources equivalences. For specific Inter-ressource equivalences (Ex: MetaNetX or PubChem), only the associated source graph is exported
        - namespaces: a dict of namespaces
        - version: the version of the ressource, if None date is used
        """
        self.ressource_uris = dict()
        self.ressources_ids = dict()
        self.graph_original_uri_prefix = dict()
        self.intra_ids_dict = dict()
        self.uri_MetaNetX = dict()
        self.uri_PubChem = dict()
        self.sources = list()
        self.namespaces = namespaces
        self.version = version
    
    def get_graph_ids_set(self, path_to_graph, graph_uri):
        """
        This function allow to parse an input SMBL RDF graph and get all the actual ids present in the graph ONLY for ressources that may have several uris.
        - path_to_graph: a path to the .ttl file of the SMBL graph
        - graph_uri: the URI of the graph, used to provide sources
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
        # The URI of the source SBML is added to the sources list.
        self.sources.append(graph_uri)
    
    def export_intra_eq(self, path_out, source):
        """
        This function is used to create a graph or URIs equivalences between the different URIs associated to a given ressource. E
        Between differents URIs of the same ressource (called intra-uris) a owl:sameAs relation is implemented
        - path_out: a path to out files
        - source : a string which defined the origin of the data stores in the IdMapping object, et may be SBML, MetaNetX, BiGG ...
        """
        ressource_version_intra = Database_ressource_version(ressource = "ressources_id_mapping/Intra/" + source, version = self.version)
        n_triples = 0
        subjects = set()
        path_out = path_out + source + "/" + ressource_version_intra.version + "/"
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        for r_name in self.intra_ids_dict.keys():
            print("Treating " + r_name + ":")
            g_name = r_name + "_intra"
            current_graph = ressource_version_intra.create_data_graph(namespace_list  = ["owl"], namespace_dict = self.namespaces)
            intra_ids = list(self.intra_ids_dict[r_name])
            print("Create intra uris equivalences ...", end = '')
            for id in intra_ids:
                intra_uris = [rdflib.URIRef(prefix + id) for prefix in self.ressource_uris[r_name]]
                for current_uri, next_uri in zip(intra_uris, intra_uris[1:]):
                    current_graph.add((current_uri, self.namespaces["owl"]['sameAs'], next_uri))
            print("Ok\nExport graph for ressource " + r_name + " ...", end = '')
            ressource_version_intra.add_DataDump(g_name + ".trig")
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
            n_triples += len(current_graph)
            print("Ok")
        print("Write metadata graph ...", end = '')
        ressource_version_intra.add_version_namespaces(["void"], self.namespaces)
        ressource_version_intra.add_version_attribute(DCTERMS["description"], rdflib.Literal("URIs equivalence inside a ressource"))
        ressource_version_intra.add_version_attribute(DCTERMS["title"], rdflib.Literal("URIs equivalence inside a ressource"))
        for source_uris in self.sources:
            ressource_version_intra.add_version_attribute(DCTERMS["source"], rdflib.URIRef(source_uris))
        ressource_version_intra.add_version_attribute(self.namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
        ressource_version_intra.add_version_attribute(self.namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
        ressource_version_intra.version_graph.serialize(destination=path_out + "void.ttl", format = 'turtle')
        print("Ok")
    
    def import_table_infos(self, config_file):
        """
        This function is used to import the configuration file. The configuration file is a tabulated file with columns containing information of each ressource in this order:
        ressource name, ressource UniChem id, all ressource URIs (comma separated), URI used on SBML, URI used in MetaNetX, URI used in PubChem
        """
        with open(config_file, "r") as config:
            for l in config:
                columns = l.split("\t")
                self.ressources_ids[str(columns[0])] = str(columns[1])
                self.ressource_uris[str(columns[0])] = str(columns[2]).split(',')
                self.graph_original_uri_prefix[str(columns[0])] = str(columns[3])
                # Use rstrip because it's the last column
                self.uri_MetaNetX[str(columns[0])] = str(columns[4])
                self.uri_PubChem[str(columns[0])] = str(columns[5]).rstrip()
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
    
    def create_graph_from_MetaNetX(self, graph_metaNetX, path_out, graph_uri):
        """
        This function is used to create a graph or uri equivalences between MetaNetX identifiers and other ressources. Equivalence information are fetch from the MetaNetX RDF graph. 
        Between ressource a skos:closeMatch relation is implemented (to avoid propaging false information)
        - graph_metaNetX: a rdflib object graph associated to the MetaNetX RDF graph
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
            print("Get ids mapping ...", end = '')
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
            print("Ok\nExport graph for ressource " + ressource + " ...", end = '')
            ressource_version_MetaNetX.add_DataDump(g_name + ".trig")
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            n_triples += len(current_graph)
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
            print("Ok\n Add ids to intra equivalences table ...", end = '')
            # Si il y a plusieurs URI pour la ressource, il faut préparer les identifiants pour les correspondances intra-ressource
            if len(self.ressource_uris["metanetx"]) > 1:
                self.intra_ids_dict["metanetx"] = self.intra_ids_dict["metanetx"].union(metaNetX_ids)
            if len(self.ressource_uris[ressource]) > 1:
                self.intra_ids_dict[ressource] = self.intra_ids_dict[ressource].union(ressource_ids)
            print("Ok")
        self.sources.append(graph_uri)
        # On crée les graph inter ressource à partir des infos de MetaNetX :
        print("Creating inter-ressource equivalences from MetaNetX: ")
        cbn_resource = itertools.combinations(selected_ressource, 2)
        for ressource_pair in cbn_resource:
            r1 = ressource_pair[0]
            r2 = ressource_pair[1]
            g_name = ("metanetx_" + r1 + "_" + r2)
            print("Treating : " + r1 + " - " + r2 + " with MetaNetX :")
            print("Get ids mapping ...", end = '')
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
            print("Ok\nExport graph for ressource " + ressource + " ...", end = '')
            ressource_version_MetaNetX.add_DataDump(g_name + ".trig")
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            n_triples += len(current_graph)
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
            print("Ok")
            # Pas besoin de savoir s'il faut les ajouter dans l'intra-dict, car ils y ont nécéssairement été ajouté par le run MetaNetX .vs. ressource  
        print("Write metadata graph ...", end = '')
        ressource_version_MetaNetX.add_version_namespaces(["void"], self.namespaces)
        ressource_version_MetaNetX.add_version_attribute(DCTERMS["description"], rdflib.Literal("Ids correspondances between differents ressources from MetaNetX"))
        ressource_version_MetaNetX.add_version_attribute(DCTERMS["title"], rdflib.Literal("Ids correspondances from MetaNetX"))
        ressource_version_MetaNetX.add_version_attribute(DCTERMS["source"], rdflib.URIRef(graph_uri))
        ressource_version_MetaNetX.add_version_attribute(self.namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
        ressource_version_MetaNetX.add_version_attribute(self.namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
        ressource_version_MetaNetX.version_graph.serialize(destination=path_out + "void.ttl", format = 'turtle')
        print("Ok")
    
    def create_graph_from_pubchem_type(self, pubchem_graph, path_out, graph_uri):
        """
        This function is ised to create a mapping graph from information contains in type pubchem graphs which can contains links between PubChem CID and ChEBI
        - pubchem_graph: a rdflib object graph associated to the PubChem type RDF graph
        - path_out: path to the output directory
        """
        ressource_version_PubChem = Database_ressource_version(ressource = "ressources_id_mapping/PubChem", version = self.version)
        n_triples = 0
        subjects = set()
        path_out = path_out + ressource_version_PubChem.version + "/"
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        selected_ressource = [r for r in self.uri_PubChem.keys() if len(self.uri_PubChem[r]) > 0 and r != "pubchem"]
        uri_PubChem = self.uri_PubChem["pubchem"]
        for ressource in selected_ressource:
            request_uri = self.uri_PubChem[ressource]
            print("Treating ressource " + ressource + " :")
            g_name = ("PubChem_" + ressource)
            current_graph = ressource_version_PubChem.create_data_graph(namespace_list  = ["skos"], namespace_dict = self.namespaces)
            print("Get ids mapping ...", end = '')
            PubChem_ids, ressource_ids = self.get_pubchem_mapping(pubchem_graph, uri_PubChem, request_uri)
            if PubChem_ids is None or ressource_ids is None:
                print("Impossible to process information for identifiers equivalence between MetaNetX and " + ressource + "\n")
                continue
            n_ids = len(PubChem_ids)
            for id_index in range(n_ids):
                #  On écrit les équivalence inter-ressource seulement pour une URI de chaque ressource, le liens avec les autres se fera par le biais des équivalence intra-ressource
                uri_1, uri_2 = rdflib.URIRef(self.ressource_uris["pubchem"][0] + PubChem_ids[id_index]), rdflib.URIRef(self.ressource_uris[ressource][0] + ressource_ids[id_index])
                current_graph.add((uri_1, self.namespaces["skos"]['closeMatch'], uri_2))
            # On écrit le graph :
            ressource_version_PubChem.add_DataDump(g_name + ".trig")
            print("Ok\nExport graph for ressource " + ressource + " ...", end = '')
            current_graph.serialize(destination = path_out + g_name + ".trig", format='trig')
            n_triples += len(current_graph)
            subjects = subjects.union(set([s for s in current_graph.subjects()]))
            # Si il y a plusieurs URI pour la ressource, il faut préparer les identifiants pour les correspondances intra-ressource
            print("Ok\nAdd ids to intra equivalences table ...", end = '')
            if len(self.ressource_uris["pubchem"]) > 1:
                self.intra_ids_dict["pubchem"] = self.intra_ids_dict["pubchem"].union(PubChem_ids)
            if len(self.ressource_uris[ressource]) > 1:
                self.intra_ids_dict[ressource] = self.intra_ids_dict[ressource].union(ressource_ids)
            print("Ok")
        self.sources.append(graph_uri)
        print("Write metadata graph ...", end = '')
        ressource_version_PubChem.add_version_namespaces(["void"], self.namespaces)
        ressource_version_PubChem.add_version_attribute(DCTERMS["description"], rdflib.Literal("Ids correspondances between differents ressources from PubChem"))
        ressource_version_PubChem.add_version_attribute(DCTERMS["title"], rdflib.Literal("Ids correspondances from PubChem"))
        ressource_version_PubChem.add_version_attribute(DCTERMS["source"], rdflib.URIRef(graph_uri))
        ressource_version_PubChem.add_version_attribute(self.namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
        ressource_version_PubChem.add_version_attribute(self.namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
        ressource_version_PubChem.version_graph.serialize(destination=path_out + "void.ttl", format = 'turtle')
        print("Ok")
        
    def get_pubchem_mapping(self, pubchem_graph, uri_1, uri2):
        """
        This function is used to request the PubChem type graph.
        - pubchem_graph: a rdflib object graph associated to the PubChem type RDF graph
        - uri_1: the uri of the ressource 1 as indicated in the uri_PubChem attribute
        - uri_2: the uri of the ressource 2 as indicated in the uri_PubChem attribute
        """
        query = pubchem_graph.query(
        """    
        SELECT (strafter(STR(?cid),\"""" + uri_1 + """\") as ?uri_r1) (strafter(STR(?xref),\"""" + uri2 + """\") as ?uri_r2) 
        WHERE {
            ?cid rdf:type ?xref
            FILTER(STRSTARTS(str(?xref), \"""" + uri2 + """\"))
        }
        """)
        ids_ressource_1 = [id[0].toPython() for id in query]
        ids_ressource_2 = [id[1].toPython() for id in query]
        return ids_ressource_1, ids_ressource_2
        
