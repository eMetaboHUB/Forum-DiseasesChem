#!/bin/bash


BASEDIR=$(dirname $0)
LOGSDIR=./logs-app

mkdir -p $LOGSDIR

# -b: path to the config file of build_rdf_store
# -v: la version de l'analyse CID/CHEBI/CHEMONT to mesh
# -p: pydio pwd
# -d: le chemin vers le répertoire où écrire les données (eg. ./data)
# -s: le chemin vers le répertoire de partage de Virtuoso où écrire les triplets (eg/ ./docker-virtuoso/share)

while getopts b:v:p:d:s: flag
	do
	    case "${flag}" in
            b) CONFIG_BUILD_RDF_STORE=${OPTARG};;
            v) VERSION=${OPTARG:-};;
            p) PYDIO_PASSWD=${OPTARG};;
			d) DATA=${OPTARG};;
			s) RESOURCES_DIR=${OPTARG};;
	    esac
	done

echo "--  Create triple store !"
echo "1) Get vocabulary and external data files from pydio ..."

ARCHIVE_TAR_GZ_PYDIO=upload.tar.gz 
URL_PYDIO_TTL="https://pfem.clermont.inra.fr/pydio/public/7af464/dl/"
OPTION_PYDIO_INRAE="-u none:$PYDIO_PASSWD"

# Init log
LOG_VOC="${LOGSDIR}/get_pydio.log"
echo "" > $LOG_VOC

echo "wget --user none --password ${PYDIO_PASSWD} ${URL_PYDIO_TTL}${ARCHIVE_TAR_GZ_PYDIO} -P ${RESOURCES_DIR}/"
wget --user none --password ${PYDIO_PASSWD} -P ${RESOURCES_DIR}/ ${URL_PYDIO_TTL}${ARCHIVE_TAR_GZ_PYDIO} 2>&1 | tee -a $LOG_VOC
tar xvf ${RESOURCES_DIR}/${ARCHIVE_TAR_GZ_PYDIO} -C ${RESOURCES_DIR} --overwrite 2>&1 | tee -a $LOG_VOC
rm -rf ${RESOURCES_DIR}/${ARCHIVE_TAR_GZ_PYDIO} 2>&1 | tee -a $LOG_VOC

echo "2) Build rdf store"

# Init logs
LOG_RDF="${LOGSDIR}/build_rdf_store.log"
echo "" > $LOG_RDF

python3 app/build_RDF_store/build_RDF_store.py --config=$CONFIG_BUILD_RDF_STORE --out=$RESOURCES_DIR --log=$DATA --version=$VERSION 2>&1 | tee -a $LOG_RDF