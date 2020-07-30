#!/bin/bash


dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')

sleep 10

docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/upload_data.sh'
