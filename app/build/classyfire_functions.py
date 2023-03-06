import requests
import json
import time
import rdflib
from rdflib.namespace import RDF, VOID, DCTERMS, XSD, RDFS
import sys
import subprocess
import signal
import glob
import datetime
import gzip
import csv
import os

# Prepare TimeoutExceptions
class TimeOutException(Exception):
   pass

def alarm_handler(signum, frame):
    raise TimeOutException()

def classify_df(df_index, df, g_direct_parent, g_alternative_parent, path_direct_p, path_alternative_p, path_out):
    """
    This function is used to retrieve all ChemOnt classes associated to each molecules in df. As these processes are run in parralel, size of each created graph need to be exported in this function. 
    This function return a table of 4 values: nb. triples in direct_parent graph file, nb. subjects in direct_parent graph file, nb. triples in Alternative_parent graph file, nb. subjects in Alternative_parent graph file  
    """
    print("Treating df " + str(df_index))
    for index, row in df.iterrows():
        classif = get_entity_from_ClassyFire(row['CID'], row['INCHIKEY'], path_out)
        if not classif:
            continue
        chemont_ids = parse_entities(row['CID'], classif, path_out)
        if not chemont_ids:
            continue
        add_triples(row['CID'], chemont_ids, g_direct_parent, g_alternative_parent)
    print("Serialyze graphs")
    g_direct_parent.serialize(destination = os.path.join(path_direct_p, "classyfire_direct_parent_" + str(df_index + 1) + ".ttl"), format='turtle')
    g_alternative_parent.serialize(destination = os.path.join(path_alternative_p, "classyfire_alternative_parent_" + str(df_index + 1) + ".ttl"), format='turtle')
    # Compress files:
    try:
        subprocess.run("gzip " + os.path.join(path_direct_p, "classyfire_direct_parent_" + str(df_index + 1) + ".ttl"), shell = True, check=True, stderr = subprocess.PIPE)
        subprocess.run("gzip " + os.path.join(path_alternative_p, "classyfire_alternative_parent_" + str(df_index + 1) + ".ttl"), shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error while trying to compress files")
        print(e)
        sys.exit(3)
    return [len(g_direct_parent), len(set([str(s) for s in g_direct_parent.subjects()])), len(g_alternative_parent), len(set([str(s) for s in g_alternative_parent.subjects()]))]

def get_entity_from_ClassyFire(CID, InchiKey, path_out):
    """
    This function is used to send a query to  classyfire.wishartlab.com/entities/INCHIKEY.json to retrieve classiication result for a compound, given his InchiKey.
    This function return the classification is json format or False if there was an error. Logs and ids for which the request failed are reported in classyFire.log and classyFire_error_ids.log
    - CID: PubChem compound identifier (use for logs)
    - InchiKey: input inchikey
    """
    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(60)
    time.sleep(1)
    try:
        r = requests.get('http://classyfire.wishartlab.com/entities/%s.json' % (InchiKey), headers = {"Content-Type": "application/json"})
        r.raise_for_status()
    # Check timeout: 
    except TimeOutException:
        print("Request timeout was reached (60s)!")
        with open(os.path.join(path_out, "classyFire.log"), "a") as f_log:
            f_log.write("CID " + CID + " - Request Timeout")
        with open(os.path.join(path_out, "classyFire_error_ids.log"), "a") as id_log:
                id_log.write(CID + "\n")
        signal.alarm(0)
        return False
    # Check if there was an error while sending request: 
    except requests.exceptions.RequestException as e:
        print("Error while trying to retrieve classication for CID: " + CID + ", Check logs.")
        with open(os.path.join(path_out, "classyFire.log"), "a") as f_log:
                f_log.write("CID " + CID + " - HTTP response status codes: ")
                f_log.write(str(e) + "\n")
        with open(os.path.join(path_out, "classyFire_error_ids.log"), "a") as id_log:
                id_log.write(CID + "\n")
        signal.alarm(0)
        return False
    # Test if the element is classified
    classif = json.loads(r.text)
    if len(classif) == 0:
        with open(os.path.join(path_out, "ids_no_classify.log"), "a") as no_classif_log:
                no_classif_log.write(CID + "\t" + InchiKey + "\n")
        signal.alarm(0)
        return False
    signal.alarm(0)
    return classif

def parse_entities(CID, classif, path_out):
    """
    This function is used to parse a response from ClassyFire and extract direct parents and alternative parents
    This function return a list of CHEMONTID associated to the classification result. The first is always the direct_parent and remaining are alternative parents
    - response: The response of the request
    """
    try:
        chemont_ids = [classif["direct_parent"]['chemont_id'].split(':')[1]] + [alt_p['chemont_id'].split(':')[1] for alt_p in classif["alternative_parents"]]
    except:
        print("Error while trying to parse response for CID: " + CID + ", Check logs.")
        with open(os.path.join(path_out, "classyFire.log"), "a") as f_log:
            f_log.write("CID " + CID + " - Error while parsing response: ")
            e = sys.exc_info()[0]
            f_log.write(str(e) + "\n")
        with open(os.path.join(path_out, "classyFire_error_ids.log"), "a") as id_log:
            id_log.write(CID + "\n")
        return False
    return(chemont_ids)

def add_triples(CID, chemont_ids, g_direct_parent, g_alternative_parent):
    """
    This function is used to create triples from ChemOnt classification. Direct-parent class is exported in direct-parent graph and, separately alternative classes are exported in alternative-classes graph. 
    """
    g_direct_parent.add((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID" + CID), RDF["type"], rdflib.URIRef("http://purl.obolibrary.org/obo/CHEMONTID_" + chemont_ids[0])))
    if len(chemont_ids) > 1:
        for alt_p in chemont_ids[1:]:
            g_alternative_parent.add((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID" + CID), RDF["type"], rdflib.URIRef("http://purl.obolibrary.org/obo/CHEMONTID_" + alt_p)))


def extract_CID_InchiKey(pmids_cids_graph_list, inchikeys_graph_list,  path_out):
    # Inti output file
    with open(path_out, "w") as out:
        out_writer = csv.writer(out, delimiter = ',')
        m = out_writer.writerow(['CID', 'INCHIKEY'])
    # Init variables
    available_cids = set()
    for pmid_cid_f_input in pmids_cids_graph_list:
        # release memory
        g_pmid_cid = None
        # Import pmid_cid graph
        print("Importing " + pmid_cid_f_input + " ...", end = '')
        g_pmid_cid = rdflib.ConjunctiveGraph()
        with gzip.open(pmid_cid_f_input, "rb") as f:
            g_pmid_cid.parse(f, format = "turtle")
        # Get all objects
        extracted_objects = [uri.toPython().split('http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID')[1] for uri in list(g_pmid_cid.objects())]
        available_cids = available_cids.union(extracted_objects)
        print(" Ok")
    # Then, we browse inchikey files to select CID - inchikey association for which the CID has an associated corpus
    for inchikey_f_input in inchikeys_graph_list:
        g_inchikey = None
        g_inchikey = rdflib.Graph()
        print("treating file " + inchikey_f_input + " ...", end = '')
        # Add InchiKeys triples to the graph
        with gzip.open(inchikey_f_input, "rb") as f:
            g_inchikey.parse(f, format = "turtle")
        # Get cid - inchikey associations
        cids_inchikeys = list(g_inchikey.subject_objects(rdflib.URIRef("http://semanticscience.org/resource/SIO_000011")))
        inchikeys = [cid_inchikey[0].toPython().split("http://rdf.ncbi.nlm.nih.gov/pubchem/inchikey/")[1] for cid_inchikey in cids_inchikeys]
        cids = [cid_inchikey[1].toPython().split("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID")[1] for cid_inchikey in cids_inchikeys]
        with open(path_out, "a") as out:
            out_writer = csv.writer(out, delimiter = ',')
            for cid_index in range(0, len(cids)):
                if cids[cid_index] in available_cids:
                    m = out_writer.writerow([cids[cid_index], inchikeys[cid_index]])
        print(" Ok")
    # Release all memory
    g_inchikey = None
    g_pmid_cid = None
    print("End procedure CID - InchiKeys associations !")


def get_CID_InchiKeys(url, graph_from, out_file):
    return None

def ask_for_graph(url, graph_uri):
    """
    This function is used to test if graph a exist without erase
    - url: Virtuoso SPARQL endpoint url
    - graph_uri: the graph uri to be tested
    """
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html"
    }
    data = {
        "format": "html",
        "query": "ASK WHERE { GRAPH <" + graph_uri + "> { ?s ?p ?o } }"
    }
    r = requests.post(url = url, headers = header, data = data)
    if r.status_code != 200:
        print("Error in request while trying to check if graph " + graph_uri + " exists.\nImpossible to continue, exit.\n")
        print(r.text)
        sys.exit(3)
    if r.text == "true":
        return True
    return False

def export_ressource_metadata(ClassyFire_direct_p, ClassyFire_alternative_p, graph_sizes, uri_targeted_ressources, path_direct_p, path_alternative_p):
    """
    This function is used export metadata for builted graphs
    """
    ClassyFire_direct_p.add_version_attribute(RDF["type"], VOID["Linkset"])
    ClassyFire_direct_p.add_version_attribute(DCTERMS["source"], rdflib.URIRef("http://classyfire.wishartlab.com"))
    ClassyFire_direct_p.add_version_attribute(RDFS["seeAlso"], rdflib.URIRef("https://doi.org/10.1186/s13321-016-0174-y"))
    
    ClassyFire_alternative_p.add_version_attribute(RDF["type"], VOID["Linkset"])
    ClassyFire_alternative_p.add_version_attribute(DCTERMS["source"], rdflib.URIRef("http://classyfire.wishartlab.com"))
    ClassyFire_alternative_p.add_version_attribute(RDFS["seeAlso"], rdflib.URIRef("https://doi.org/10.1186/s13321-016-0174-y"))
    
    for uri_targeted_ressource in uri_targeted_ressources:
        ClassyFire_direct_p.add_version_attribute(VOID["target"], uri_targeted_ressource)
        ClassyFire_alternative_p.add_version_attribute(VOID["target"], uri_targeted_ressource)
    ClassyFire_direct_p.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providing links between PubChem compounds and their class according to ChemOnt ontology from ClassyFire. The provided class correspond to the Direct Parent, representing the dominant class in the molecule"))
    ClassyFire_direct_p.add_version_attribute(DCTERMS["title"], rdflib.Literal("ChemOnt Classification - Direct parent"))
    # On ajoute les infos pour la seconde ressource, les endpoint:
    ClassyFire_alternative_p.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providing links between PubChem compounds and their classes according to ChemOnt ontology from ClassyFire. The provided classes correspond to the Alternative Parents, representing classes describing the molecule but which not have an ancestor–descendant relationship with each other or with the Direct Parent"))
    ClassyFire_alternative_p.add_version_attribute(DCTERMS["title"], rdflib.Literal("ChemOnt Classification - Alternative parents"))
    # On exporte le graph des metadata :
    print("Export version graph with metadata ... ", end = '')
    ClassyFire_direct_p.add_version_attribute(VOID["triples"], rdflib.Literal(sum([g[0] for g in graph_sizes]), datatype=XSD.long))
    ClassyFire_direct_p.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(sum([g[1] for g in graph_sizes]), datatype=XSD.long ))
    ClassyFire_alternative_p.add_version_attribute(VOID["triples"], rdflib.Literal(sum([g[2] for g in graph_sizes]), datatype=XSD.long ))
    ClassyFire_alternative_p.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(sum([g[3] for g in graph_sizes]), datatype=XSD.long ))
    ClassyFire_direct_p.version_graph.serialize(destination = os.path.join(path_direct_p, "void.ttl"), format='turtle')
    ClassyFire_alternative_p.version_graph.serialize(destination = os.path.join(path_alternative_p, "void.ttl"), format='turtle')
    print("Ok")
