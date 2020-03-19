import rdflib
from datetime import date
from rdflib import XSD

def create_empty_graph(namespace_list, namespaces_dict):
    g = rdflib.Graph()
    for ns_name in namespace_list:
        g.bind(ns_name, namespaces_dict[ns_name])
    return g

def create_ressource_from_graph(graph, ressource, annotation_dict):
    # Create associated ressource version
    ressource_graph = rdflib.Graph()
    ressource_graph.bind("dcterms", rdflib.Namespace("http://purl.org/dc/terms/"))
    today = date.today().strftime("%y-%m-%d")
    uri_ressource = rdflib.URIRef("http://database/ressources/" + ressource)
    uri_graph = rdflib.URIRef("http://database/ressources/" + ressource + "/" + today)
    # add the graph as a new version of the ressource
    ressource_graph.add((uri_ressource, rdflib.URIRef("http://purl.org/dc/terms/hasVersion"), uri_graph))
    ressource_graph.add((uri_graph, rdflib.URIRef("http://purl.org/dc/terms/created"), rdflib.Literal(today,datatype=XSD.date)))