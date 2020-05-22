
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

inchi_annotation_request = """
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
prefix mnx: <https://rdf.metanetx.org/schema/>
prefix sio: <http://semanticscience.org/resource/>
prefix voc:  <http://database/ressources/properties#> 
CONSTRUCT {
        ?specie voc:hasInchI ?selected_inchi .
}
FROM <%s>
%s
where {
        ?specie a SBMLrdf:Species ;
                SBMLrdf:name ?spe_name .
        OPTIONAL { ?specie bqbiol:is ?ref_metaNetX . FILTER ( STRSTARTS(STR(?ref_metaNetX), "https://rdf.metanetx.org/chem/")) }
        OPTIONAL { ?specie bqbiol:is ?ref_chebi . FILTER ( STRSTARTS(STR(?ref_chebi), "http://purl.obolibrary.org/obo/CHEBI_")) }
        OPTIONAL { ?specie bqbiol:is ?ref_pc . FILTER ( STRSTARTS(STR(?ref_pc), "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID")) }     
        { ?ref_metaNetX mnx:inchi ?inchi . }
        UNION
        { ?ref_chebi <http://purl.obolibrary.org/obo/chebi/inchi> ?inchi . }
        UNION
        { 
        ?ref_pc sio:has-attribute ?ref_pc_desc .
        ?ref_pc_desc a sio:CHEMINF_000396 ;
                sio:has-value ?inchi
        }
BIND(URI(str(?inchi)) as ?selected_inchi)
}
"""

smiles_annotation_request = """
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
prefix mnx: <https://rdf.metanetx.org/schema/>
prefix sio: <http://semanticscience.org/resource/>
prefix voc:  <http://database/ressources/properties#> 
CONSTRUCT {
        ?specie voc:hasSmiles ?selected_smiles .
}
FROM <%s>
%s
where {
        ?specie a SBMLrdf:Species ;
                SBMLrdf:name ?spe_name .
        OPTIONAL { ?specie bqbiol:is ?ref_metaNetX . FILTER ( STRSTARTS(STR(?ref_metaNetX), "https://rdf.metanetx.org/chem/")) }
        OPTIONAL { ?specie bqbiol:is ?ref_chebi . FILTER ( STRSTARTS(STR(?ref_chebi), "http://purl.obolibrary.org/obo/CHEBI_")) }
        OPTIONAL { ?specie bqbiol:is ?ref_pc . FILTER ( STRSTARTS(STR(?ref_pc), "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID")) }        
        { ?ref_metaNetX mnx:smiles ?smiles . }
        UNION
        { ?ref_chebi <http://purl.obolibrary.org/obo/chebi/smiles> ?smiles . }
        UNION
        { 
        ?ref_pc sio:has-attribute ?ref_pc_desc .
        ?ref_pc_desc a sio:CHEMINF_000376 ;
                sio:has-value ?smiles
        }
BIND(URI(str(?smiles)) as ?selected_smiles)
}
"""

if not ask_for_graph(url, SBML_graph_uri):
    print("SMBL graph " + SBML_graph_uri + " does not exists")
    sys.exit(3)

for uri in sources_uris:
    if not ask_for_graph(url, uri):
        print("Annotation graph " + uri + " does not exists")
        sys.exit(3)

if test_if_graph_exists(url, annot_graph_base_uri + version, [], path_to_dumps, update_f_name):
    print("Create graphs ...")


test_inchi = request_annotation(url, inchi_annotation_request, SBML_graph_uri, sources_uris, header, data, out_path + "inchi.ttl")
if test_inchi:
        print("Inchi annotation Ok")
else:
        print("Inchi annotation fail")


test_smiles = request_annotation(url, smiles_annotation_request, SBML_graph_uri, sources_uris, header, data, out_path + "smiles.ttl")
if test_smiles:
        print("Smiles annotation Ok")
else:
        print("Smiles annotation fail")

create_update_file_from_ressource(path_to_dumps, path_to_dir_from_dumps + version, "*.ttl", annot_graph_base_uri + version, update_f_name)