#!/bin/bash

LOGSDIR=./logs-app
RESOURCES_DIR=./share

function runBuild() {

CONTAINER_NAME=metdisease_app

mkdir -p ${RESOURCES_DIR} ${LOGSDIR} ./data_tmp

COMPOSE_FILE=docker-compose-app-chemont.yml

cat << EOF | tee ${COMPOSE_FILE} > /dev/null
version: '3.3'
services:
    metdisease:
        build: .
        container_name: ${CONTAINER_NAME}
        volumes:
           - ${RESOURCES_DIR}:/workdir/share-virtuoso/
           - ${LOGSDIR}:/workdir/out/
        command: python3 app/ChemOnt/fetch_ChemOnt.py --config="app/ChemOnt/config/2020-08-14/config.ini"
EOF

sudo -n docker-compose -f ${COMPOSE_FILE} build
sudo -n docker-compose -f ${COMPOSE_FILE} up
rm -rf ${COMPOSE_FILE}
}

runBuild
