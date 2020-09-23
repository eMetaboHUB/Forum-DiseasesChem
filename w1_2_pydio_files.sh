#!/bin/bash

if [ "$#" -ne  "2" ]
then
     echo "1. pydio passwd - https://pfem.clermont.inra.fr/pydio/ - "
	 exit
fi

if ! command -v jq &> /dev/null
then
    echo "jq could not be found"
    exit
fi

PYDIO_PASSWD=$1

RESOURCES_DIR=share
ARCHIVE_TAR_GZ_PYDIO=upload.tar.gz 
URL_PYDIO_TTL="https://pfem.clermont.inra.fr/pydio/public/7af464/dl/"
OPTION_PYDIO_INRAE="-u none:$PYDIO_PASSWD"

function download_resources() {
    echo " -- Download resources."

    # download files 
	
	[ ! -d ${RESOURCES_DIR} ] && mkdir -p ${RESOURCES_DIR}
	echo "wget --user none --password ${PYDIO_PASSWD} ${URL_PYDIO_TTL}/upload.tar.gz -P ${RESOURCES_DIR}/"
	wget --user none --password ${PYDIO_PASSWD} ${URL_PYDIO_TTL}/${ARCHIVE_TAR_GZ_PYDIO} -P ${RESOURCES_DIR}/
	tar xvf ${RESOURCES_DIR}/${ARCHIVE_TAR_GZ_PYDIO} -C ${RESOURCES_DIR}
	rm -rf ${RESOURCES_DIR}/${ARCHIVE_TAR_GZ_PYDIO}
}


download_resources

