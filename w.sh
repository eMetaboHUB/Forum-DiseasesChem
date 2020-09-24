#!/bin/bash

basedir=$(dirname $0)

pushd $BASEDIR

# download/build rdf resources 
./w1_build_rdf_store.sh
# download rdf resources 
./w1_2_pydio_files.sh F0rum_p455w0rd
# start and load virtuoso with rdf data in the "share" directory
./w2_virtuoso.sh start

popd
