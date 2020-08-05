import argparse, sys, os, requests, json
import configparser
from processing_functions import ask_for_graph, import_request_file


parser = argparse.ArgumentParser()
parser.add_argument("--chem", help="Identifier of the chemical involved in the association", type=str)
parser.add_argument("--chemType", help="Type of the chemical identifier: PubChem, ChEBI or ChemOnt", type=str)
parser.add_argument("--MeSH", help="MeSh identifier involved in the association", type=str)
parser.add_argument("--config", help="Path to the request configuration file ", type=str)
args = parser.parse_args()

# Parse config file for request parameters
if not os.path.exists(args.config):
    print("Config file : " + args.config + " does not exist")
    sys.exit(3)

try:    
    config = configparser.ConfigParser()
    config.read(args.config)
except configparser.Error as e:
    print(e)
    sys.exit(3)

# Get Virtuoso endpoint url from config
url = config["VIRTUOSO"].get("url")
# Prepare testing request
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

# Load requests module:
module = import_request_file(config['DEFAULT'].get('request_file'))
prefix = getattr(module, 'prefix')
print(prefix)

chem = args.chem
type = args.chemType
meSh = args.MeSH

if(type not in {"PubChem", "ChEBI", "ClassyFire"}):
    print("Error: chemType muste be PubChem ChEBI, or ClassyFire")
    exit(2)

# Request:
if(type == "PubChem"):
    print("coucou")