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
path_to_docker_yml_file = config['VIRTUOSO'].get('path_to_docker_yml_file')
db_password = config['VIRTUOSO'].get('db_password')
url = config['VIRTUOSO'].get('url')
# SBML
SBML_graph_uri = config['SBML'].get("graph_uri")
# ANNOTATIONS
mapping_graph_uri = config['MAPPING_GRAPH'].get("graph_uri").split('\n')
sources_uris = config['EXT_SOURCES'].get("graph_uri").split('\n')
version = config['ANNOTATION_TYPE'].get('version')
annot_graph_base_uri = config['ANNOTATION_TYPE'].get('annotation_graph_base_uri')

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

synonyms_request = """
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
CONSTRUCT {
    ?specie bqbiol:is ?ref_syn .
}
FROM <%s>
%s
where {
    ?specie a SBMLrdf:Species ;
        bqbiol:is ?ref .
    ?ref skos:exactMatch ?ref_syn option(t_distinct) .

}
"""

infered_uris_request = """
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
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
			&&
			not exists {?ref skos:exactMatch ?otherRef option(t_distinct)}
		)

}
"""

infered_uris_synonyms_request = """
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
CONSTRUCT {
	?specie bqbiol:is ?otherRef_syn . 
}
FROM <%s>
%s
where {
	?otherRef skos:exactMatch ?otherRef_syn option(t_distinct) .
	FILTER (
		not exists { ?specie bqbiol:is ?otherRef_syn }
		&&
		not exists { ?ref skos:exactMatch ?otherRef_syn option(t_distinct) }
	)
	{
		select ?specie ?otherRef ?ref where {
		?specie a SBMLrdf:Species ;
			bqbiol:is ?ref .
		?ref skos:closeMatch ?otherRef .
		FILTER (
			not exists {?specie bqbiol:is ?otherRef }
      &&
    		not exists { ?ref skos:exactMatch ?otherRef option(t_distinct) }
		)

		}
	}
}
"""

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

if test_if_graph_exists(url, annot_graph_base_uri + version, [], path_to_dumps, path_to_docker_yml_file, db_password):
    print("Create graphs ...")

print("Starting annotation ...")
print("Compute Synonyms ...")
test_synonyms = request_annotation(url, synonyms_request, SBML_graph_uri, mapping_graph_uri, header, data, out_path + "synonyms.ttl")
if test_synonyms:
    print("Synonyms annotation Ok")
else:
    print("Synonyms annotation fail")

print("Compute Infered uris ...")
test_infered_uris = request_annotation(url, infered_uris_request, SBML_graph_uri, mapping_graph_uri, header, data, out_path + "infered_uris.ttl")
if test_infered_uris:
    print("Infered uris annotation Ok")
else:
    print("Infered uris annotation fail")

print("Compute Infered uris synonyms...")
test_infered_uris_synonyms = request_annotation(url, infered_uris_synonyms_request, SBML_graph_uri, mapping_graph_uri, header, data, out_path + "infered_uris_synonyms.ttl")
if test_infered_uris_synonyms:
    print("Infered uris synonyms annotation Ok")
else:
    print("Infered uris synonyms annotation fail")

create_update_file_from_ressource(path_to_dumps, path_to_dir_from_dumps + version, path_to_docker_yml_file, db_password, "*.ttl", annot_graph_base_uri + version)