import argparse, sys, os, requests, json
import rdflib
import configparser
import subprocess

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

path_to_g_SBML = config['SBML'].get('g_path')
path_to_dir_SMBL = config['SBML'].get('path_to_dir_from_dumps')

# Move SBML RDF file to Virtuoso shared directory:
if not os.path.exists(path_to_g_SBML + ".graph"):
    print("There is no .graph file attached to the SBML file.\nPlease create a <source-file>.ttl.graph containing the URI of the graph to load it.")
    sys.exit(3)
print("Try to move SMBL files to Virtuoso shared directory ...")
if not os.path.exists(path_to_dumps + path_to_dir_SMBL):
    os.makedirs(path_to_dumps + path_to_dir_SMBL)
subprocess.run("cp " + path_to_g_SBML + " " + path_to_g_SBML + ".graph " + path_to_dumps + path_to_dir_SMBL, shell = True, stderr=subprocess.STDOUT)

print("Try to load SMBL graph in Virtuoso ...")
dockvirtuoso = subprocess.check_output("docker-compose -f '" + path_to_docker_yml_file + "' ps | grep virtuoso | awk '{print $1}'", shell = True, universal_newlines=True, stderr=subprocess.STDOUT).rstrip()
create_update_file_from_graph_dir(path_to_dumps, path_to_dir_SMBL)
subprocess.run("docker exec -t " + dockvirtuoso + " bash -c \'/usr/local/virtuoso-opensource/bin/isql-v 1111 dba \"" + db_password + "\" ./dumps/update.sh'", shell = True, stderr=subprocess.STDOUT)