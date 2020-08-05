import argparse, sys, os, requests, json
import configparser
from processing_functions import ask_for_graph, import_request_file


parser = argparse.ArgumentParser()
parser.add_argument("--chem", help="Identifier of the chemical involved in the association", type=str)
parser.add_argument("--chemType", help="Type of the chemical identifier: PubChem, ChEBI or ChemOnt", type=str)
parser.add_argument("--MeSH", help="MeSh identifier involved in the association", type=str)
parser.add_argument("--config", help="Path to the request configuration file ", type=str)
parser.add_argument("--out", help="Path to output directory", type=str)
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
# Format sources graphs
graph_from = "\n".join(["FROM <" + uri + ">" for uri in config['VIRTUOSO'].get("graph_from").split('\n')])

# Get main arguments
chem = args.chem
type = args.chemType
MeSH = args.MeSH
out = args.out

if(type not in {"PubChem", "ChEBI", "ClassyFire"}):
    print("Error: chemType muste be PubChem ChEBI, or ClassyFire")
    exit(2)

# Request:
SPARQL_request = getattr(module, type)
formated_SPARQL_request = SPARQL_request % (graph_from, ("<" + config['NAMESPACES'].get(type) + chem + ">"), ("<" + config['NAMESPACES'].get("MeSH") + MeSH + ">"))

# Prepare logs: 
with open(out + "/wordcloud.log", "w") as log_fail:
    pass

# Send query
query = prefix + formated_SPARQL_request
print(query)
r_data = data
r_data["query"] = query
r = requests.post(url = url, headers = header, data = r_data)
if r.status_code != 200:
    print("Error in request while determining publication involved in the association between chemical: " + chem + " and MeSH Descriptor: " + MeSH + ".\n Check logs at " + out)
    with open(out + "/wordcloud.log", "w") as log_fail:
        log_fail.write("Request failed for chemical: " + chem + " and MeSh Descriptor: " + MeSH + "\n")
        log_fail.write(r.text + "\n")
    sys.exit(3)

lines = r.text.splitlines()
# Is the file empty ? If not write file at outpath
if(len(lines) > 1):
    with open(out + "/wordcloud_count.csv", "w") as out_f:
        for l in lines:
            out_f.write(l + "\n")
else:
    print("Result for association between chemical: " + chem + " and MeSH Descriptor: " + MeSH + ". Check identifiers or if there really are associations")