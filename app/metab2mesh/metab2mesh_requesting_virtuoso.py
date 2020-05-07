from sparql_queries import *
from processing_functions import launch_from_config, build_PMID_list_by_CID_MeSH, prepare_data_frame, send_counting_request
import configparser
import argparse, sys, os, requests, json

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
X_name = config['X'].get('name')
Y_name = config['Y'].get('name')
print("Prepare data Extraction for contingency table using Set X as " + X_name + " and Set Y as : " + Y_name)

# Count distinct CID
print("Start getting " + X_name + "_" + Y_name +" coocurences")
launch_from_config(prefix, header, data, url, config, 'X_Y', out_path)

# Get CID distinct PMID :
print("Start getting " + X_name + " sets size") 
launch_from_config(prefix, header, data, url, config, 'X', out_path)

# Get MeSH distinct PMID :
print("Start getting " + Y_name + " sets size")
launch_from_config(prefix, header, data, url, config, 'Y', out_path)

# On compte le nombre total de distinct pmids qui ont un CID et un MeSH
count_U = send_counting_request(prefix, header, data, url, config, 'U')
# Nb. total pmids = 8754160

print("Start merge files and create data.frame")
cid_mesh_out_path = out_path + config['X_Y']['out_dir'] + "/"
cid_pmid_out_path = out_path + config['X']['out_dir'] + "/"
mesh_pmid_out_path = out_path + config['Y']['out_dir'] + "/"

df_metab2mesh = prepare_data_frame(config, cid_mesh_out_path , cid_pmid_out_path , mesh_pmid_out_path, count_U, out_path + config['DEFAULT'].get('df_out_dir') + "/", config['DEFAULT'].getint('file_size'))