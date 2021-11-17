import argparse, configparser, os, glob, sys, json, rdflib, gzip, subprocess
import pandas as pd
import numpy as np
import multiprocessing as mp
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version
from download_functions import check_void
from classyfire_functions import *

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--log", help="path to log and additional files directory")
args = parser.parse_args()


if not os.path.exists(args.config):
    print("Config file : " + args.config + " does not exist")
    sys.exit(3)

try:    
    config = configparser.ConfigParser()
    config.read(args.config)
except configparser.Error as e:
    print(e)
    sys.exit(3)

# Import namespaces
namespaces = {
    "cito": rdflib.Namespace("http://purl.org/spar/cito/"),
    "compound": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"),
    "reference": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/reference/"),
    "endpoint":	rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/"),
    "obo": rdflib.Namespace("http://purl.obolibrary.org/obo/"),
    "dcterms": rdflib.Namespace("http://purl.org/dc/terms/"),
    "fabio": rdflib.Namespace("http://purl.org/spar/fabio/"),
    "mesh": rdflib.Namespace("http://id.nlm.nih.gov/mesh/"),
    "void": rdflib.Namespace("http://rdfs.org/ns/void#"),
    "skos": rdflib.Namespace("http://www.w3.org/2004/02/skos/core#"),
    "chemont": rdflib.Namespace("http://purl.obolibrary.org/obo/CHEMONTID_")
}


# Init

version = config["CHEMONT"].get("version")
chemont_upload_file = config["DEFAULT"].get("upload_file")
chemont_log_dir = config["DEFAULT"].get("log_dir")
n_processes = config["CHEMONT"].getint("n_processes")
path_to_PMID_CID = config["PMID_CID"].get("path")
path_to_inchikey = config["INCHIKEY"].get("path")

log_dir = os.path.join(args.log, chemont_log_dir)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Init output and log files: 
with open(os.path.join(log_dir, "classyFire.log"), "w") as f_log:
    pass

with open(os.path.join(log_dir, "classyFire_error_ids.log"), "w") as f_log:
    pass

with open(os.path.join(log_dir, "ids_no_classify.log"), "w") as f_log:
    pass

# On initialise les ressources :
ClassyFire_direct_p = Database_ressource_version(ressource = "ClassyFire/direct-parent", version = version)
ClassyFire_alternative_p = Database_ressource_version(ressource = "ClassyFire/alternative-parents", version = version)

# On initialise les path où exporter les graphs :
path_direct_p = os.path.join(args.out, ClassyFire_direct_p.ressource, ClassyFire_direct_p.version)
path_alternative_p = os.path.join(args.out, ClassyFire_alternative_p.ressource, ClassyFire_alternative_p.version)

# Check if resource already exist:
uri_direct_p = check_void(os.path.join(path_direct_p, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/ClassyFire/direct-parent"))
uri_alternative_p = check_void(os.path.join(path_alternative_p, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/ClassyFire/alternative-parents"))

if uri_direct_p and uri_alternative_p:
    print("Resource Chemont version " + version + "already exists")

# If not, create resource
else:

    # Check is resource InchiKey and PMID_CID exists
    PMID_CID_uri = check_void(os.path.join(args.out, path_to_PMID_CID, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/PMID_CID"))
    PubChem_inchikey_uri = check_void(os.path.join(args.out, path_to_inchikey, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/PubChem/inchikey"))
    
    if (not PMID_CID_uri) or (not PubChem_inchikey_uri):
        print("PMID_CID resource at " + path_to_PMID_CID + " and/or PubChem inchikey resource at " + path_to_inchikey + " is invalid. Please, provide valid resources, see import_PMID_CID.py and import_PubChem.py.")
        sys.exit(3)
    
    # Get PMID_CID and inchikey graphs
    pmids_cids_graph_list = glob.glob(os.path.join(args.out, path_to_PMID_CID, config["PMID_CID"].get("mask")))
    inchikeys_graph_list = glob.glob(os.path.join(args.out, path_to_inchikey, config["INCHIKEY"].get("mask")))
    
    # Test files
    if (not len(pmids_cids_graph_list)):
        print("No PMID_CID files found at " + path_to_PMID_CID + " with mask " + config["PMID_CID"].get("mask"))
        sys.exit(3)
    if (not len(inchikeys_graph_list)):
        print("No inchikey files found at " + path_to_inchikey + " with mask " + config["INCHIKEY"].get("mask"))
        sys.exit(3)

    # Create CID - Inchikey:
    path_inchiKey = os.path.join(log_dir, "CID_InchiKeys.csv")
    extract_CID_InchiKey(pmids_cids_graph_list, inchikeys_graph_list, path_inchiKey)
    
    # Read input file
    CID_inchiKeys = pd.read_csv(path_inchiKey, sep = ",", dtype= {'CID': str, 'INCHIKEY':str})
    df_list = np.array_split(CID_inchiKeys, n_processes)
    
    # On initialise les listes de graphs :
    ClassyFire_direct_p_graph_l = [ClassyFire_direct_p.create_data_graph(["compound", "chemont"], namespaces) for i in range(0, n_processes)]
    ClassyFire_alternative_p_graph_l = [ClassyFire_alternative_p.create_data_graph(["compound", "chemont"], namespaces) for i in range(0, n_processes)]
    
    if not os.path.exists(path_direct_p):
        os.makedirs(path_direct_p)
    
    if not os.path.exists(path_alternative_p):
        os.makedirs(path_alternative_p)
    
    pool = mp.Pool(processes = n_processes)
    results = [pool.apply_async(classify_df, args=(i, df_list[i], ClassyFire_direct_p_graph_l[i], ClassyFire_alternative_p_graph_l[i], path_direct_p, path_alternative_p, log_dir)) for i in range(0, n_processes)]
    graph_sizes = [p.get() for p in results]
    # Close Pool
    pool.close()
    pool.join()
    export_ressource_metadata(ClassyFire_direct_p, ClassyFire_alternative_p, graph_sizes, [rdflib.URIRef(PMID_CID_uri), rdflib.URIRef(PubChem_inchikey_uri)], path_direct_p, path_alternative_p)

# Write ouput file header :
with open(os.path.join(args.out, chemont_upload_file), "w") as upload_f:
    upload_f.write("delete from DB.DBA.load_list ;\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/ClassyFire/direct-parent/", version, '') + "', '*.ttl.gz', '" + str(ClassyFire_direct_p.uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/ClassyFire/direct-parent/", version, '') + "', 'void.ttl', '" + str(ClassyFire_direct_p.uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/ClassyFire/alternative-parents/", version, '') + "', '*.ttl.gz', '" + str(ClassyFire_alternative_p.uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/ClassyFire/alternative-parents/", version, '') + "', 'void.ttl', '" + str(ClassyFire_alternative_p.uri_version) + "');\n")
    upload_f.write("select * from DB.DBA.load_list;\n")
    upload_f.write("rdf_loader_run();\n")
    upload_f.write("checkpoint;\n")
    upload_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")
