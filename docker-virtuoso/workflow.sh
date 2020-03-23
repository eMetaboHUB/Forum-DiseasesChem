#!/bin/bash
# author : olivier.filangi@askelys.com
# author2: maxime.delmas@inrae.fr

# Starting with just one file

docker-compose up -d

date=$(date '+%d/%m/%Y')

# upload data
echo "DELETE FROM DB.DBA.RDF_QUAD ;" >./share/upload.sh
echo "ld_dir_all ('./dumps/.','.*.ttl ','http://database/ressources/$date/');">>./share/upload.sh
echo "rdf_loader_run();" >>./share/upload.sh


dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "myDBTest" ./dumps/upload.sh'

echo "MetDisease database endpoint : http://localhost:9999/sparql"