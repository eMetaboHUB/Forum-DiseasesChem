#!/bin/bash


BASEDIR=$(dirname $0)


usage () {
	echo "script usage: $(basename $0)"
    echo "-a path/to/SBML"
	echo "-b SBML version"
    echo "-c path/to/the/global/config/file"
    echo "-d MetaNetX version"
    echo "-e PubChem version"
	echo "-s /path/to/docker-virtuoso/share/dir"
	echo "-l /path/to/logs/dir"
}

VERSION=""

while getopts a:b:c:d:e:s:l: flag
	do
	    case "${flag}" in
            a) SBML_PATH=${OPTARG};;
            b) SBML_VERSION=${OPTARG};;
			c) CONFIG=${OPTARG};;
            d) METANETX_VERSION=${OPTARG};;
            e) PUBCHEM_VERSION=${OPTARG};;
			s) RESOURCES_DIR=${OPTARG};;
			l) LOGSDIR=${OPTARG};;
			?) usage; exit 1;;
	    esac
	done

if [ -z "$SBML_PATH" ] || [ -z "$SBML_VERSION" ] || [ -z "$CONFIG" ] || [ -z "$METANETX_VERSION" ]  || [ -z "$PUBCHEM_VERSION" ]  || [ -z "$RESOURCES_DIR" ] || [ -z "$LOGSDIR" ]
then
	echo "One (or few) mandatory options seem missing. Mandatory options are: -a -b -c -d -e -s -l" ;
	usage ;
	exit 1 ;
fi

mkdir -p $LOGSDIR

echo "1) Import SBML"

# Init logs
LOG_SBML="${LOGSDIR}/load_SBML.log"
echo "" > $LOG_SBML

python3 app/SBML_upgrade/import_SBML.py --config=$CONFIG --out=$RESOURCES_DIR --sbml=$SBML_PATH --version=$SBML_VERSION 2>&1 | tee -a $LOG_SBML

echo "2) Import PubChem mapping"

# Init logs
LOG_PUBCHEM="${LOGSDIR}/load_PubChem_mapping.log"
echo "" > $LOG_PUBCHEM

# python3 app/SBML_upgrade/import_PubChem_mapping.py --config=$CONFIG --out=$RESOURCES_DIR --version=$PUBCHEM_VERSION 2>&1 | tee -a $LOG_PUBCHEM


echo "3) Import MetaNetX mapping"

# Init logs
LOG_METANETX="${LOGSDIR}/load_MetaNetX_mapping.log"
echo "" > $LOG_METANETX

# python3 app/SBML_upgrade/import_MetaNetX_mapping.py --config=$CONFIG --out=$RESOURCES_DIR --version=$METANETX_VERSION 2>&1 | tee -a $LOG_METANETX

echo "End !"