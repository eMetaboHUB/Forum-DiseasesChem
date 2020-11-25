import argparse, sys, os
import configparser
import subprocess

from processing_functions import *

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

# Intialyze attributes and paths: 
# Virtuoso
path_to_dumps = config['VIRTUOSO'].get('path_to_dumps')
url = config['VIRTUOSO'].get('url')
update_f_name = config['VIRTUOSO'].get('update_file')
# SBML
SBML_graph_uri = config['SBML'].get("graph_uri")
# ANNOTATIONS
mapping_graph_uri = config['MAPPING_GRAPH'].get("graph_uri").split('\n')
version = config['ANNOTATION_TYPE'].get('version')
annot_graph_base_uri = "http://database/ressources/annotation_graph/Id_mapping/"

# OUT:
path_to_dir_from_dumps = config['ANNOTATION_TYPE'].get('path_to_dir_from_dumps')
out_path = path_to_dumps + path_to_dir_from_dumps + version + "/"

if not os.path.exists(out_path):
    print("Create output directory at " + out_path)
    os.makedirs(out_path)

header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/turtle"
}
data = {
    "format": "turtle"
}


infered_uris_request = """
DEFINE input:inference 'schema-inference-rules'
DEFINE input:same-as "yes"
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix skos: <http://www.w3.org/2004/02/skos/core#>
CONSTRUCT {
	?specie bqbiol:is ?otherRef . 
}
FROM <%s>
%s
where {
		?specie a SBMLrdf:Species ;
			bqbiol:is ?ref .
		?ref skos:closeMatch ?otherRef .
		FILTER (
			not exists { ?specie bqbiol:is ?otherRef }
		)
}
"""


print("Initialyze update file : " + update_f_name)
with open(path_to_dumps + update_f_name, "w") as update_f:
    pass

# Test if annot graph(s) and SBML graph exists
# SBML
if not ask_for_graph(url, SBML_graph_uri):
    print("SMBL graph " + SBML_graph_uri + " does not exists")
    sys.exit(3)
# ANNOTATIONS
for uri in mapping_graph_uri:
    if not ask_for_graph(url, uri):
        print("Annotation graph " + uri + " does not exists")
        sys.exit(3)

if test_if_graph_exists(url, annot_graph_base_uri + version, [], path_to_dumps, update_f_name):
    print("Graphs not already exists, create new graphs...")

print("Compute Infered uris ...")
test_infered_uris = request_annotation(url, infered_uris_request, SBML_graph_uri, mapping_graph_uri, header, data, out_path + "infered_uris.ttl")
if test_infered_uris:
    print("Infered uris annotation Ok")
else:
    print("Infered uris annotation fail")

# Creation ressource information file
sources_list = mapping_graph_uri + [SBML_graph_uri]
create_annotation_graph_ressource_version(out_path, version, "annotation_graph/Id_mapping", 
"An annotation graph providing supplementary indenfiers from mapping using different external ressources",
"Id mapping annotation graph",
sources_list)
# Create upload file
create_update_file_from_ressource(path_to_dumps, path_to_dir_from_dumps + version, "*.ttl", annot_graph_base_uri + version, update_f_name)