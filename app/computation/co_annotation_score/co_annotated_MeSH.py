import argparse, sys, os, requests, json
import configparser
sys.path.append("app/computation")
from processing_functions import ask_for_graph, import_request_file

parser = argparse.ArgumentParser()
parser.add_argument("--chem", help="Identifier of the chemical involved in the association", type=str)
parser.add_argument("--chemType", help="Type of the chemical identifier: PubChem, ChEBI or ChemOnt", type=str)
parser.add_argument("--MeSH", help="Identifier of the MeSH involved in the association", type=str)
parser.add_argument("--config", help="Path to the request configuration file ", type=str)
parser.add_argument("--out", help="Path to output file", type=str)
parser.add_argument("--TreeList", help="List of MeSH Tree code, sperated by a |. Ex: C|A|D|G|B|F|I|J", type = str)
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
print("Check graphs ... ", end = '')
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
Tree_list = args.TreeList

if(type not in {"PubChem", "ChEBI", "ChemOnt"}):
    print("Error: chemType muste be PubChem ChEBI, or ChemOnt")
    exit(2)

# Request:
SPARQL_request = getattr(module, type)
formated_SPARQL_request = SPARQL_request % (graph_from, ("<" + config['NAMESPACES'].get(type) + chem + ">"), ("<" + config['NAMESPACES'].get("MeSH") + MeSH + ">"), Tree_list)

# Send query
query = prefix + formated_SPARQL_request

print("Ok\nSending request ... ", end = '')

r_data = data
r_data["query"] = query
r = requests.post(url = url, headers = header, data = r_data)
if r.status_code != 200:
    print("Error in request while determining publication involved in the association between chemical: " + chem + " and MeSH Descriptor: " + MeSH)
    print(r.text)
    sys.exit(3)

print("Ok\nExport MeSH coocurences to out ... ", end = '')

lines = r.text.splitlines()
# Is the file empty ? If not write file at outpath
if(len(lines) > 1):
    with open(out, "w") as out_f:
        for l in lines:
            out_f.write(l + "\n")
    print("Ok")
else:
    print("Fail\nNo results for association between chemical: " + "<" + config['NAMESPACES'].get(type) + chem + ">" + " and MeSH Descriptor: " + MeSH + ".")