import requests
import json
import time
import rdflib
from rdflib.namespace import RDF


def classify_df(df_index, df, g_direct_parent, g_alternative_parent, path_direct_p, path_alternative_p):
    print("Treating df " + str(df_index))
    for index, row in df.iterrows():
        classif = get_entity_from_ClassyFire(row['CID'], row['INCHIKEY'])
        if not classif:
            continue
        add_triples(row['CID'], parse_entities(classif), g_direct_parent, g_alternative_parent)
    print("Serialyze graphs")
    g_direct_parent.serialize(destination=path_direct_p + "classyfire_direct_parent_" + str(df_index + 1) + ".trig", format='trig')
    g_alternative_parent.serialize(destination=path_alternative_p + "classyfire_alternative_parent_" + str(df_index + 1) + ".trig", format='trig')

def get_entity_from_ClassyFire(CID, InchiKey):
    """
    This function is used to send a query to  classyfire.wishartlab.com/entities/INCHIKEY.json to retrieve classiication result for a compound, given his InchiKey.
    This function return the classification is json format or False if there was an error. Logs and ids for which the request failed are reported in classyFire.log and classyFire_error_ids.log
    - CID: PubChem compound identifier (use for logs)
    - InchiKey: input inchikey
    """
    try:
        r = requests.get('http://classyfire.wishartlab.com/entities/%s.json' % (InchiKey),
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
    time.sleep(1)
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
    print(chemont_ids)
    print(CID)
    g_direct_parent.add((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID" + CID), RDF["type"], rdflib.URIRef("http://purl.obolibrary.org/obo/CHEMONTID_" + chemont_ids[0])))
    if len(chemont_ids) > 1:
        for alt_p in chemont_ids[1:]:
            g_alternative_parent.add((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID" + CID), RDF["type"], rdflib.URIRef("http://purl.obolibrary.org/obo/CHEMONTID_" + alt_p)))