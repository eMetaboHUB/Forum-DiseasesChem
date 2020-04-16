import rdflib

def merge_SMBL_and_annot_graphs(path_to_SMBL_RDF, list_annot_graph, path_to_annot_graph):
    """
    This function is used to build a conjuctive graph with rdflib, merging triples from the original SBML graph and triples from annotations graphs
    - path_to_SMBL_RDF: a path to the SMBL graph (.ttl)
    - a list of annotation graph files that have to be loaded
    - a path to the directory containing annotation graphs
    """
    sbml = rdflib.ConjunctiveGraph()
    sbml.parse(path_to_SMBL_RDF, format='turtle')
    for annot_graph in list_annot_graph:
        sbml.parse(path_to_annot_graph + annot_graph, format='trig')
    return(sbml)

def extract_ids_from_SMBL_by_URI_prefix(smbl_graph, uri_prefix):
    """
    This function is used to request a sbml graph in sparl to extract all identifiers that match a prefix URI.
    - the sbml_graph, a rdflib.Graph object
    - uri_prefix: the URI prefix
    """
    # On va chercher tout les id avec une requête sparql qui correspondent à ce prefix :
    query = smbl_graph.query(
        """
        select distinct (strafter(STR(?ref),\"""" + uri_prefix + """\") as ?id)
        where {
            ?species a SBMLrdf:Species .
            ?species bqbiol:is ?ref .
            FILTER(STRSTARTS(STR(?ref), \"""" + uri_prefix + """\"))
            }
        """)
    # On récupère et formate correctement la liste d'ids
    id_list = [id[0].toPython() for id in query]
    return(id_list)