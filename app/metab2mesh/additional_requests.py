
from processing_functions import launch_from_config, build_PMID_list_by_CID_MeSH, prepare_data_frame, send_counting_request, ask_for_graph, import_request_file
import configparser
import argparse, sys, os, requests, subprocess

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

# Initialyse global paramters:
url = config['VIRTUOSO'].get('url')
out_path = config['DEFAULT'].get('out_path')
request_file_name = config['DEFAULT'].get('request_file')
# Get module for sparql queries :
module = import_request_file(request_file_name)
# Get prefix from module :
prefix = getattr(module, 'prefix')
header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/csv"
}
data = {
    "format": "csv",
}

# First step is to test if all the needed graph are present in the RDF Store :
for uri in config['VIRTUOSO'].get("graph_from").split('\n'):
    if not ask_for_graph(url, uri):
        print("Annotation graph " + uri + " does not exists")
        sys.exit(3)

# Start data Extraction : 

print("Start Getting MeSH labels")
launch_from_config(prefix, header, data, url, config, 'MESH_NAMES', out_path, module)

mesh_names_final_path = out_path + config['MESH_NAMES'].get('out_dir') + "/"

print("Concat files")
subprocess.run("cat " + mesh_names_final_path + "res_offset_* >> " + mesh_names_final_path + "res_full.csv", shell = True, check=True)

# To Extract CID Names, please use the PubChem translation service at https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi using a list of all cids (ex: all_linked_ids)
# The same thing was done for CID

print("Start getting CID - MeSH coocurences pmid list")

launch_from_config(prefix, header, data, url, config, 'CID_MESH_PMID_LIST', out_path, module)
l_pmid_out_path = out_path + config['CID_MESH_PMID_LIST']['out_dir'] + "/"

print("Call aggregate function")
count_cid = send_counting_request(prefix, header, data, url, config, 'CID_MESH_PMID_LIST', module)
build_PMID_list_by_CID_MeSH(count_cid, config['CID_MESH_PMID_LIST'].getint('limit_pack_ids'), l_pmid_out_path, config['CID_MESH_PMID_LIST'].getint('n_processes'))

print("Concat files")
subprocess.run("cat " + l_pmid_out_path + "res_offset_aggregate_* >> " + l_pmid_out_path + "res_full.csv", shell = True, check=True)