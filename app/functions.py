import rdflib

def create_empty_graph(namespace_list, namespaces_dict):
    g = rdflib.Graph()
    for ns_name in namespace_list:
        g.bind(ns_name, namespaces_dict[ns_name])
    return g