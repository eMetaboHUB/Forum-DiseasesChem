#!/bin/bash

# get script current dir
BASEDIR=$(dirname $0)

# go to the directory where this script is
pushd $BASEDIR
    #clean directory
    ./w2_virtuoso.sh clean
    # download/build rdf resources 
    ./w1_build_rdf_store.sh
    # download rdf resources 
    ./w1_2_pydio_files.sh $1
    # start and load virtuoso with rdf data in the "share" directory
    ./w2_virtuoso.sh start
    # test database if fill and ok

    #chemOnt 
    #./w4_fetch_ChemOnt.sh

popd

# remove old pid file
nohup_pid="/tmp/deploy_endpoint.pid";
if test -f "$nohup_pid"; then
    echo "[info] remove PID file";
    test -f $nohup_pid && rm $nohup_pid;
fi
