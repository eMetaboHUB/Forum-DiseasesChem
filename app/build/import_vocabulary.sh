#!/bin/bash

usage () {
	echo "script usage: $(basename $0)"
	echo "-s path to the share directory where output vocabulary"
	echo "-f complete path to the archive on the ftp"
	echo "-u user"
	echo "-p password"
    echo "-l /path/to/logs/dir"
}

while getopts s:a:f:u:p: flag
	do
	    case "${flag}" in
			s) SHARE_DIR=${OPTARG};;
            f) FTP=${OPTARG};;
            u) USER=${OPTARG};;
            p) PASSWORD=${OPTARG};;
			?) usage; exit 1;;

	    esac
	done

echo "1) Get vocabulary and external data files from sftp ..."

# ARCHIVE_TAR_GZ=upload.tar.gz 
# URL="ftp.semantic-metabolomics.org:/upload.tar.gz"
# FTP="ftp.semantic-metabolomics.org:""
# ARCHIVE_TAR_GZ="../tmp/upload_2021.tar.gz"
# USER="forum"
# PASSWORD="Forum2021Cov!"
# TMP:

# Extract nalme of the archive from path in $FTP
ARCHIVE_TAR_GZ="$(basename -- $FTP)"

echo "URL: $FTP"

echo "sftp ${USER}@${FTP}"

if [[ ! -d ~/.ssh ]]; then
	mkdir ~/.ssh; chmod 0700 ~/.ssh
fi

ssh-keyscan -H ftp.semantic-metabolomics.org >> ~/.ssh/known_hosts
sshpass -p ${PASSWORD} sftp ${USER}@${FTP} ${SHARE_DIR}/ 
tar xvf ${SHARE_DIR}/${ARCHIVE_TAR_GZ} -C ${SHARE_DIR} --overwrite 
rm -rf ${SHARE_DIR}/${ARCHIVE_TAR_GZ}