#!/bin/bash

# bash workflow/w_upload_metabolic_network.sh -a data/OtherGEM/ecol/rdf/e_coli_core.ttl -b ecol/v2 -c app/SBML_upgrade/config/config_ecol.ini -d 4.1 -e 2020-12-03 -s docker-virtuoso/share -l logs

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

while getopts a:b:u:c:d:e:s:l: flag
	do
	    case "${flag}" in
            a) SBML_PATH=${OPTARG};;
            b) SBML_VERSION=${OPTARG};;
			u) SBML_URI=${OPTARG};;
			c) CONFIG=${OPTARG};;
            d) METANETX_VERSION=${OPTARG};;
            e) PUBCHEM_VERSION=${OPTARG};;
			s) RESOURCES_DIR=${OPTARG};;
			l) LOGSDIR=${OPTARG};;
			?) usage; exit 1;;
	    esac
	done

if [ -z "$SBML_PATH" ] || [ -z "$SBML_VERSION" ] || [ -z "$SBML_URI" ] || [ -z "$CONFIG" ] || [ -z "$METANETX_VERSION" ]  || [ -z "$PUBCHEM_VERSION" ]  || [ -z "$RESOURCES_DIR" ] || [ -z "$LOGSDIR" ]
then
	echo "One (or few) mandatory options seem missing. Mandatory options are: -a -b -c -d -e -s -l" ;
	usage ;
	exit 1 ;
fi

mkdir -p $LOGSDIR

echo "1) SBML to RDF"
LOG_SBML2RDF="${LOGSDIR}/SBML2RDF.log"
echo "" > $LOG_SBML2RDF
BASENAME_SBML="$(basename -- $SBML_PATH)"
F_SBML="${BASENAME_SBML%.*}"
OUT_DIR_SBML="$RESOURCES_DIR/GEM/$SBML_VERSION"

mkdir -p $OUT_DIR_SBML

OUT_SBML="$OUT_DIR_SBML/$F_SBML.ttl"

java -jar ../sbml2rdf/SBML2RDF.jar -i $SBML_PATH -o $OUT_SBML -u $SBML_URI

echo "2) Import SBML"

# Init logs
LOG_SBML="${LOGSDIR}/load_SBML.log"
echo "" > $LOG_SBML

python3 app/SBML_upgrade/import_SBML.py --config=$CONFIG --out=$RESOURCES_DIR --sbml=$OUT_SBML --version=$SBML_VERSION 2>&1 | tee -a $LOG_SBML

echo "3) Import PubChem mapping"

# Init logs
LOG_PUBCHEM="${LOGSDIR}/load_PubChem_mapping.log"
echo "" > $LOG_PUBCHEM

python3 app/SBML_upgrade/import_PubChem_mapping.py --config=$CONFIG --out=$RESOURCES_DIR --version=$PUBCHEM_VERSION 2>&1 | tee -a $LOG_PUBCHEM


echo "4) Import MetaNetX mapping"

# Init logs
LOG_METANETX="${LOGSDIR}/load_MetaNetX_mapping.log"
echo "" > $LOG_METANETX

python3 app/SBML_upgrade/import_MetaNetX_mapping.py --config=$CONFIG --out=$RESOURCES_DIR --version=$METANETX_VERSION 2>&1 | tee -a $LOG_METANETX

echo "End !"