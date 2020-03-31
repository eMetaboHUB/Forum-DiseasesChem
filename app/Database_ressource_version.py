import rdflib
import sys
import re
from datetime import date
from rdflib.namespace import XSD, DCTERMS, RDF

class Database_ressource_version:
    """This class represent a ressource version in the database, represented in a RDF model. It is composed of:
    - ressource: the name of the ressource for which a new version will be created
    - uri_version: the new URI of the new version, created by the object it-self
    - data_graph_dict: a dict containing all the graph associated to the ressource version. Keys are filenames and values are the rdflib.Graph() associated to.
    - version_graph: the graph containing information about the created version
    """
    def __init__(self, ressource, version):
        self.ressource = ressource
        self.version = version
        self.uri_version = None
        self.data_graph_dict = dict()
        self.version_graph = self.initialyze_version()
    
    def initialyze_version(self):
        """
        This function is used to initialyse the version graph by creating the associated elements like URI, etc ...
        """
        g_v = rdflib.Graph()
        g_v.bind("dcterms", rdflib.Namespace("http://purl.org/dc/terms/"))
        # Si une version a été donnée on l'utilise sinon par défault on met la date:
        if not self.version:
            self.version = date.today().isoformat()
        # On crée l'URI de la version
        self.uri_version = rdflib.URIRef("http://database/ressources/" + self.ressource + "/" + self.version)
        g_v.add((rdflib.URIRef("http://database/ressources/" + self.ressource), DCTERMS['hasVersion'], self.uri_version))
        g_v.add((self.uri_version, DCTERMS["created"], rdflib.Literal(self.version, datatype=XSD.date)))
        # On indique qu'il s'agit d'une nouveau dataset:
        g_v.add((self.uri_version, RDF["type"], rdflib.URIRef("http://rdfs.org/ns/void#Dataset")))
        return g_v
    
    def append_data_graph(self, file, namespace_list, namespace_dict):
        """
        This function is used to append a new data graph to the ressource version. A data-graph is a graph containing triples associated to the ressource
        - file: a file named that will be used as a Key to refer the graph in data_graph_dict, and which will be used as dc:source object.
        - namespace_list: a list of the namespaces that should be associated to the graph
        - namespace_dict: a dict containing all the used namespaces.
        """
        base_name = re.split("\.", file)[0]
        # On crée le graph avec l'URI et les namespaces associés
        g_d = rdflib.Graph(identifier=rdflib.URIRef("http://database/ressources/" + self.ressource + "/" + self.version + "/" + base_name))
        # On ajoute un namespace correspondante à la version et à la ressource que l'on traite :
        g_d.bind(self.ressource + "_" + self.version, rdflib.Namespace("http://database/ressources/" + self.ressource + "/" + self.version + "/"))
        for ns_name in namespace_list:
            g_d.bind(ns_name, namespace_dict[ns_name])
        
        self.version_graph.add((g_d.identifier, DCTERMS['isPartOf'], self.uri_version))
        self.version_graph.add((g_d.identifier, DCTERMS['source'], rdflib.Literal(file)))
        # Add graph data to dict
        self.data_graph_dict[base_name] = g_d
    
    def add_version_attribute(self, predicate, object):
        """
        The function is used to add a new triples to the version graph Subject of the triple will be the URI of the version-graph.
        - predicate: a rdfli.URIRef representing the predicate of the triple
        - a rdfli.URIRef representing the object of the triple
        """
        # Add property
        self.version_graph.add((self.uri_version, predicate, object))
        
    def add_version_namespaces(self, namespace_list, namespace_dict):
        """
        This function is used to add namespaces to the version graph
        - namespace_list: a list of the namespaces that should be associated to the graph
        - namespace_dict: a dict containing all the used namespaces.
        """
        # Test if namespace is aleady added
        for namespace in namespace_list:
            if namespace not in [ns[0] for ns in self.version_graph.namespace_manager.namespaces()]:
                self.version_graph.bind(namespace, namespace_dict[namespace])
