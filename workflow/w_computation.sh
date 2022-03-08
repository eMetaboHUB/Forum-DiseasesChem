#!/bin/bash

BASEDIR=$(dirname $0)

#EG. bash workflow/w_computation.sh -v test -m app/computation/config/CHEBI_MESH_Thesaurus_Onto/test/config.ini -t app/Analyzes/Enrichment_to_graph/config/CHEBI_MESH/2020-07-10/config.ini -u CHEBI_MESH -d ./data -s ./docker-virtuoso/share

# -v: la version de l'analyse CID/CHEBI/CHEMONT to mesh
# -m: le chemin vers le fichier de configuration de l'analyse compound2mesh (eg. app/computation/config/CID_MESH_Thesaurus/test/config.ini)
# -t: le chemin vers le fichier de configuration du processus association-to-triples (eg. app/Analyzes/Enrichment_to_graph/config/CID_MESH/2020-07-07/config.ini)
# -u: le nom de la ressource créée par l'analyse (eg. CID_MESH ou CHEBI_MESH)
# -d: le chemin vers le répertoire où écrire les données (eg. ./data)
# -s: le chemin vers le répertoire de partage de Virtuoso où écrire les triplets (eg/ ./docker-virtuoso/share)

usage () {
	echo "script usage: $(basename $0)" 
	echo "-v version (optional, date as default value)"
	echo "-m /path/to/config/compound2mesh"
	echo "-t /path/to/config/EnrichmentAnalysis"
	echo "-u ressource name"
	echo "-d /path/data/dir"
	echo "-s /path/to/docker-virtuoso/share/dir"
	echo "-l /path/to/logs/dir"
	echo "-c chunksize for parsing files (optional, default 100000)"
	echo "-p number of used cores (optional, default 5)"
	echo "-o threshold used in fragility index (optional, default 1e-6)"
	echo "-i alpha of Jeffrey's CI for fragility index computation (optional, default 0.05)"
}

VERSION=$(date +"%Y-%m-%d")
CHUNKSIZE=100000
PARALLEL=5
THRESHOLD=1e-6
ALPHACI=0.05

while getopts v:m:t:u:d:s:l:c:p:o:i: flag
	do
	    case "${flag}" in
	        v) VERSION=${OPTARG};;
            m) CONFIG_COMPOUND2MESH=${OPTARG};;
            t) CONFIG_COMPOUND2MESH_TRIPLES=${OPTARG};;
			u) RESSOURCE_NAME=${OPTARG};;
			d) DATA=${OPTARG};;
			s) RESOURCES_DIR=${OPTARG};;
			l) LOGSDIR=${OPTARG};;
			c) CHUNKSIZE=${OPTARG};;
			p) PARALLEL=${OPTARG};;
			o) THRESHOLD=${OPTARG};;
			i) ALPHACI=${OPTARG};;
			?) usage; exit 1;;


	    esac
	done

if [ -z "$CONFIG_COMPOUND2MESH" ] || [ -z "$CONFIG_COMPOUND2MESH_TRIPLES" ] || [ -z "$RESSOURCE_NAME" ] || [ -z "$DATA" ] || [ -z "$RESOURCES_DIR" ] || [ -z "$LOGSDIR" ]
then
	echo "One (or few) mandatory options seem missing. Mandatory options are: -m -t -u -d -s -l" ;
	usage ;
	exit 1 ;
fi

mkdir -p $LOGSDIR

# Init logs
LOG="${LOGSDIR}/processes_${RESSOURCE_NAME}.log"

echo "" > $LOG

# Compute fisher exact tests
echo " - compute associations"

OUT_M="${DATA}/computation/${RESSOURCE_NAME}/${VERSION}/"

python3 -u app/computation/requesting_virtuoso.py --config=$CONFIG_COMPOUND2MESH --out=$OUT_M 2>&1 | tee -a $LOG

echo " - compute fisher exact tests"

IN_F="${DATA}/computation/${RESSOURCE_NAME}/${VERSION}/results/associations.csv"
OUT_F="${DATA}/computation/${RESSOURCE_NAME}/${VERSION}/r_fisher.csv"

Rscript app/computation/post-processes/compute_fisher_exact_test.R --file=$IN_F --chunksize=$CHUNKSIZE --parallel=$PARALLEL --p_out=$OUT_F 2>&1 | tee -a $LOG

# Compute post-processes (eg. q.value)
echo " - Compute benjamini and Holchberg procedure"

IN_Q=$OUT_F
OUT_Q="${DATA}/computation/${RESSOURCE_NAME}/${VERSION}/r_fisher_q.csv"

Rscript app/computation/post-processes/post_process.R --p_associations=$IN_Q --p_out=$OUT_Q 2>&1 | tee -a $LOG

# Compute weakness test
echo " - Compute weakness tests"

IN_W=$OUT_Q
OUT_W="${DATA}/computation/${RESSOURCE_NAME}/${VERSION}/r_fisher_q_w.csv"
Rscript app/computation/post-processes/weakness/weakness_test.R --file=$IN_W --threshold=$THRESHOLD --alphaCI=$ALPHACI --chunksize=$CHUNKSIZE --parallel=$PARALLEL --p_out=$OUT_W 2>&1 | tee -a $LOG

# Upload step: Aboard
# FTP="ftp://data/anayse/version"
# --uri=$FTP
# Create triples

echo " - Convert significant relations to triples"

IN_T=$OUT_W

python3 -u app/build/convert_association_table_to_triples.py --config=$CONFIG_COMPOUND2MESH_TRIPLES --c2mconfig=$CONFIG_COMPOUND2MESH --c2mname=$RESSOURCE_NAME --input=$IN_T --version=$VERSION --out=$RESOURCES_DIR 2>&1 | tee -a $LOG