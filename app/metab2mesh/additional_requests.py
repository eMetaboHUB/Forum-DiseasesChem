
from sparql_queries import *
from processing_functions import launch_from_config, build_PMID_list_by_CID_MeSH, prepare_data_frame, send_counting_request
import configparser
import argparse, sys, os, requests

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
header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/csv"
}
data = {
    "format": "csv",
}

# Start data Extraction : 

print("Start Getting MeSH labels")
launch_from_config(prefix, header, data, url, config, 'MESH_NAMES', out_path)

# To Extract CID Names, please use the PubChem translation service at https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi using a list of all cids (ex: all_linked_ids)
# The same thing was done for CID

print("Start getting CID - MeSH coocurences pmid list")

# launch_from_config(prefix, header, data, url, config, 'CID_MESH_PMID_LIST', out_path)
l_pmid_out_path = out_path + config['CID_MESH_PMID_LIST']['out_dir'] + "/"

print("Call aggregate function")
count_cid = send_counting_request(prefix, header, data, url, config, 'CID_MESH_PMID_LIST')
build_PMID_list_by_CID_MeSH(count_cid, config['CID_MESH_PMID_LIST'].getint('limit_pack_ids'), l_pmid_out_path, config['CID_MESH_PMID_LIST'].getint('n_processes'))

os.system("cat " + l_pmid_out_path + "res_offset_aggregate_* >> " + l_pmid_out_path + "res_full.csv")