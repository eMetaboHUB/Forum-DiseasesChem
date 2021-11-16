
import argparse, sys, os, gzip, glob
import rdflib
import configparser
import subprocess

from Id_mapping import Id_mapping
from sbml_processing_functions import *
from download_functions import check_void

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
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


# Init
path_to_dumps = args.out
meta_table = config["META"].get("path")
Pubchem_v = config["PUBCHEM"].get("version")
path_to_dir = config["PUBCHEM"].get("path_to_dir")
mask = config["PUBCHEM"].get("mask")
path_to_version_dir = os.path.join(path_to_dumps, path_to_dir, Pubchem_v)
meta_resource = rdflib.URIRef("https://forum.semantic-metabolomics.org/PubChem/compound")
update_f_name = config["DEFAULT"].get("upload_file")

# Create upload file
with open(os.path.join(path_to_dumps, update_f_name), "w") as update_f:
    pass

# Check is this PubChem Id-mapping already exist
uri_pubchem_inter_eq = check_void(os.path.join(path_to_dumps, "Id_mapping", "Inter", "PubChem", Pubchem_v, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/Id_mapping/Inter/PubChem"))
uri_pubchem_intra_eq = check_void(os.path.join(path_to_dumps, "Id_mapping", "Intra", "PubChem", Pubchem_v, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/Id_mapping/Intra/PubChem"))
if uri_pubchem_inter_eq and uri_pubchem_intra_eq:
    print("Id-mapping for PubChem version " + Pubchem_v + " already exists, skip computation")

# If not, create
else:

    # Check if the PubChem resource exists
    uri_source_graph = check_void(os.path.join(path_to_version_dir, "void.ttl"), meta_resource)
    if not uri_source_graph:
        print("Can't find a valid version " + Pubchem_v + " of PubChem Compound at " + path_to_version_dir)
        print("See import_PubChem.py")
        sys.exit(3)
    
    # Intialyze Object:
    map_ids = Id_mapping(Pubchem_v)
    print("Import configuration table ... ", end = '')
    map_ids.import_table_infos(meta_table, "\t")

    # Create Inter equivalences URIs
    print("Ok\nCreate PubChem mapping graph: ")
    uri_pubchem_inter_eq = map_ids.create_graph_from_pubchem_type(path_to_version_dir, os.path.join(path_to_dumps, "Id_mapping", "Inter", "PubChem"), uri_source_graph, mask)

    # Create Intra equivalences URIs
    print("Create PubChem Intra equivalences graph: ")
    uri_pubchem_intra_eq = map_ids.export_intra_eq(os.path.join(path_to_dumps, "Id_mapping", "Intra"), "PubChem")

# Write upload files
print("Create upload files")
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Inter", "PubChem", Pubchem_v, ''), "*.ttl.gz", str(uri_pubchem_inter_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Inter", "PubChem", Pubchem_v, ''), "void.ttl", str(uri_pubchem_inter_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Intra", "PubChem", Pubchem_v, ''), "*.ttl.gz", str(uri_pubchem_intra_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Intra", "PubChem", Pubchem_v, ''), "void.ttl", str(uri_pubchem_intra_eq), update_f_name)