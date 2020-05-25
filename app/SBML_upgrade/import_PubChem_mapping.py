
import argparse, sys, os, gzip, glob
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
url = config['VIRTUOSO'].get('url')
update_f_name = config['VIRTUOSO'].get('update_file')
# PubChem:
# MetaNetX:
Pubchem_v = config['PUBCHEM'].get('version')
path_to_pubchem_dir = config['PUBCHEM'].get('path_to_pubchem_dir')
path_to_pubchem_dumps_dir = config['PUBCHEM'].get('path_to_dir_from_dumps')
base_uri_pubchem = config['PUBCHEM'].get('base_uri')
# Intra
path_to_dir_Intra = config['INTRA'].get('path_to_dir_from_dumps')
base_uri_Intra = config['INTRA'].get('base_uri')

uri_PubChem = base_uri_pubchem + Pubchem_v
linked_grahs = [base_uri_Intra + Pubchem_v]

print("Initialyze update file : " + update_f_name)
with open(path_to_dumps + update_f_name, "w") as update_f:
    pass

# Test if graph exists
if test_if_graph_exists(url, uri_PubChem, linked_grahs, path_to_dumps, update_f_name):
    print("Create graphs ...")
else:
    sys.exit(3)

# Intialyze Object:
map_ids = Id_mapping(Pubchem_v, namespaces)
print("Import configuration table ...", end = '')
map_ids.import_table_infos(config['PUBCHEM'].get('path_to_table_infos'))

print("Ok\nRead pubchem type graph(s) ...", end = '')
g = rdflib.ConjunctiveGraph()
for path in glob.glob(path_to_pubchem_dir + "*_type*.ttl.gz"):
    with gzip.open(path, "rb") as f:
        g.parse(f, format="turtle")

print("Ok\nCreate PubChem mapping graph")
map_ids.create_graph_from_pubchem_type(g, path_to_dumps + path_to_pubchem_dumps_dir)
print("Create PubChem Intra equivalences graph ")
map_ids.export_intra_eq(path_to_dumps + path_to_dir_Intra, "PubChem")

print("Try to load mapping graphs in Virtuoso ...")
create_update_file_from_ressource(path_to_dumps, path_to_pubchem_dumps_dir + Pubchem_v + "/", "*.trig", '', update_f_name)
create_update_file_from_ressource(path_to_dumps, path_to_pubchem_dumps_dir + Pubchem_v + "/", "ressource_info_*.ttl", base_uri_pubchem + Pubchem_v, update_f_name)

print("Try to intra mapping graphs in Virtuoso ...")
create_update_file_from_ressource(path_to_dumps, path_to_dir_Intra + "PubChem/" + Pubchem_v + "/", "*.trig", '', update_f_name)
create_update_file_from_ressource(path_to_dumps, path_to_dir_Intra + "PubChem/" + Pubchem_v + "/", "ressource_info_*.ttl", base_uri_Intra + Pubchem_v, update_f_name)