
import argparse, sys, os
import rdflib
import configparser
import subprocess
import gzip

from Id_mapping import Id_mapping
from processing_functions import *

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--version", help="version of the MetaNetX ressource, if none, the date is used")
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

# Global
path_to_dumps = args.out
meta_table = config["META"].get("path")
ftp = config["FTP"].get("ftp")

# MetaNetX:
MetaNetX_v = args.version

path_to_MetaNetX_dir = os.path.join(path_to_dumps, "MetaNetX", MetaNetX_v)
path_to_g_MetaNetX = os.path.join(path_to_MetaNetX_dir, "metanetx.ttl.gz")

uri_source_graph = get_uri_from_void(path_to_MetaNetX_dir)

# Intialyze Object:
map_ids = Id_mapping(MetaNetX_v, ftp)
print("Import configuration table ... ", end = '')
map_ids.import_table_infos(meta_table, sep = "\t")

print("Ok\nTry de create URIs equivalences from MetaNetX graph: ")

# Test if data triples already created:
if (len(glob.glob(os.path.join(path_to_dumps, "Id_mapping", "Inter", "MetaNetX", MetaNetX_v, "void.ttl"))) == 1) and (len(glob.glob(os.path.join(path_to_dumps, "Id_mapping", "Intra", "MetaNetX", MetaNetX_v, "void.ttl"))) == 1):
    print(" - [SKIPPING] " + os.path.join(path_to_dumps, "Id_mapping", "Inter", "MetaNetX", MetaNetX_v, "void.ttl") + " already exists.")
    print(" - [SKIPPING] " + os.path.join(path_to_dumps, "Id_mapping", "Intra", "MetaNetX", MetaNetX_v, "void.ttl") + " already exists")
    print(" - [SKIPPING] Skip Intra/Inter-mapping.")
    sys.exit(1)

update_f_name = "Id_mapping_MetaNetX_upload_file.sh"
with open(os.path.join(path_to_dumps, update_f_name), "w") as update_f:
    pass

# Create graphs :
print("- MetaNetX Inter-mapping")
uri_MetaNetX_inter_eq = map_ids.create_graph_from_MetaNetX(path_to_g_MetaNetX, os.path.join(path_to_dumps, "Id_mapping", "Inter", "MetaNetX"), uri_source_graph)
print("Create upload files ... ", end = '')
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Inter", "MetaNetX", MetaNetX_v), "*.ttl.gz", str(uri_MetaNetX_inter_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Inter", "MetaNetX", MetaNetX_v), "void.ttl", str(uri_MetaNetX_inter_eq), update_f_name)

print("- MetaNetX Intra-mapping")
uri_MetaNetX_intra_eq = map_ids.export_intra_eq(os.path.join(path_to_dumps, "Id_mapping", "Intra"), "MetaNetX")
print("Create upload files ... ", end = '')
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Intra", "MetaNetX", MetaNetX_v), "*.ttl.gz", str(uri_MetaNetX_intra_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Intra", "MetaNetX", MetaNetX_v), "void.ttl", str(uri_MetaNetX_intra_eq), update_f_name)
print("Ok")