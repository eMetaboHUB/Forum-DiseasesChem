


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