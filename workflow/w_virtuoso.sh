#!/bin/bash
set -e
# necessite ./share/updload.sh

# USAGE (1) : ${0} start                  # start virtuoso and load data with script ./share/updload.sh
# USAGE (2) : ${0} stop                   # stop virtuoso                  
# USAGE (3) : ${0} clean                  # remove docker directory

# By default we use only load essential data: MeSH, PubChem_Reference, PubChem_Compound, PMID_CID, PMID_CID_endpoints

while getopts d:s:c: flag;
	do
	    case "${flag}" in
	        d) DOCKER_DIR=${OPTARG};;
            s) PATH_TO_SHARED_DIR_FROM_D=${OPTARG};;
            c) CMD=${OPTARG};;
	    esac
	done

if [ "$CMD" != "start" ] && [ "$CMD" != "stop" ] && [ "$CMD" != "clean" ]; then
    echo "-c (command) must be 'start' or 'stop' or 'clean'"
    exit 1
fi

shift $(($OPTIND - 1))
uploads="$@"

COMPOSE_PROJECT_NAME="forum-KG"
LISTEN_PORT="9980"
PASSWORD="FORUM"
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

function memInGb() {
    grep MemTotal /proc/meminfo | awk '{print $2}' | xargs -I {} echo "scale=4; {}/1024^2" | bc
}

# doc : https://docs.openlinksw.com/virtuoso/rdfperfgeneral/ 

function getNumberOfBuffer() {
    memInGb=$(memInGb)
    
    case 1 in
        $(echo "$memInGb < 2" | bc -l)) echo "getNumberOfBuffer - not enough memory - MemTotal(/proc/meminfo) : $memInGb"; exit 1;;
        $(echo "$memInGb < 4" | bc -l)) echo "170000";;
        $(echo "$memInGb < 8" | bc -l)) echo "340000";;
        $(echo "$memInGb < 16" | bc -l)) echo "680000";;
        $(echo "$memInGb < 32" | bc -l)) echo "1360000";;
        $(echo "$memInGb < 48" | bc -l)) echo "2720000";;
        $(echo "$memInGb < 64" | bc -l)) echo "4000000";;
                                      *) echo "5450000";;
    esac
}

function getMaxDirtyBuffers() {
    memInGb=$(memInGb)
    
    case 1 in
        $(echo "$memInGb < 2" | bc -l)) echo "getMaxDirtyBuffers - not enough memory - MemTotal(/proc/meminfo) : $memInGb"; exit 1;;
        $(echo "$memInGb < 4" | bc -l)) echo "130000";;
        $(echo "$memInGb < 8" | bc -l)) echo "250000";;
        $(echo "$memInGb < 16" | bc -l)) echo "500000";;
        $(echo "$memInGb < 32" | bc -l)) echo "1000000";;
        $(echo "$memInGb < 48" | bc -l)) echo "2000000";;
        $(echo "$memInGb < 64" | bc -l)) echo "3000000";;
                                      *) echo "4000000";;
    esac
}

function getMaxQueryMem() {
    memInGb=$(memInGb)
    
    case 1 in
        $(echo "$memInGb < 2" | bc -l)) echo "getMaxDirtyBuffers - not enough memory - MemTotal(/proc/meminfo) : $memInGb"; exit 1;;
        $(echo "$memInGb < 4" | bc -l)) echo "2";;
        $(echo "$memInGb < 16" | bc -l)) echo "4";;
        $(echo "$memInGb < 48" | bc -l)) echo "6";;
                                      *) echo "8";;
    esac
}

function virtuosoControler() {
    echo " -- Virtuoso controler"
    
    memInGb=$(memInGb)
    vgetNumberOfBuffer=$(getNumberOfBuffer)
    vgetMaxDirtyBuffers=$(getMaxDirtyBuffers)
    vMaxQueryMem=$(getMaxQueryMem)

    echo " ********************************************************************************"
    echo "       Total Memory in Gb = $memInGb"
    echo "       vgetNumberOfBuffer = $vgetNumberOfBuffer    "
    echo "       vgetMaxDirtyBuffers = $vgetMaxDirtyBuffers  "
    echo "       vMaxQueryMem = $vMaxQueryMem "
    echo " ********************************************************************************"
    echo " -- Generating docker-compose"
    COMPOSE_FILE="${DOCKER_DIR}/docker-compose-${LISTEN_PORT}.yml"
    COMPOSE_CMD="docker compose -p ${COMPOSE_PROJECT_NAME} -f ${COMPOSE_FILE}" # Ici Olivier faisait sudo -n docker-compose
    CONTAINER_NAME="${COMPOSE_PROJECT_NAME}_virtuoso_${LISTEN_PORT}"
    NETWORK_NAME="virtuoso_${LISTEN_PORT}_net"
    OUT_NETWORK_NAME="${COMPOSE_PROJECT_NAME}_${NETWORK_NAME}"
    RESOURCES_DIR="${PATH_TO_SHARED_DIR_FROM_D}"
    DATA="${DOCKER_DIR}/data/virtuoso"
    cat << EOF | tee ${COMPOSE_FILE} > /dev/null
version: '3.3'
services:
    virtuoso:
        image: tenforce/virtuoso
        container_name: ${CONTAINER_NAME}
        environment:
            VIRT_Parameters_NumberOfBuffers: ${vgetNumberOfBuffer}   # See virtuoso/README.md to adapt value of this line
            VIRT_Parameters_MaxDirtyBuffers: ${vgetMaxDirtyBuffers}    # See virtuoso/README.md to adapt value of this line
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
            VIRT_Parameters_VectorSize: 100000
            VIRT_Parameters_MaxVectorSize: 3000000
            VIRT_Parameters_AdjustVectorSize: 1
            VIRT_Parameters_MaxQueryMem: ${vMaxQueryMem}
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
                if [ "${uploads[0]}" = "" ]; then
                    echo "No upload files to load. Please, specificy a list of upload files."
                    echo "Exit"
                    exit 1
                fi
                echo " -- Generating new compose instance."             
                echo "---------------------------------" 

                echo " -- Pull Images"
                ${COMPOSE_CMD} pull
                echo " -- Start Container"
                ${COMPOSE_CMD} up -d
                waitStarted
                echo " -- Container started."
                
                for f in ${uploads[@]}; do
                echo "Load $f: docker exec ${CONTAINER_NAME} isql-v 1111 dba '${PASSWORD}' ./dumps/$f"
                docker exec \
                    ${CONTAINER_NAME} \
                    isql-v 1111 dba "${PASSWORD}" ./dumps/$f
                done
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
