#!/bin/bash

# download/build rdf resources 
./w1_build_rdf_store.sh
# start and load virtuoso with rdf data in the "share" directory
./w2_virtuoso.sh start F0rum_p455w0rd
