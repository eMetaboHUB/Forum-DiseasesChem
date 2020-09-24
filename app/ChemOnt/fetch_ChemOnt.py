import os
import sys
import pandas as pd
import numpy as np
import multiprocessing as mp
import subprocess
import rdflib
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version
from processing_functions import *
import argparse, configparser

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
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
version = config["PROCESSES"].get("version")
n_processes = config["PROCESSES"].getint("n_processes")
path_to_share = config["PROCESSES"].get("path_to_share")
path_out = config["PROCESSES"].get("out")
inchikey_v = config["INCHIKEYS"].get("version")
pmids_cids_v = config["PMID_CID"].get("version")

# Init output and log files: 
with open(path_out + "classyFire.log", "w") as f_log:
    pass

with open(path_out + "classyFire_error_ids.log", "w") as f_log:
    pass

with open(path_out + "ids_no_classify.log", "w") as f_log:
    pass


pmids_cids_graph_list = get_graph_list(path_to_share, inchikey_v, "PMID_CID/", "*.trig.gz")
inchikeys_graph_list = get_graph_list(path_to_share, pmids_cids_v, "PubChem_InchiKey/inchikey/", "pc_inchikey2compound_*.ttl.gz")  # pc_inchikey2compound_*.ttl.gz
# Create CID - InchiLKey:
path_inchiKey = path_out + "CID_InchiKeys.csv"
extract_CID_InchiKey(path_to_share, pmids_cids_graph_list, inchikeys_graph_list, path_inchiKey)

# Read input file
CID_inchiKeys = pd.read_csv(path_inchiKey, sep = ",", dtype= {'CID': str, 'INCHIKEY':str})
df_list = np.array_split(CID_inchiKeys, n_processes)

# On initialise les ressources :
ClassyFire_direct_p = Database_ressource_version(ressource = "ClassyFire/direct-parent", version = version)
ClassyFire_alternative_p = Database_ressource_version(ressource = "ClassyFire/alternative-parents", version = version)

# On initialise les listes de graphs :
ClassyFire_direct_p_graph_l = [ClassyFire_direct_p.create_data_graph(["compound", "classyfire"], namespaces) for i in range(0, n_processes)]
ClassyFire_alternative_p_graph_l = [ClassyFire_alternative_p.create_data_graph(["compound", "classyfire"], namespaces) for i in range(0, n_processes)]

# On initialise les path où exporter les graphs :
path_direct_p = path_to_share + "/" + ClassyFire_direct_p.ressource + "/" + ClassyFire_direct_p.version + "/"
path_alternative_p = path_to_share + "/" + ClassyFire_alternative_p.ressource + "/" + ClassyFire_alternative_p.version + "/"
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
export_ressource_metadata(ClassyFire_alternative_p, ClassyFire_direct_p, graph_sizes, [rdflib.URIRef("http://database/ressources/PubChem/compound"), rdflib.URIRef("http://database/ressources/ChemOnt")], path_direct_p, path_alternative_p)

# Compress files:
try:
    subprocess.run("gzip " + path_to_share + "/ClassyFire/direct-parent/" + version + "/*.trig", shell = True, check=True, stderr = subprocess.PIPE)
    subprocess.run("gzip " + path_to_share + "/ClassyFire/alternative-parents/" + version + "/*.trig", shell = True, check=True, stderr = subprocess.PIPE)
except subprocess.CalledProcessError as e:
    print("Error while trying to compress files")
    print(e)
    sys.exit(3)

# Write ouput file header :
with open(path_to_share + "/upload_ClassyFire.sh", "w") as upload_f:
    upload_f.write("delete from DB.DBA.load_list ;\n")
    upload_f.write("ld_dir_all ('./dumps/ClassyFire/direct-parent/" + version + "/', '*.trig.gz', '');\n")
    upload_f.write("ld_dir_all ('./dumps/ClassyFire/direct-parent/" + version + "/', 'void.ttl', '" + str(ClassyFire_direct_p.uri_version) + "');\n")
    upload_f.write("ld_dir_all ('./dumps/ClassyFire/alternative-parents/" + version + "/', '*.trig.gz', '');\n")
    upload_f.write("ld_dir_all ('./dumps/ClassyFire/alternative-parents/" + version + "/', 'void.ttl', '" + str(ClassyFire_alternative_p.uri_version) + "');\n")
    upload_f.write("select * from DB.DBA.load_list;\n")
    upload_f.write("rdf_loader_run();\n")
    upload_f.write("checkpoint;\n")
    upload_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")
