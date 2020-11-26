
import argparse, sys, os, gzip, glob
import rdflib
import configparser
import subprocess

from Id_mapping import Id_mapping
from processing_functions import *

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
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
    "owl": rdflib.Namespace("http://www.w3.org/2002/07/owl#")
}


# Global
path_to_dumps = args.out + "/"
meta_table = config["META"].get("path")
ftp = config["FTP"].get("ftp")

# PubChem:
Pubchem_v = args.version
path_to_pubchem_dir = path_to_dumps + "PubChem_Compound/compound/" + Pubchem_v + "/"
uri_source_graph = get_uri_from_void(path_to_pubchem_dir)

update_f_name = "PubChem_update_file.sh"
with open(path_to_dumps + update_f_name, "w") as update_f:
    pass

# Intialyze Object:
map_ids = Id_mapping(Pubchem_v, namespaces, ftp)
print("Import configuration table ... ", end = '')
map_ids.import_table_infos(meta_table, "\t")

print("Ok\nRead pubchem type graph(s) ... ", end = '')
if len(glob.glob(path_to_pubchem_dir + "*_type*.ttl.gz")) == 0:
    print("Can't find *_type*.ttl.gz PubChem RDF file(s) in " + path_to_pubchem_dir + ". Please, check version.\nIf needed, the resource can be created using build_RDF_store.py")
    sys.exit(3)
g = rdflib.ConjunctiveGraph()
for path in glob.glob(path_to_pubchem_dir + "*_type*.ttl.gz"):
    with gzip.open(path, "rb") as f:
        g.parse(f, format="turtle")

print("Ok\nCreate PubChem mapping graph: ")
uri_pubchem_inter_eq = map_ids.create_graph_from_pubchem_type(g, path_to_dumps + "Id_mapping/PubChem/", uri_source_graph)
print("Create PubChem Intra equivalences graph: ")
uri_pubchem_intra_eq = map_ids.export_intra_eq(path_to_dumps + "Id_mapping/Intra/", "PubChem")

print("Create upload files ...", end = '')
create_upload_file_from_resource(path_to_dumps, "Id_mapping/PubChem/" + Pubchem_v + "/", "*.ttl.gz", str(uri_pubchem_inter_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, "Id_mapping/PubChem/" + Pubchem_v + "/", "void.ttl", str(uri_pubchem_inter_eq), update_f_name)

create_upload_file_from_resource(path_to_dumps, "Id_mapping/Intra/" + "PubChem/" + Pubchem_v + "/", "*.ttl.gz", str(uri_pubchem_intra_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, "Id_mapping/Intra/" + "PubChem/" + Pubchem_v + "/", "void.ttl", str(uri_pubchem_intra_eq), update_f_name)
print("Ok")