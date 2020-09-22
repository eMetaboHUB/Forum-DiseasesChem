#!/bin/bash

# necessite ./share/updload.sh

# USAGE (1) : ${0} start                  # start virtuoso and load data with script ./share/updload.sh
# USAGE (2) : ${0} stop                   # stop virtuoso                  
# USAGE (3) : ${0} clean                  # remove docker directory


if [ "$#" -ne  "1" ]
then
     echo "what to do (start | stop | clean)"
     exit
fi

CMD=$1

RESOURCES_DIR=./share/
UPDATA_FILE=update.sh


COMPOSE_PROJECT_NAME="metdisease"
LISTEN_PORT="9980"
PASSWORD="FORUM-Met-Disease-DB"
GRAPH="http://default#"
ALLOW_UDPATE="true"


function waitStarted() {
    set +e
    RES=1
    echo -n "Wait for start "
    until [ $RES -eq 0 ]; do
        echo -n "."
        sleep 1
        docker logs ${CONTAINER_NAME} 2>&1 | grep "Server online at 1111" > /dev/null
        RES=$?
    done
    echo ""
    set -e
}

function virtuosoControler() {
    echo " -- Virtuoso controler"
    echo " --"

    echo " -- Generating docker-compose"
    COMPOSE_FILE=docker-compose-${LISTEN_PORT}.yml
    COMPOSE_CMD="docker-compose -p ${COMPOSE_PROJECT_NAME} -f ${COMPOSE_FILE}"
    CONTAINER_NAME="${COMPOSE_PROJECT_NAME}_virtuoso_${LISTEN_PORT}"
    NETWORK_NAME="virtuoso_${LISTEN_PORT}_net"
    OUT_NETWORK_NAME="${COMPOSE_PROJECT_NAME}_${NETWORK_NAME}"
    DATA=$(realpath ${CONTAINER_NAME}_data)
    cat << EOF | tee ${COMPOSE_FILE} > /dev/null
version: '3.3'
services:
    virtuoso:
        image: tenforce/virtuoso
        container_name: ${CONTAINER_NAME}
        environment:
            VIRT_Parameters_NumberOfBuffers: 27200   # See virtuoso/README.md to adapt value of this line
            VIRT_Parameters_MaxDirtyBuffers: 20000    # See virtuoso/README.md to adapt value of this line
            VIRT_Parameters_MaxCheckpointRemap: 6800
            VIRT_Parameters_TN_MAX_memory: 20000000
            VIRT_SPARQL_ResultSetMaxRows: 100000000
            VIRT_SPARQL_MaxDataSourceSize: 100000000
            VIRT_Flags_TN_MAX_memory: 20000000
            VIRT_Parameters_StopCompilerWhenXOverRunTime: 1
            VIRT_SPARQL_MaxQueryCostEstimationTime: 0       # query time estimation
            VIRT_SPARQL_MaxQueryExecutionTime: 500          # 5 min
            VIRT_Parameters_MaxMemPoolSize: 2000000
            VIRT_HTTPServer_EnableRequestTrap: 0
            VIRT_Parameters_ThreadCleanupInterval: 1
            VIRT_Parameters_ResourcesCleanupInterval: 1
            VIRT_Parameters_AsyncQueueMaxThreads: 1
            VIRT_Parameters_ThreadsPerQuery: 1
            VIRT_Parameters_AdjustVectorSize: 1
            VIRT_Parameters_MaxQueryMem: 2G
            VIRT_Database_LockFile: virtuoso.lck
            DBA_PASSWORD: "${PASSWORD}"
            SPARQL_UPDATE: "${ALLOW_UDPATE}"
            DEFAULT_GRAPH: "${GRAPH}"
        volumes:
           - ./share:/usr/local/virtuoso-opensource/var/lib/virtuoso/db/dumps
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
                echo "$(ls)"

                echo " -- Pull Images"
                ${COMPOSE_CMD} pull
                echo " -- Start Container"
                ${COMPOSE_CMD} up -d
                waitStarted
                echo " -- Container started."
				
				docker exec \
                        ${CONTAINER_NAME} \
                        isql-v 1111 dba "${PASSWORD}" ./dumps/${UPDATA_FILE}
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
                    --mount type=bind,source="${DATA}",target=/data \
                    tenforce/virtuoso \
                    bash -c "rm -rf /tmp/data /usr/local/virtuoso-opensource/share/virtuoso/vad/dumps/"
                set -e
                rm -rf "${DATA}"
                rm -rf "${DATA}_dumps"
				rm -rf ${RESOURCES_DIR}
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
    rm ${COMPOSE_FILE}
    exit 0
}

virtuosoControler