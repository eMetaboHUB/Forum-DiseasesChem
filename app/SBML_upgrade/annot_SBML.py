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

header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/html"
}
data = {
    "format": "html"
}

synonyms_request = """
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
INSERT {
    GRAPH <%s%s> { ?specie bqbiol:is ?ref_syn . }
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
INSERT {
	GRAPH <%s%s> { ?specie bqbiol:is ?otherRef . }
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
INSERT {
	GRAPH <%s%s> { ?specie bqbiol:is ?otherRef_syn . }
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
INSERT {
        GRAPH <%s%s> { ?specie voc:hasInchI ?selected_inchi . }
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
INSERT {
        GRAPH <%s%s> { ?specie voc:hasSmiles ?selected_smiles . }
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
if config['ANNOTATION_TYPE'].getboolean('id_mapping'):
    test_synonyms = request_annotation(url, annot_graph_base_uri, synonyms_request, SBML_graph_uri, mapping_graph_uri, version, header, data)
    if test_synonyms:
        print("Synonyms annotation Ok")
    else:
        print("Synonyms annotation fail")
    test_infered_uris = request_annotation(url, annot_graph_base_uri, infered_uris_request, SBML_graph_uri, mapping_graph_uri, version, header, data)
    if test_infered_uris:
        print("Infered uris annotation Ok")
    else:
        print("Infered uris annotation fail")
    test_infered_uris_synonyms = request_annotation(url, annot_graph_base_uri, infered_uris_synonyms_request, SBML_graph_uri, mapping_graph_uri, version, header, data)
    if test_infered_uris_synonyms:
        print("Infered uris synonyms annotation Ok")
    else:
        print("Infered uris synonyms annotation fail")

# Add annotation graph URI from computed Synonyms and infered URIs:
mapping_graph_uri.append(annot_graph_base_uri + version)
# Add annotation graph from external sources containing additional informatio
mapping_graph_uri = mapping_graph_uri + sources_uris

if not ask_for_graph(url, annot_graph_base_uri + version):
    print("SMBL graph " + annot_graph_base_uri + version + " does not exists")
    sys.exit(3)

if config['ANNOTATION_TYPE'].getboolean('inchi'):
    test_inchi = request_annotation(url, annot_graph_base_uri, inchi_annotation_request, SBML_graph_uri, mapping_graph_uri, version, header, data)
    if test_inchi:
        print("Inchi annotation Ok")
    else:
        print("Inchi annotation fail")

if config['ANNOTATION_TYPE'].getboolean('smiles'):
    test_smiles = request_annotation(url, annot_graph_base_uri, smiles_annotation_request, SBML_graph_uri, mapping_graph_uri, version, header, data)
    if test_smiles:
        print("Smiles annotation Ok")
    else:
        print("Smiles annotation fail")