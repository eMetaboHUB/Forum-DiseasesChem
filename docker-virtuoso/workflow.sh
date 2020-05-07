#!/bin/bash

if [ -d "data" ]; then
rm -r data
rm share/upload.sh
docker-compose down
fi

docker-compose up -d

# upload data
# Allowing request by service :
echo "GRANT SELECT ON \"DB\".\"DBA\".\"SPARQL_SINV_2\" TO \"SPARQL\";" >> share/upload.sh
echo "GRANT EXECUTE ON \"DB\".\"DBA\".\"SPARQL_SINV_IMP\" TO \"SPARQL\";" >> share/upload.sh
# Allowing insert in graph :
echo "GRANT EXECUTE ON \"DB\".\"DBA\".\"EXEC_AS\" TO \"SPARQL\";" >> share/upload.sh
echo "GRANT EXECUTE ON \"DB\".\"DBA\".\"SPARQL_INSERT_DICT_CONTENT\" TO \"SPARQL\";" >> share/upload.sh

# Importing namespace : 
echo "DB.DBA.XML_SET_NS_DECL ('SBMLrdf', 'http://identifiers.org/biomodels.vocabulary#', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('bqbiol', 'http://biomodels.net/biology-qualifiers#', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('mnxCHEM', 'http://identifiers.org/metanetx.chemical/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('chebi', 'http://identifiers.org/chebi/CHEBI:', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('fbc', 'http://www.sbml.org/sbml/level3/version1/fbc/version2#', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('model', 'http:doi.org/10.1126/scisignal.aaz1482#', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('cid', 'http://identifiers.org/pubchem.compound/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('uniprot', 'http://identifiers.org/uniprot/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('ncbigene', 'http://identifiers.org/ncbigene/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('ensembl', 'http://identifiers.org/ensembl/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('hgnc_symbol', 'http://identifiers.org/hgnc.symbol/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('kegg_compound', 'http://identifiers.org/kegg.compound/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('hmdb', 'http://identifiers.org/hmdb/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('lipidmaps', 'http://identifiers.org/lipidmaps/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('kegg_rdf', 'https://www.kegg.jp/entry/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('cid_rdf', 'http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('chebi_rdf', 'http://purl.obolibrary.org/obo/CHEBI_', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('chebi_2', 'https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('chembl', 'http://identifiers.org/chembl.compound/', 2);">> share/upload.sh
echo "DB.DBA.XML_SET_NS_DECL ('chembl_rdf', 'http://rdf.ebi.ac.uk/resource/chembl/molecule/', 2);">> share/upload.sh

# Start loading data :
echo "DELETE FROM DB.DBA.RDF_QUAD ;" >> share/upload.sh

# echo "ld_dir_all ('./dumps/HumanGEM/', '*.ttl', 'http://database/ressources/SMBL');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/MetaNetX/', '*.ttl.gz', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/annot_graphs/MetaNetX_BiGG/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/annot_graphs/MetaNetX_BiGG/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/Id_mapping/UniChem/2020-04-22/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/Id_mapping/UniChem/2020-04-22/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/Id_mapping/MetaNetX/2020-04-22/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/Id_mapping/MetaNetX/2020-04-22/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/Id_mapping/BiGG/2020-04-22/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/Id_mapping/BiGG/2020-04-22/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/Id_mapping/Intra/2020-04-22/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/Id_mapping/Intra/2020-04-22/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/BiGG_inchi_and_smiles/', '*.ttl', 'http://database/ressources/ressources_id_mapping/BiGG');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/CID_PMID/SMBL_2020-04-06/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/CID_PMID/SMBL_2020-04-06/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/CID_PMID_endpoints/SMBL_2020-04-06/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/CID_PMID_endpoints/SMBL_2020-04-06/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/PMID_CID/2020-04-18/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/PMID_CID/2020-04-18/', '*.trig.gz', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/PMID_CID_endpoints/2020-04-18/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/PMID_CID_endpoints/2020-04-18/', '*.trig.gz', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/PubChem_Compound/CompoundFiltered/2020-04-29/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/PubChem_Compound/CompoundFiltered/2020-04-29/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/PubChem_Descriptor/DescriptorFiltered/2020-04-29/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/PubChem_Descriptor/DescriptorFiltered/2020-04-29/', '*.trig', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/PubChem_References/PrimarySubjectTermFiltered/2020-04-20/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/PubChem_References/PrimarySubjectTermFiltered/2020-04-20/', '*.trig.gz', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/PubChem_References/referenceFiltered/2020-04-19/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/PubChem_References/referenceFiltered/2020-04-19/', '*.trig.gz', '');" >> share/upload.sh

# echo "ld_dir_all ('./dumps/MeSH/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
# echo "ld_dir_all ('./dumps/MeSH/', '*.trig', '');" >> share/upload.sh

echo "ld_dir_all ('./dumps/vocabulary/', '*.ttl', 'http://database/inference-rules/');" >> share/upload.sh
echo "ld_dir_all ('./dumps/vocabulary/', '*.rdf', 'http://database/inference-rules/');" >> share/upload.sh
echo "ld_dir_all ('./dumps/vocabulary/', '*.owl', 'http://database/inference-rules/');" >> share/upload.sh

echo "select * from DB.DBA.load_list;" >> share/upload.sh
echo "rdf_loader_run();" >> share/upload.sh
echo "checkpoint;" >> share/upload.sh
echo "select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;" >> share/upload.sh

# Set rules inferences
echo "RDFS_RULE_SET ('schema-inference-rules', 'http://database/inference-rules/');" >> share/upload.sh
echo "checkpoint;" >> share/upload.sh

sleep 5

dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')

sleep 10

docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/upload.sh'

echo "MetDisease database endpoint : http://localhost:9980/sparql"