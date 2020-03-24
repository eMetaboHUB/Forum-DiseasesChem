#!/bin/bash

# Starting with just one file

docker-compose up -d

# upload data
echo "DELETE FROM DB.DBA.RDF_QUAD ;" >./share/upload.sh
echo "ld_dir_all ('./dumps/CID_PMID/', '*.ttl', 'http://database/ressources/');" >> ./share/upload.sh
echo "rdf_loader_run();" >> ./share/upload.sh
echo "checkpoint;" >> ./share/upload.sh

dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "myDBTest" ./dumps/upload.sh'

echo "MetDisease database endpoint : http://localhost:9999/sparql"