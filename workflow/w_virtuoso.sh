#!/bin/bash

# necessite ./share/updload.sh

# USAGE (1) : ${0} start                  # start virtuoso and load data with script ./share/updload.sh
# USAGE (2) : ${0} stop                   # stop virtuoso                  
# USAGE (3) : ${0} clean                  # remove docker directory


while getopts d:s: flag;
	do
	    case "${flag}" in
	    d) DOCKER_DIR=${OPTARG};;
            s) PATH_TO_SHARED_DIR_FROM_D=${OPTARG};;
	    esac
	done

echo $DOCKER_DIR
echo $PATH_TO_SHARED_DIR_FROM_D

CMD=${@:$OPTIND:1}

echo $CMD

COMPOSE_PROJECT_NAME="metdisease"
LISTEN_PORT="9980"
PASSWORD="FORUM-Met-Disease-DB"
GRAPH="http://default#"
ALLOW_UDPATE="false"


function waitStarted() {
    set +e
    RES=1
    echo -n "Wait for start "
    until [ $RES -eq 0 ]; do
        echo -n "."
        sleep 1
        # As we check logs every 1 sec (sleep 1), we only check logs for the last 2 sec (--since 2s) to avoid grapping a "Server Online message" from a previous start
        docker logs --since 2s ${CONTAINER_NAME} 2>&1 | grep "Server online at 1111" > /dev/null
        RES=$?
    done
    echo ""
    set -e
}

function virtuosoControler() {
    echo " -- Virtuoso controler"
    echo " --"

    echo " -- Generating docker-compose"
    COMPOSE_FILE="${DOCKER_DIR}/docker-compose-${LISTEN_PORT}.yml"
    COMPOSE_CMD="docker-compose -p ${COMPOSE_PROJECT_NAME} -f ${COMPOSE_FILE}" # Ici Olivier faisait sudo -n docker-compose
    CONTAINER_NAME="${COMPOSE_PROJECT_NAME}_virtuoso_${LISTEN_PORT}"
    NETWORK_NAME="virtuoso_${LISTEN_PORT}_net"
    OUT_NETWORK_NAME="${COMPOSE_PROJECT_NAME}_${NETWORK_NAME}"
    RESOURCES_DIR="${DOCKER_DIR}/${PATH_TO_SHARED_DIR_FROM_D}"
    DATA="${DOCKER_DIR}/data/virtuoso"
    cat << EOF | tee ${COMPOSE_FILE} > /dev/null
version: '3.3'
services:
    virtuoso:
        image: tenforce/virtuoso
        container_name: ${CONTAINER_NAME}
        environment:
            VIRT_Parameters_NumberOfBuffers: 5450000   # See virtuoso/README.md to adapt value of this line
            VIRT_Parameters_MaxDirtyBuffers: 4000000    # See virtuoso/README.md to adapt value of this line
            VIRT_Parameters_MaxCheckpointRemap: 680000
            VIRT_Parameters_TN_MAX_memory: 2000000000
            VIRT_SPARQL_ResultSetMaxRows: 10000000000
            VIRT_SPARQL_MaxDataSourceSize: 10000000000
            VIRT_Flags_TN_MAX_memory: 2000000000
            VIRT_Parameters_StopCompilerWhenXOverRunTime: 1
            VIRT_SPARQL_MaxQueryCostEstimationTime: 0       # query time estimation
            VIRT_SPARQL_MaxQueryExecutionTime: 50000          # 5 min
            VIRT_Parameters_MaxMemPoolSize: 200000000
            VIRT_HTTPServer_EnableRequestTrap: 0
            VIRT_Parameters_ThreadCleanupInterval: 1
            VIRT_Parameters_ResourcesCleanupInterval: 1
            VIRT_Parameters_AsyncQueueMaxThreads: 1
            VIRT_Parameters_ThreadsPerQuery: 1
            VIRT_Parameters_AdjustVectorSize: 1
            VIRT_Parameters_MaxQueryMem: 2G
            DBA_PASSWORD: "${PASSWORD}"
            SPARQL_UPDATE: "${ALLOW_UDPATE}"
            DEFAULT_GRAPH: "${GRAPH}"
        volumes:
           - ${RESOURCES_DIR}:/usr/local/virtuoso-opensource/var/lib/virtuoso/db/dumps
           - ${DATA}:/data
        ports:
           - ${LISTEN_PORT}:8890
        networks:
           - ${NETWORK_NAME}

networks:
    ${NETWORK_NAME}:
EOF
    case $CMD in
        start)
            if [ -d ${DATA} ]; then
                echo " -- Already generated."
                echo " -- Start Container"
                ${COMPOSE_CMD} up -d
                waitStarted
            else
                echo " -- Generating new compose instance."             
                echo "---------------------------------" 

                echo " -- Pull Images"
                ${COMPOSE_CMD} pull
                echo " -- Start Container"
                ${COMPOSE_CMD} up -d
                waitStarted
                echo " -- Container started."
                echo " -- Load vocabulary."
		    docker exec \
                        ${CONTAINER_NAME} \
                        isql-v 1111 dba "${PASSWORD}" ./dumps/upload.sh
                echo " -- Load data."
                    docker exec \
                        ${CONTAINER_NAME} \
                        isql-v 1111 dba "${PASSWORD}" ./dumps/pre_upload.sh
                echo " -- Load ClassyFire."
                    docker exec \
                            ${CONTAINER_NAME} \
                            isql-v 1111 dba "${PASSWORD}" ./dumps/upload_ClassyFire.sh
            fi
        ;;
        stop)
            ${COMPOSE_CMD} stop
        ;;
        clean)
            if [ -d ${DATA} ]; then
		${COMPOSE_CMD} down
                set +e
                docker run --rm \
                    --mount type=bind,source="${DOCKER_DIR}",target=/cache \
                    tenforce/virtuoso \
                    bash -c "rm -r /cache/data"
                set -e
            else
                echo " -- Instance not present. Skipping cleaning."
            fi
        ;;
        *)
            rm ${COMPOSE_FILE}
            echo "Error: unsupported command $CMD"
            exit 1
        ;;
    esac
    exit 0
}

virtuosoControler
