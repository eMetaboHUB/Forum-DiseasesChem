import rdflib
import sys
import re
from datetime import date
from rdflib.namespace import XSD, DCTERMS, RDF, VOID

class Database_ressource_version:
    """This class represent a version of a resource in the Knowledge graph. It is composed of:
    - ressource: the name of the resource for which a new version will be created
    - version: the version
    - uri_version: the URI of this version
    - version_graph: the metadata graph containing information about the created version
    """
    def __init__(self, ressource, version):
        self.ressource = ressource
        self.version = version
        self.uri_version = None
        self.version_graph = self.initialyze_version()
    
    def initialyze_version(self):
        """
        This function is used to initialyse the version graph by creating the associated elements like URI, etc ...
        """
        g_v = rdflib.Graph()
        g_v.bind("dcterms", rdflib.Namespace("http://purl.org/dc/terms/"))
        g_v.bind("void", rdflib.Namespace("http://rdfs.org/ns/void#"))
        # Si une version a été donnée on l'utilise sinon par défault on met la date:
        if not self.version:
            self.version = date.today().isoformat()
        # On crée l'URI de la version
        self.uri_version = rdflib.URIRef("https://forum.semantic-metabolomics.org/" + self.ressource + "/" + self.version)
        g_v.add((rdflib.URIRef("https://forum.semantic-metabolomics.org/" + self.ressource), DCTERMS['hasVersion'], self.uri_version))
        g_v.add((self.uri_version, DCTERMS["created"], rdflib.Literal(date.today().isoformat(), datatype=XSD.date)))
        return g_v
    
    def create_data_graph(self, namespace_list, namespace_dict):
        """
        This function is used to create a new data graph for the ressource version. A data-graph is a graph containing triples associated to the ressource
        - namespace_list: a list of the namespaces that should be associated to the graph
        - namespace_dict: a dict containing all the used namespaces.
        """
        # On crée le graph avec l'URI et les namespaces associés
        g_d = rdflib.Graph(identifier=self.uri_version)
        for ns_name in namespace_list:
            g_d.bind(ns_name, namespace_dict[ns_name])
        return g_d
    
    def add_version_attribute(self, predicate, object):
        """
        The function is used to add a new triple to the version graph, Subject of this triple will be the URI the resource version.
        - predicate: a rdfli.URIRef representing the predicate of the triple
        - object: a rdfli.URIRef representing the object of the triple
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
    
    def add_DataDump(self, graph_file, ftp):
        """
        This function will create an attribute void:dataDump to indicate the location of data file(s) on the provided ftp server.
        - graph_file: the graph file name
        - ftp: The ftp server address on which created data will be stored. A valid adress is not mandatory as data will not be automatically upload to the ftp server.
        If an empty string is used, dataDump triples will not be added to the void.ttl
        """
        if len(ftp) > 0:
            self.version_graph.add((self.uri_version, VOID["dataDump"], rdflib.URIRef(ftp + self.ressource + "/" + self.version + "/" + graph_file)))