import argparse, sys, os
import configparser
import subprocess
import rdflib
from processing_functions import *
from Id_mapping import Id_mapping

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--sbml", help="path to sbml file")
parser.add_argument("--version", help="version of the SBML RDF file")
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
path_to_dumps = args.out + "/"
meta_table = config["META"].get("path")
path_to_g_SBML = args.sbml
ftp = config["FTP"].get("ftp")

# SBML
sbml_version = args.version
sbml_rdf_format = config["SBML"].get("format")
gem_path = path_to_dumps + "GEM/" + sbml_version

# URIS
base_uri_SBML = "https://forum.semantic-metabolomics.org/SBML/"

# PROCESSES
uri = base_uri_SBML + sbml_version

print("Try to move SBML file to Virtuoso shared directory ... ", end = '')
if not os.path.exists(gem_path):
    os.makedirs(gem_path)
try:
    subprocess.run("cp " + path_to_g_SBML + " " + gem_path + "/", shell = True, stderr=subprocess.STDOUT)
except subprocess.SubprocessError as e:
    print("There was an error when trying to move SBML file : " + e)
    sys.exit(3)
print("Ok")

update_f_name = "SBML_upload_file.sh"
with open(path_to_dumps + update_f_name, "w") as update_f:
    pass

gem_file = os.path.basename(path_to_g_SBML)
create_upload_file_from_resource(path_to_dumps, "GEM/" + sbml_version + "/", gem_file, uri, update_f_name)

# Intialyze Object:
map_ids = Id_mapping(sbml_version, ftp)
print("Import configuration table ... ", end = '')
map_ids.import_table_infos(meta_table, "\t")
print("OK\nImport identifiers from SBML rdf graph to create SBML URIs intra equivalences ... ", end = '')
map_ids.get_graph_ids_set(gem_path + "/" + gem_file, uri, sbml_rdf_format)
print("Ok\nExport SBML Uris intra equivalences ... ", end = '')
intra_eq_uri = map_ids.export_intra_eq(path_to_dumps + "Id_mapping/Intra/", "SBML")
print("Export upload file ... ", end = '')
create_upload_file_from_resource(path_to_dumps, "Id_mapping/Intra/SBML/" + sbml_version + "/", "*.ttl.gz", str(intra_eq_uri), update_f_name)
create_upload_file_from_resource(path_to_dumps, "Id_mapping/Intra/SBML/" + sbml_version + "/", "void.ttl", str(intra_eq_uri), update_f_name)
print("Ok")