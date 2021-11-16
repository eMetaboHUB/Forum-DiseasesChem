import argparse, configparser, os, glob, sys, json, rdflib
sys.path.insert(1, 'app/')
from download_functions import download_MetaNetX, check_void

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--log", help="path to log and additional files directory")
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
meta_resource = rdflib.URIRef("https://forum.semantic-metabolomics.org/MetaNetX")
MetaNetX_out_dir = "MetaNetX"
MetaNetX_upload_file = config['DEFAULT'].get("upload_file")
MetaNetX_log_file = config['DEFAULT'].get("log_file")
MetaNetX_version = config['METANETX'].get("version")
MetaNetX_url = config['METANETX'].get("url")
MetaNetX_url = MetaNetX_url.format(version = MetaNetX_version)

# Intialyze logs
log_path = os.path.join(args.log, MetaNetX_log_file)
with open(log_path, "wb") as f_log:
    pass

version_path = os.path.join(args.out, MetaNetX_out_dir, MetaNetX_version)
path_to_void = os.path.join(version_path, "void.ttl")

# Chevk void: 
MetaNetX_uri = check_void(path_to_void, meta_resource)

if not MetaNetX_uri:
    print("MetaNetX version " + MetaNetX_version + " was not found.")
    MetaNetX_uri = download_MetaNetX(version_path, log_path, MetaNetX_version, MetaNetX_url)

# Create MetanetX resource
with open(os.path.join(args.out, MetaNetX_upload_file), "w") as upload_MetaNetX:
    upload_MetaNetX.write("delete from DB.DBA.load_list ;\n")
    upload_MetaNetX.write("ld_dir_all ('" + os.path.join("./dumps/", MetaNetX_out_dir, MetaNetX_version, '') + "', 'metanetx.ttl.gz', '" + MetaNetX_uri + "');\n")
    upload_MetaNetX.write("ld_dir_all ('" + os.path.join("./dumps/", MetaNetX_out_dir, MetaNetX_version, '') + "', 'void.ttl', '" + MetaNetX_uri + "');\n")
    upload_MetaNetX.write("select * from DB.DBA.load_list;\n")
    upload_MetaNetX.write("rdf_loader_run();\n")
    upload_MetaNetX.write("checkpoint;\n")
    upload_MetaNetX.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")