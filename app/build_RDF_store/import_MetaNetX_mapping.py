
import argparse, sys, os
import rdflib
import configparser
import subprocess
import gzip

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
MetaNetX_out_dir = "MetaNetX"
meta_resource = rdflib.URIRef("https://forum.semantic-metabolomics.org/MetaNetX")
MetaNetX_v = config["METANETX"].get("version")
f_name = config["METANETX"].get("file_name")
update_f_name = config["DEFAULT"].get("upload_file")

path_to_MetaNetX_dir = os.path.join(path_to_dumps, MetaNetX_out_dir, MetaNetX_v)
path_to_g_MetaNetX = os.path.join(path_to_MetaNetX_dir, f_name)

# Create upload file

with open(os.path.join(path_to_dumps, update_f_name), "w") as update_f:
    pass


# Check if this Id-mapping resource for MetaNetX already exists :
uri_MetaNetX_inter_eq = check_void(os.path.join(path_to_dumps, "Id_mapping", "Inter", MetaNetX_out_dir, MetaNetX_v, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/Id_mapping/Inter/MetaNetX"))
uri_MetaNetX_intra_eq = check_void(os.path.join(path_to_dumps, "Id_mapping", "Intra", MetaNetX_out_dir, MetaNetX_v, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/Id_mapping/Intra/MetaNetX"))

if uri_MetaNetX_inter_eq and uri_MetaNetX_intra_eq:
    print("Id-mapping for MetaNetX version " + MetaNetX_v + " already exists, skip computation")

# If not, compute:
else:
    # Check if this MetaNetX version exists:
    uri_source_graph = check_void(os.path.join(path_to_dumps, MetaNetX_out_dir, MetaNetX_v, "void.ttl"), meta_resource)
    if not uri_source_graph:
        print("Can't find a valid version " + MetaNetX_v + " of MetaNetX at " + os.path.join(path_to_dumps, MetaNetX_out_dir, MetaNetX_v))
        print("See import_MetanetX.py")
        sys.exit(3)

    # Intialyze Object:
    map_ids = Id_mapping(MetaNetX_v)
    print("Import configuration table ... ", end = '')
    map_ids.import_table_infos(meta_table, sep = "\t")

    print("Ok\nTry de create URIs equivalences from MetaNetX graph: ")

    # Create Inter equivalences URIs
    print("- MetaNetX Inter-mapping")
    uri_MetaNetX_inter_eq = map_ids.create_graph_from_MetaNetX(path_to_g_MetaNetX, os.path.join(path_to_dumps, "Id_mapping", "Inter", "MetaNetX"), uri_source_graph)

    # Create Intra equivalences URIs
    print("- MetaNetX Intra-mapping")
    uri_MetaNetX_intra_eq = map_ids.export_intra_eq(os.path.join(path_to_dumps, "Id_mapping", "Intra"), "MetaNetX")

# Write upload files
print("Create upload files")

create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Inter", "MetaNetX", MetaNetX_v, ''), "*.ttl.gz", str(uri_MetaNetX_inter_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Inter", "MetaNetX", MetaNetX_v, ''), "void.ttl", str(uri_MetaNetX_inter_eq), update_f_name)

create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Intra", "MetaNetX", MetaNetX_v, ''), "*.ttl.gz", str(uri_MetaNetX_intra_eq), update_f_name)
create_upload_file_from_resource(path_to_dumps, os.path.join("Id_mapping", "Intra", "MetaNetX", MetaNetX_v, ''), "void.ttl", str(uri_MetaNetX_intra_eq), update_f_name)