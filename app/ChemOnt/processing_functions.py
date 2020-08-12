import requests
import json
import time
import rdflib
from rdflib.namespace import RDF, VOID, DCTERMS, XSD


def classify_df(df_index, df, g_direct_parent, g_alternative_parent, path_direct_p, path_alternative_p):
    """
    This function is used to retrieve all ChemOnt classes associated to each molecules in df. As these processes are run in parralel, size of each created graph need to be exported in this function. 
    This function return a table of 4 values: nb. triples in direct_parent graph file, nb. subjects in direct_parent graph file, nb. triples in Alternative_parent graph file, nb. subjects in Alternative_parent graph file  
    """
    print("Treating df " + str(df_index))
    for index, row in df.iterrows():
        classif = get_entity_from_ClassyFire(row['CID'], row['INCHIKEY'])
        if not classif:
            continue
        add_triples(row['CID'], parse_entities(classif), g_direct_parent, g_alternative_parent)
    print("Serialyze graphs")
    g_direct_parent.serialize(destination=path_direct_p + "classyfire_direct_parent_" + str(df_index + 1) + ".trig", format='trig')
    g_alternative_parent.serialize(destination=path_alternative_p + "classyfire_alternative_parent_" + str(df_index + 1) + ".trig", format='trig')
    return [len(g_direct_parent), len(set([str(s) for s in g_direct_parent.subjects()])), len(g_alternative_parent), len(set([str(s) for s in g_alternative_parent.subjects()]))]

def get_entity_from_ClassyFire(CID, InchiKey):
    """
    This function is used to send a query to  classyfire.wishartlab.com/entities/INCHIKEY.json to retrieve classiication result for a compound, given his InchiKey.
    This function return the classification is json format or False if there was an error. Logs and ids for which the request failed are reported in classyFire.log and classyFire_error_ids.log
    - CID: PubChem compound identifier (use for logs)
    - InchiKey: input inchikey
    """
    try:
        r = requests.get('https://gnps-classyfire.ucsd.edu/entities/%s.json' % (InchiKey),
                     headers={
                         "Content-Type": "application/json"})
        r.raise_for_status()
    # Check if there was an error while sending request: 
    except requests.exceptions.RequestException as e:
        print("Error while trying to retrieve classication for CID: " + CID + ", Check logs.")
        with open("classyFire.log", "a") as f_log:
                f_log.write("CID " + CID + " - HTTP response status codes: ")
                f_log.write(str(e) + "\n")
        with open("classyFire_error_ids.log", "a") as id_log:
                id_log.write(CID + "\n")
        return False
    # Test if the element is classified
    classif = json.loads(r.text)
    if len(classif) == 0:
        with open("ids_no_classify.log", "a") as no_classif_log:
                no_classif_log.write(CID + "\t" + InchiKey + "\n")
        return False
    # time.sleep(1)
    return classif

def parse_entities(classif):
    """
    This function is used to parse a response from ClassyFire and extract direct parents and alternative parents
    This function return a list of CHEMONTID associated to the classification result. The first is always the direct_parent and remaining are alternative parents
    - response: The response of the request
    """
    chemont_ids = [classif["direct_parent"]['chemont_id'].split(':')[1]] + [alt_p['chemont_id'].split(':')[1] for alt_p in classif["alternative_parents"]]
    return(chemont_ids)

def add_triples(CID, chemont_ids, g_direct_parent, g_alternative_parent):
    """
    This function is used to create triples from ChemOnt classification. Direct-parent class is exported in direct-parent graph and, separately alternative classes are exported in alternative-classes graph. 
    """
    g_direct_parent.add((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID" + CID), RDF["type"], rdflib.URIRef("http://purl.obolibrary.org/obo/CHEMONTID_" + chemont_ids[0])))
    if len(chemont_ids) > 1:
        for alt_p in chemont_ids[1:]:
            g_alternative_parent.add((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID" + CID), RDF["type"], rdflib.URIRef("http://purl.obolibrary.org/obo/CHEMONTID_" + alt_p)))

def export_ressource_metatdata(ClassyFire_direct_p, ClassyFire_alternative_p, graph_sizes, uri_targeted_ressources, path_direct_p, path_alternative_p):
    """
    This function is used export metadata for builted graphs
    """
    # On ajoute les infos pour la première ressource:
    for i in range(1, (len(graph_sizes) + 1)):
        ClassyFire_direct_p.add_DataDump("classyfire_direct_parent_" + str(i) + ".trig")
        ClassyFire_alternative_p.add_DataDump("classyfire_alternative_parent_" + str(i) + ".trig")
    ClassyFire_direct_p.add_version_attribute(RDF["type"], VOID["Linkset"])
    ClassyFire_alternative_p.add_version_attribute(RDF["type"], VOID["Linkset"])
    for uri_targeted_ressource in uri_targeted_ressources:
        ClassyFire_direct_p.add_version_attribute(VOID["target"], uri_targeted_ressource)
        ClassyFire_alternative_p.add_version_attribute(VOID["target"], uri_targeted_ressource)
    ClassyFire_direct_p.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providing links between PubChem compounds and their class according to ChemOnt ontology from ClassyFire. The provided class correspond to the \"Direct Parent\", representing the dominant class in the molecule"))
    ClassyFire_direct_p.add_version_attribute(DCTERMS["title"], rdflib.Literal("ChemOnt Classification - Direct parent"))
    # On ajoute les infos pour la seconde ressource, les endpoint:
    ClassyFire_alternative_p.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providing links between PubChem compounds and their classes according to ChemOnt ontology from ClassyFire. The provided classes correspond to the \"Alternative Parents\", representing classes describing the molecule but which not have an ancestor–descendant relationship with each other or with the Direct Parent"))
    ClassyFire_alternative_p.add_version_attribute(DCTERMS["title"], rdflib.Literal("ChemOnt Classification - Alternative parents"))
    # On exporte le graph des metadata :
    print(" Export version graph with metadata ...\n", end = '')
    ClassyFire_direct_p.add_version_attribute(VOID["triples"], rdflib.Literal(sum([g[0] for g in graph_sizes]), datatype=XSD.long))
    ClassyFire_direct_p.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(sum([g[1] for g in graph_sizes]), datatype=XSD.long ))
    ClassyFire_alternative_p.add_version_attribute(VOID["triples"], rdflib.Literal(sum([g[2] for g in graph_sizes]), datatype=XSD.long ))
    ClassyFire_alternative_p.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(sum([g[3] for g in graph_sizes]), datatype=XSD.long ))
    ClassyFire_direct_p.version_graph.serialize(destination= path_direct_p + "void.ttl", format='turtle')
    ClassyFire_alternative_p.version_graph.serialize(destination= path_alternative_p + "void.ttl", format='turtle')