
import argparse, sys, os, requests, json
import rdflib
import configparser
import subprocess

from Id_mapping import Id_mapping
from processing_functions import *

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
    "skos": rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
}

# Intialyze attributes and paths: 
# Virtuoso:
path_to_dumps = config['VIRTUOSO'].get('path_to_dumps')
path_to_docker_yml_file = config['VIRTUOSO'].get('path_to_docker_yml_file')
db_password = config['VIRTUOSO'].get('db_password')
url = config['VIRTUOSO'].get('url')
# MetaNetX:
MetaNetX_v = config['METANETX'].get('version')
path_to_g_MetaNetX = config['METANETX'].get('g_path')
path_to_dir_MetaNetX = config['METANETX'].get('path_to_dir_from_dumps')

if test_if_graph_exists(url, "http://database/ressources/ressources_id_mapping/MetaNetX/" + MetaNetX_v):
    print("Mapping v." + MetaNetX_v + " graph already exist !")
else:
    print("Mapping v." + MetaNetX_v + " graph don't exist, create graph.")
    # Intialyze Object:
    map_ids = Id_mapping(MetaNetX_v, namespaces)
    print("Import configuration table ...", end = '')
    map_ids.import_table_infos(config['METANETX'].get('path_to_table_infos'))
    # Import graph :
    print("Ok\nTry to load MetanetX graph from " + config['METANETX'].get('g_path') + " ...", end = '')
    # graph_metaNetX = rdflib.Graph()
    # graph_metaNetX.parse(path_to_g_MetaNetX, format = "turtle")
    print("Ok\nTry de create URIs equivalences from MetaNetX graph ...")
    # Create graphs :
    # map_ids.create_graph_from_MetaNetX(graph_metaNetX, path_to_dumps + path_to_dir_MetaNetX)
    print("Try to load mapping graphs in Virtuoso ...")
    dockvirtuoso = subprocess.check_output("docker-compose -f '" + path_to_docker_yml_file + "' ps | grep virtuoso | awk '{print $1}'", shell = True, universal_newlines=True, stderr=subprocess.STDOUT).rstrip()
    create_update_file_from_ressource(path_to_dumps, path_to_dir_MetaNetX + MetaNetX_v + "/")
    subprocess.run("docker exec -t " + dockvirtuoso + " bash -c \'/usr/local/virtuoso-opensource/bin/isql-v 1111 dba \"" + db_password + "\" ./dumps/update.sh'", shell = True, stderr=subprocess.STDOUT)