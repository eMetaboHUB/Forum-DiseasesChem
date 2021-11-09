import os
import sys
import pandas as pd
import numpy as np
import multiprocessing as mp
import subprocess
import glob
import rdflib
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version
from processing_functions import *
import argparse, configparser

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--log", help="path to log and additional files directory")
parser.add_argument("--version", help="version of the PMID-CID ressource, if none, the date is used")
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
    "classyfire": rdflib.Namespace("http://purl.obolibrary.org/obo/CHEMONTID_")
}

# Get initial parameters
version = args.version
n_processes = config["PROCESSES"].getint("n_processes")
ftp = config['FTP'].get('ftp')
path_to_share = args.out + "/"
path_out = args.log + "/"

# Init output and log files: 
with open(path_out + "classyFire.log", "w") as f_log:
    pass

with open(path_out + "classyFire_error_ids.log", "w") as f_log:
    pass

with open(path_out + "ids_no_classify.log", "w") as f_log:
    pass

# On initialise les ressources :
ClassyFire_direct_p = Database_ressource_version(ressource = "ClassyFire/direct-parent", version = version)
ClassyFire_alternative_p = Database_ressource_version(ressource = "ClassyFire/alternative-parents", version = version)

# On initialise les path où exporter les graphs :
path_direct_p = os.path.join(args.out, ClassyFire_direct_p.ressource, ClassyFire_direct_p.version)
path_alternative_p = os.path.join(args.out, ClassyFire_alternative_p.ressource, ClassyFire_alternative_p.version)

# Check if a previous version already exists :
if (len(glob.glob(os.path.join(path_direct_p, "void.ttl"))) == 1) and (len(glob.glob(os.path.join(path_alternative_p, "void.ttl"))) == 1):
    print("This version already exist, skip computation.")
else:
    pmids_cids_graph_list = get_graph_list(args.out, "PMID_CID/", "*.ttl.gz")
    inchikeys_graph_list = get_graph_list(args.out, "PubChem_InchiKey/inchikey/", "pc_inchikey2compound_*.ttl.gz")  
    # Create CID - InchiLKey:
    path_inchiKey = os.path.join(path_out, "CID_InchiKeys.csv")
    extract_CID_InchiKey(pmids_cids_graph_list, inchikeys_graph_list, path_inchiKey)
    
    # Read input file
    CID_inchiKeys = pd.read_csv(path_inchiKey, sep = ",", dtype= {'CID': str, 'INCHIKEY':str})
    df_list = np.array_split(CID_inchiKeys, n_processes)
    
    # On initialise les listes de graphs :
    ClassyFire_direct_p_graph_l = [ClassyFire_direct_p.create_data_graph(["compound", "classyfire"], namespaces) for i in range(0, n_processes)]
    ClassyFire_alternative_p_graph_l = [ClassyFire_alternative_p.create_data_graph(["compound", "classyfire"], namespaces) for i in range(0, n_processes)]
    
    if not os.path.exists(path_direct_p):
        os.makedirs(path_direct_p)
    
    if not os.path.exists(path_alternative_p):
        os.makedirs(path_alternative_p)
    
    pool = mp.Pool(processes = n_processes)
    results = [pool.apply_async(classify_df, args=(i, df_list[i], ClassyFire_direct_p_graph_l[i], ClassyFire_alternative_p_graph_l[i], path_direct_p, path_alternative_p, path_out)) for i in range(0, n_processes)]
    graph_sizes = [p.get() for p in results]
    # Close Pool
    pool.close()
    pool.join()
    export_ressource_metadata(ClassyFire_direct_p, ClassyFire_alternative_p, graph_sizes, [rdflib.URIRef("https://forum.semantic-metabolomics.org/PubChem/compound"), rdflib.URIRef("https://forum.semantic-metabolomics.org/ChemOnt")], path_direct_p, path_alternative_p, ftp)

# The same for the both: 
version = ClassyFire_direct_p.version

# Write ouput file header :
with open(os.path.join(path_to_share, "upload_ClassyFire.sh"), "w") as upload_f:
    upload_f.write("delete from DB.DBA.load_list ;\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/ClassyFire/direct-parent/", version, '') + "', '*.ttl.gz', '" + str(ClassyFire_direct_p.uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/ClassyFire/direct-parent/", version, '') + "', 'void.ttl', '" + str(ClassyFire_direct_p.uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/ClassyFire/alternative-parents/", version, '') + "', '*.ttl.gz', '" + str(ClassyFire_alternative_p.uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/ClassyFire/alternative-parents/", version, '') + "', 'void.ttl', '" + str(ClassyFire_alternative_p.uri_version) + "');\n")
    upload_f.write("select * from DB.DBA.load_list;\n")
    upload_f.write("rdf_loader_run();\n")
    upload_f.write("checkpoint;\n")
    upload_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")
