import argparse, sys, os
import configparser
import subprocess
import rdflib
from processing_functions import *
from Id_mapping import Id_mapping

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
args = parser.parse_args()

# Intialyze attributes and paths: 

if not os.path.exists(args.config):
    print("Config file : " + args.config + " does not exist")
    sys.exit(3)

try:    
    config = configparser.ConfigParser()
    config.read(args.config)
except configparser.Error as e:
    print(e)
    sys.exit(3)

# Global
path_to_dumps = args.out
meta_table = config["META"].get("path")
update_f_name = config["DEFAULT"].get("upload_file")

# SBML
path_to_g_SBML =  config["SBML"].get("path")
sbml_version = config["SBML"].get("version")
sbml_rdf_format = config["SBML"].get("format")

# URIS
base_uri_SBML = "https://forum.semantic-metabolomics.org/SBML/"

# PROCESSES
uri = base_uri_SBML + sbml_version

gem_file = os.path.basename(path_to_g_SBML)

with open(os.path.join(path_to_dumps, update_f_name), "w") as update_f:
    pass

# Check if the provided sbml is available
if not glob.glob(os.path.join(path_to_dumps, path_to_g_SBML)):
    print("Can't find file at " + os.path.join(path_to_dumps, path_to_g_SBML))
    sys.exit(3)

# Check if this version already exist by checkink the Intra-mapping void
if glob.glob(os.path.join(path_to_dumps, "Id_mapping", "Intra", "SBML", sbml_version, "void.ttl")):
    print("void found at " + os.path.join(path_to_dumps, "Id_mapping", "Intra", "SBML", sbml_version, "void.ttl"))
    print("Skip computation, the resource already exists.")

# If not, create the resource 
else:
    # Intialyze Object:
    map_ids = Id_mapping(sbml_version)
    print("Import configuration table ... ", end = '')
    map_ids.import_table_infos(meta_table, "\t")
    print("OK\nImport identifiers from SBML rdf graph to create SBML URIs intra equivalences ... ", end = '')
    map_ids.get_graph_ids_set(os.path.join(path_to_dumps, path_to_g_SBML), uri, sbml_rdf_format)

    # Else create intra-mapping
    print("- SBML Intra-mapping")
    intra_eq_uri = map_ids.export_intra_eq(os.path.join(path_to_dumps, "Id_mapping", "Intra"), "SBML")
    print("Ok")

print("Export upload file")
create_upload_file_from_resource(path_to_dumps, os.path.dirname(path_to_g_SBML), gem_file, uri, update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Intra", "SBML", sbml_version), "*.ttl.gz", str(intra_eq_uri), update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Intra", "SBML", sbml_version), "void.ttl", str(intra_eq_uri), update_f_name)