
from sparql_queries import *
from processing_functions import launch_from_config, build_PMID_list_by_CID_MeSH, prepare_data_frame
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
R1_name = config['MESH_NAMES'].get('name')
R2_name = config['CID_MESH_PMID_LIST'].get('name')
print("Counting total number of " + R1_name + " ...")
# Count distinct CID
data["query"] = prefix + eval(config['CID_MESH_PMID_LIST'].get('Size_Request_name'))
count_cid_res = requests.post(url = url, headers = header, data = data)
count_cid = int(count_cid_res.text.splitlines().pop(1))

print("Counting total number of MESH ...")
# Count distinct MESH
data["query"] = prefix + eval(config['MESH_NAMES'].get('Size_Request_name'))
count_mesh_res = requests.post(url = url, headers = header, data = data)
count_mesh = int(count_mesh_res.text.splitlines().pop(1))
print("There are " + str(count_mesh) + " distinct MESH in the graph")

# Extract MeSH Names
print("MESH Name Extraction ...")
launch_from_config(count_mesh, MESH_name, prefix, header, data, url, config, 'MESH_NAMES', out_path)

# To Extract CID Names, please use the PubChem translation service at https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi using a list of all cids (ex: all_linked_ids)
# The same thing was done for CID

print("Start getting CID - MeSH coocurences pmid list")

launch_from_config(count_cid, list_of_distinct_pmid_by_CID_MeSH, prefix, header, data, url, config, 'CID_MESH_PMID_LIST', out_path)
l_pmid_out_path = out_path + config['CID_MESH_PMID_LIST']['out_dir'] + "/"
build_PMID_list_by_CID_MeSH(count_cid, config['CID_MESH_PMID_LIST']['limit_pack_ids'], l_pmid_out_path, config['CID_MESH_PMID_LIST']['n_processes'])

os.system("cat " + l_pmid_out_path + "res_offset_aggregate_* >> " + l_pmid_out_path + "res_full.csv")