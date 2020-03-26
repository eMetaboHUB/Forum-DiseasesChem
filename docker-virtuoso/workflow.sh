#!/bin/bash

if [ -d "data" ]; then
rm -r data
rm share/upload.sh
docker-compose down
fi

docker-compose up -d

# upload data
echo "DELETE FROM DB.DBA.RDF_QUAD ;" >> share/upload.sh
echo "ld_dir_all ('./dumps/CID_PMID/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
echo "ld_dir_all ('./dumps/CID_PMID/', '*.trig', '');" >> share/upload.sh

echo "ld_dir_all ('./dumps/CID_PMID_endpoints/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
echo "ld_dir_all ('./dumps/CID_PMID_endpoints/', '*.trig', '');" >> share/upload.sh

echo "ld_dir_all ('./dumps/PubChem_Compound/CompoundFiltered/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
echo "ld_dir_all ('./dumps/PubChem_Compound/CompoundFiltered/', '*.trig', '');" >> share/upload.sh

echo "ld_dir_all ('./dumps/PubChem_References/PrimarySubjectTermFiltered/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
echo "ld_dir_all ('./dumps/PubChem_References/PrimarySubjectTermFiltered/', '*.trig', '');" >> share/upload.sh

echo "ld_dir_all ('./dumps/PubChem_References/referenceFiltered/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
echo "ld_dir_all ('./dumps/PubChem_References/referenceFiltered/', '*.trig', '');" >> share/upload.sh

echo "ld_dir_all ('./dumps/MeSH/', '*.ttl', 'http://database/ressources/');" >> share/upload.sh
echo "ld_dir_all ('./dumps/MeSH/', '*.trig', '');" >> share/upload.sh

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