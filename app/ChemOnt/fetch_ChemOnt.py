import os
import sys
import pandas as pd
import numpy as np
import multiprocessing as mp
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
outpath = config["OUT"].get("path")

# Init output and log files: 
with open("classyFire.log", "w") as f_log:
    pass

with open("classyFire_error_ids.log", "w") as f_log:
    pass

with open("ids_no_classify.log", "w") as f_log:
    pass

# Read input file
CID_inchiKeys = pd.read_csv(config["INPUT"].get("path"), sep = "\t", dtype= {'CID': str, 'INCHIKEY':str})
df_list = np.array_split(CID_inchiKeys, n_processes)
print(df_list)

# On initialise les ressources :
ClassyFire_direct_p = Database_ressource_version(ressource = "ClassyFire/direct-parent", version = version)
ClassyFire_alternative_p = Database_ressource_version(ressource = "ClassyFire/alternatives-parents", version = version)

# On initialise les listes de graphs :
ClassyFire_direct_p_graph_l = [ClassyFire_direct_p.create_data_graph(["compound", "classyfire"], namespaces) for i in range(0, n_processes)]
ClassyFire_alternative_p_graph_l = [ClassyFire_direct_p.create_data_graph(["compound", "classyfire"], namespaces) for i in range(0, n_processes)]

# On initialise les path où exporter les graphs :
path_direct_p = outpath + "/" + ClassyFire_direct_p.ressource + "/" + ClassyFire_direct_p.version + "/"
path_alternative_p = outpath + "/" + ClassyFire_alternative_p.ressource + "/" + ClassyFire_alternative_p.version + "/"
if not os.path.exists(path_direct_p):
    os.makedirs(path_direct_p)

if not os.path.exists(path_alternative_p):
    os.makedirs(path_alternative_p)

pool = mp.Pool(processes = n_processes, maxtasksperchild = 20)
results = [pool.apply_async(classify_df, args=(i, df_list[i], ClassyFire_direct_p_graph_l[i], ClassyFire_alternative_p_graph_l[i], path_direct_p, path_alternative_p)) for i in range(0, n_processes)]
output = [p.get() for p in results]
# Close Pool
pool.close()
pool.join()


