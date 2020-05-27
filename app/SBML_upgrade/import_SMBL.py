import argparse, sys, os
import configparser
import subprocess
import rdflib
from processing_functions import *
from Id_mapping import Id_mapping

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


# Intialyze attributes and paths: 

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


# Virtuoso:
path_to_dumps = config['VIRTUOSO'].get('path_to_dumps')
url = config['VIRTUOSO'].get('url')
update_f_name = config['VIRTUOSO'].get('update_file')
# SBML
path_to_g_SBML = config['SBML'].get('g_path')
path_to_dir_SMBL = config['SBML'].get('path_to_dir_from_dumps')
sbml_version = config['SBML'].get('version')
path_to_dir_Intra = config['SBML'].get('path_to_dir_intra_from_dumps')
base_uri_SBML = "http://database/ressources/SMBL/"
#LINKED GRAPH
Intra_eq_base_uri = "http://database/ressources/ressources_id_mapping/Intra/SBML/"

uri = base_uri_SBML + sbml_version

linked_grahs = [Intra_eq_base_uri + sbml_version]

print("Initialyze update file : " + update_f_name)
with open(path_to_dumps + update_f_name, "w") as update_f:
    pass

if test_if_graph_exists(url, uri, linked_grahs, path_to_dumps, update_f_name):
    print("Graphs not already exists, create new graphs...")
else:
    sys.exit(3)

# Move SBML RDF file to Virtuoso shared directory:
print("Try to move SMBL files to Virtuoso shared directory ...")
if not os.path.exists(path_to_dumps + path_to_dir_SMBL):
    os.makedirs(path_to_dumps + path_to_dir_SMBL)
try:
    subprocess.run("cp " + path_to_g_SBML + " " + path_to_dumps + path_to_dir_SMBL, shell = True, stderr=subprocess.STDOUT)
except subprocess.SubprocessError as e:
    print("There was an error when trying to move SBML files : " + e)
    sys.exit(3)
# Load graph
print("Try to load SMBL graph in Virtuoso ...")
create_update_file_from_ressource(path_to_dumps, path_to_dir_SMBL, "*.ttl", uri, update_f_name)

print("Import identifiers from Graph to create SBML URIs intra equivalences")
# Intialyze Object:
map_ids = Id_mapping(sbml_version, namespaces)
print("Import configuration table", end = '')
map_ids.import_table_infos(config['SBML'].get('path_to_table_infos'))
map_ids.get_graph_ids_set(path_to_g_SBML)
print("Export SBML Uris intra equivalences ")
map_ids.export_intra_eq(path_to_dumps + path_to_dir_Intra, "SBML")
print("Try to load SMBL URIs intra equivalences in Virtuoso ...")

create_update_file_from_ressource(path_to_dumps, path_to_dir_Intra + "SBML/" + sbml_version + "/", "*.trig", '', update_f_name)
create_update_file_from_ressource(path_to_dumps, path_to_dir_Intra + "SBML/" + sbml_version + "/", "void.ttl", Intra_eq_base_uri + sbml_version, update_f_name)