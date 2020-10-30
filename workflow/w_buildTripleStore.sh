#!/bin/bash


BASEDIR=$(dirname $0)
LOGSDIR=./logs-app

mkdir -p $LOGSDIR

# -v: la version de l'analyse CID/CHEBI/CHEMONT to mesh
# -u: le nom de la ressource créée par l'analyse (eg. CID_MESH ou CHEBI_MESH)
# -d: le chemin vers le répertoire où écrire les données (eg. ./data)
# -s: le chemin vers le répertoire de partage de Virtuoso où écrire les triplets (eg/ ./docker-virtuoso/share)

# Init logs
echo "" > $LOGSDIR/post_processes.log

while getopts v:p:d:s: flag
	do
	    case "${flag}" in
	        v) VERSION=${OPTARG};;
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

echo $RESOURCES_DIR
echo "wget --user none --password ${PYDIO_PASSWD} ${URL_PYDIO_TTL}${ARCHIVE_TAR_GZ_PYDIO} -P ${RESOURCES_DIR}/"
wget --user none --password ${PYDIO_PASSWD} -P ${RESOURCES_DIR}/ ${URL_PYDIO_TTL}${ARCHIVE_TAR_GZ_PYDIO} 
tar xvf ${RESOURCES_DIR}/${ARCHIVE_TAR_GZ_PYDIO} -C ${RESOURCES_DIR}
rm -rf ${RESOURCES_DIR}/${ARCHIVE_TAR_GZ_PYDIO}

