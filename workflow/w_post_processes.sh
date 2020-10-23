#!/bin/bash

BASEDIR=$(dirname $0)
LOGSDIR=./logs-app
RESOURCES_DIR=./share
DATA=./data

mkdir -p $LOGSDIR

# Init logs
echo "" > $LOGSDIR/post_processes.log

while getopts v: flag
	do
	    case "${flag}" in
	        v) VERSION=${OPTARG};;
	    esac
	done

# Compute fisher exact tests
echo " - compute fisher exact tests"

IN_F="${DATA}/metab2mesh/CID_MESH/${VERSION}/results/test.csv"
OUT_F="${DATA}/metab2mesh/CID_MESH/${VERSION}/r_fisher.csv"

Rscript app/metab2mesh/post-processes/compute_fisher_exact_test_V2.R --file=$IN_F --chunksize=1000 --parallel=5 --p_out=$OUT_F 2>&1 | tee -a $LOGSDIR/post_processes.log
# Compute post-processes (eg. q.value)
echo " - Compute benjamini and Holchberg procedure"

IN_Q=$OUT_F
OUT_Q="${DATA}/metab2mesh/CID_MESH/${VERSION}/r_fisher_q.csv"

Rscript app/metab2mesh/post-processes/post_process_metab2mesh.R --p_metab2mesh=$IN_Q --p_out=$OUT_Q 2>&1 | tee -a $LOGSDIR/post_processes.log

# Compute weakness test
echo " - Compute weakness tests"

IN_W=$OUT_Q
OUT_W="${DATA}/metab2mesh/CID_MESH/${VERSION}/r_fisher_q_w.csv"
Rscript app/metab2mesh/post-processes/weakness/weakness_test.R --file=$IN_W --threshold=1e-6 --alphaCI=0.05 --chunksize=1000 --parallel=5 --p_out=$OUT_W 2>&1 | tee -a $LOGSDIR/post_processes.log

# Upload step - Skip for now
#TODO
FTP="ftp://data/anayse/version"

# Create triples

echo " - Convert significant relations to triples"

IN_T=$OUT_W

python3 app/Analyzes/Enrichment_to_graph/convert_association_table_to_triples.py --config="app/Analyzes/Enrichment_to_graph/config/CID_MESH/2020-07-07/config.ini" --input=$IN_T --uri=$FTP --version=$VERSION