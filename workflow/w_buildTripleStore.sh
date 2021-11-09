#!/bin/bash


BASEDIR=$(dirname $0)

# Test: bash workflow/w_buildTripleStore.sh -b app/build_RDF_store/config/config.ini -c app/ChemOnt/config/2020-08-14/config.ini -p F0rum_p455w0rd -s ./share-virtuoso

# -b: path to the config file of build_rdf_store
# -v: la version de l'analyse CID/CHEBI/CHEMONT to mesh
# -p: pydio pwd
# -s: le chemin vers le répertoire de partage de Virtuoso où écrire les triplets (eg/ ./docker-virtuoso/share)

usage () {
	echo "script usage: $(basename $0)"
	echo "-b path/to/buid_rdf_store/config"
	echo "-c /path/to/Chemont/config"
	echo "-v version (optional, date as default value)"
	echo "-s /path/to/docker-virtuoso/share/dir"
	echo "-l /path/to/logs/dir"
}

VERSION=""

while getopts b:c:v:p:s:l: flag
	do
	    case "${flag}" in
            b) CONFIG_BUILD_RDF_STORE=${OPTARG};;
			c) CONFIG_CHEMONT=${OPTARG};;
            v) VERSION=${OPTARG};;
			s) RESOURCES_DIR=${OPTARG};;
			l) LOGSDIR=${OPTARG};;
			?) usage; exit 1;;

	    esac
	done

if [ -z "$RESOURCES_DIR" ] || [ -z "$LOGSDIR" ]
then
	echo "One (or few) mandatory options seem missing. Mandatory options are: -s -l" ;
	usage ;
	exit 1 ;
fi

mkdir -p $LOGSDIR

echo "--  Create triple store !"
echo "1) Get vocabulary and external data files from sftp ..."

# ARCHIVE_TAR_GZ=upload.tar.gz 
# URL_SFTP="ftp.semantic-metabolomics.org:/upload.tar.gz"

# TMP:
ARCHIVE_TAR_GZ=upload_2021.tar.gz
URL_SFTP="ftp.semantic-metabolomics.org:../tmp/upload_2021.tar.gz"
USER="forum"
PASSWORD="Forum2021Cov!"

# Init log
LOG_VOC="${LOGSDIR}/get_voc.log"
echo "" > $LOG_VOC

echo "sftp ${USER}@${URL_SFTP}"
if [[ ! -d ~/.ssh ]]
then
	mkdir ~/.ssh; chmod 0700 ~/.ssh
fi
ssh-keyscan -H ftp.semantic-metabolomics.org >> ~/.ssh/known_hosts
sshpass -p ${PASSWORD} sftp ${USER}@${URL_SFTP} ${RESOURCES_DIR}/ 2>&1 | tee -a $LOG_VOC
tar xvf ${RESOURCES_DIR}/${ARCHIVE_TAR_GZ} -C ${RESOURCES_DIR} --overwrite 2>&1 | tee -a $LOG_VOC
rm -rf ${RESOURCES_DIR}/${ARCHIVE_TAR_GZ} 2>&1 | tee -a $LOG_VOC

if [ -n "$CONFIG_BUILD_RDF_STORE" ] 
then

echo "2) Build rdf store"

# Init logs
LOG_RDF="${LOGSDIR}/build_rdf_store.log"
echo "" > $LOG_RDF

python3 -u app/build_RDF_store/build_RDF_store.py --config=$CONFIG_BUILD_RDF_STORE --out=$RESOURCES_DIR --log=$LOGSDIR --version=$VERSION 2>&1 | tee -a $LOG_RDF

fi

if [ -n "$CONFIG_CHEMONT" ]
then

echo "3) Create Chemont ressource"

# Init logs
LOG_CHEMONT="${LOGSDIR}/chemont.log"
echo "" > $LOG_CHEMONT

python3 -u app/ChemOnt/fetch_ChemOnt.py --config=$CONFIG_CHEMONT --out=$RESOURCES_DIR --log=$LOGSDIR --version=$VERSION 2>&1 | tee -a $LOG_CHEMONT

fi