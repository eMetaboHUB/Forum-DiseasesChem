import rdflib
import sys
import re
from datetime import date
from rdflib.namespace import XSD, DCTERMS

class Database_ressource_version:
    """This class represent a ressource in the database represented in a RDF model. it can be divided in two main parts:
    - a dict of data graph containing triples associated to the data of the ressource
    - a graph which describe the version of the ressource being build
    """
    def __init__(self, ressource, version_date):
        self.ressource = ressource
        self.version_date = version_date
        self.uri_version = None
        self.data_graph_dict = dict()
        self.version_graph = self.initialyze_version()
    
    def initialyze_version(self):
        g_v = rdflib.Graph()
        g_v.bind("dcterms", rdflib.Namespace("http://purl.org/dc/terms/"))
        # On crée l'URI de la version
        self.uri_version = rdflib.URIRef("http://database/ressources/" + self.ressource + "/" + self.version_date)
        g_v.add((rdflib.URIRef("http://database/ressources/" + self.ressource), DCTERMS['hasVersion'], self.uri_version))
        g_v.add((self.uri_version, DCTERMS["created"], rdflib.Literal(self.version_date, datatype=XSD.date)))
        return g_v
    
    def append_data_graph(self, file, namespace_list, namespace_dist):
        base_name = re.split("\.", file)[0]
        # On crée le graph avec l'URI et les namespaces associés
        g_d = rdflib.Graph(identifier=rdflib.URIRef("http://database/ressources/" + self.ressource + "/" + self.version_date + "/" + base_name))
        for ns_name in namespace_list:
            g_d.bind(ns_name, namespace_dist[ns_name])
        
        self.version_graph.add((g_d.identifier, DCTERMS['isPartOf'], self.uri_version))
        self.version_graph.add((g_d.identifier, DCTERMS['source'], rdflib.Literal(file)))
        # Add graph data to dict
        self.data_graph_dict[base_name] = g_d
    
    def add_version_attribute(self, predicate, object):
        # Add property
        self.version_graph.add((self.uri_version, predicate, object))
        
    def add_version_namespaces(self, namespace_list, namespace_dist):
        # Test if namespace is aleady added
        for namespace in namespace_list:
            if namespace not in [ns[0] for ns in self.version_graph.namespace_manager.namespaces()]:
                self.version_graph.bind(namespace, namespace_dist[namespace])
