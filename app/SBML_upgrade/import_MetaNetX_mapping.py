
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

# Global
path_to_dumps = args.out + "/"
meta_table = config["META"].get("path")
ftp = config["FTP"].get("ftp")

# MetaNetX:
MetaNetX_v = args.version

path_to_MetaNetX_dir = path_to_dumps + "MetaNetX/" + MetaNetX_v
path_to_g_MetaNetX = path_to_MetaNetX_dir + "/" + "metanetx.ttl.gz"

uri_source_graph = get_uri_from_void(path_to_MetaNetX_dir)

update_f_name = "Id_mapping_MetaNetX_update_file.sh"
with open(path_to_dumps + update_f_name, "w") as update_f:
    pass

# Intialyze Object:
map_ids = Id_mapping(MetaNetX_v, ftp)
print("Import configuration table ... ", end = '')
map_ids.import_table_infos(meta_table, sep = "\t")
# Import graph :
print("Ok\nTry to load MetanetX graph from " + path_to_g_MetaNetX + " ... ", end = '')
graph_metaNetX = rdflib.Graph()
with gzip.open(path_to_g_MetaNetX, "rb") as f_MetaNetX:
    graph_metaNetX.parse(f_MetaNetX, format="turtle")
print("Ok\nTry de create URIs equivalences from MetaNetX graph: ")
# Create graphs :
uri_MetaNetX_inter_eq = map_ids.create_graph_from_MetaNetX(graph_metaNetX, path_to_dumps + "Id_mapping/MetaNetX/", uri_source_graph)
uri_MetaNetX_intra_eq = map_ids.export_intra_eq(path_to_dumps + "Id_mapping/Intra/", "MetaNetX")

print("Create upload files ... ", end = '')
create_upload_file_from_resource(path_to_dumps, "Id_mapping/MetaNetX/" + MetaNetX_v + "/", "*.ttl.gz", str(uri_MetaNetX_inter_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, "Id_mapping/MetaNetX/" + MetaNetX_v + "/", "void.ttl", str(uri_MetaNetX_inter_eq), update_f_name)

create_upload_file_from_resource(path_to_dumps, "Id_mapping/Intra/" + "MetaNetX/" + MetaNetX_v + "/", "*.ttl.gz", str(uri_MetaNetX_intra_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, "Id_mapping/Intra/" + "MetaNetX/" + MetaNetX_v + "/", "void.ttl", str(uri_MetaNetX_intra_eq), update_f_name)
graph_metaNetX = None
print("Ok")