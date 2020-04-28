import os
import rdflib
from rdflib.namespace import XSD, DCTERMS, OWL
from Database_ressource_version import Database_ressource_version
def create_annotation_graph_version(path_to_annot_graphs_dir, version, namespaces):
    """
    This function is used to create the ressource_info file associated to the version of the created annotation_graph.
    - path_to_annot_graphs_dir: A path to a directory containing all the associated annotation graph created using Virtuoso as .TriG file (Cf. README)
    - version: the version of the annotations graphs, MUST be the same as the one used in Virtuoso !
    """
    ressource_version = Database_ressource_version(ressource = "annotation_graph", version = version)
    n_triples = 0
    subjects = set()
    for annot_graph in os.listdir(path_to_annot_graphs_dir):
        if not annot_graph.endswith(".trig"):
            continue
        sub_g = rdflib.ConjunctiveGraph()
        sub_g.parse(path_to_annot_graphs_dir + annot_graph, format = 'trig')
        n_triples += len(sub_g)
        subjects = subjects.union(set([s for s in sub_g.subjects()]))
        ressource_version.add_DataDump(annot_graph)
    ressource_version.add_version_namespaces(["void"], namespaces)
    ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal("Annotation graphs contains additionnal annotation which can be usefull to explore the SBML file"))
    ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal("Annotation Graph"))
    ressource_version.add_version_attribute(namespaces["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
    ressource_version.add_version_attribute(namespaces["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
    ressource_version.version_graph.serialize(destination=path_to_annot_graphs_dir + "ressource_info_annotation_graph_" + ressource_version.version + ".ttl", format = 'turtle')