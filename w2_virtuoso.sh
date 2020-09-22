#!/bin/bash

# USAGE (1) : ${0} start $PYDIO_PASSWD    # start virtuoso and load data (if needed) from PYDIO INRAE FORUM Project
# USAGE (2) : ${0} stop                   # stop virtuoso                  
# USAGE (3) : ${0} clean                  # remove docker directory


if [ "$#" -ne  "1" ]
then
     echo "what to do (start | stop | clean)"
     exit
fi

CMD=$1
PYDIO_PASSWD=$2

# LISTEN_PORT   Port to listen
# PASSWORD      admin password
# GRAPH         default graph name (iri)
# ALLOW_UDPATE  allow sparql update (YES | NO)

COMPOSE_PROJECT_NAME="metdisease"
LISTEN_PORT="9980"
PASSWORD="FORUM-Met-Disease-DB"
GRAPH="http://default#"
ALLOW_UDPATE="true"

URL_PYDIO_TTL="https://pfem.clermont.inra.fr/pydio/public/7af464/dl/"
OPTION_PYDIO_INRAE="-u none:$PYDIO_PASSWD"

RESOURCES_DIR=./share/

function download_resources() {
    echo " -- Download resources."

    # download files 
	
	[ ! -d ${RESOURCES_DIR}/MetaNetX ] && mkdir -p ${RESOURCES_DIR}/MetaNetX/
	[ ! -f ${RESOURCES_DIR}/MetaNetX/HumanGEM.ttl ] && wget --user none --password ${PYDIO_PASSWD} ${URL_PYDIO_TTL}/HumanGEM.ttl -P ${RESOURCES_DIR}/MetaNetX/
	[ ! -f ${RESOURCES_DIR}/MetaNetX/metanetx.ttl ] && wget --user none --password ${PYDIO_PASSWD} ${URL_PYDIO_TTL}/metanetx.ttl -P ${RESOURCES_DIR}/MetaNetX/
	
	[ ! -d ${RESOURCES_DIR}/vocabulary ] && wget --user none --password ${PYDIO_PASSWD} ${URL_PYDIO_TTL}/vocabulary -O ${RESOURCES_DIR}/vocabulary.zip
	[ -f ${RESOURCES_DIR}/vocabulary.zip ] && unzip ${RESOURCES_DIR}/vocabulary.zip -d ${RESOURCES_DIR}/ && rm -rf ${RESOURCES_DIR}/vocabulary.zip
}

## - not usefull actually -
function build() {
    echo " -- Build Docker Metdisease."
	docker build -t forum/metdisease .
}

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

UPDATA_FILE=update.sh

cat << EOF | tee ${RESOURCES_DIR}/${UPDATA_FILE} > /dev/null

GRANT SELECT ON "DB"."DBA"."SPARQL_SINV_2" TO "SPARQL";
GRANT EXECUTE ON "DB"."DBA"."SPARQL_SINV_IMP" TO "SPARQL";

# Importing namespace :
DB.DBA.XML_SET_NS_DECL ('SBMLrdf', 'http://identifiers.org/biomodels.vocabulary#', 2);
DB.DBA.XML_SET_NS_DECL ('bqbiol', 'http://biomodels.net/biology-qualifiers#', 2);
DB.DBA.XML_SET_NS_DECL ('mnxCHEM', 'http://identifiers.org/metanetx.chemical/', 2);
DB.DBA.XML_SET_NS_DECL ('chebi', 'http://identifiers.org/chebi/CHEBI:', 2);
DB.DBA.XML_SET_NS_DECL ('fbc', 'http://www.sbml.org/sbml/level3/version1/fbc/version2#', 2);
DB.DBA.XML_SET_NS_DECL ('model', 'http:doi.org/10.1126/scisignal.aaz1482#', 2);
DB.DBA.XML_SET_NS_DECL ('cid', 'http://identifiers.org/pubchem.compound/', 2);
DB.DBA.XML_SET_NS_DECL ('uniprot', 'http://identifiers.org/uniprot/', 2);
DB.DBA.XML_SET_NS_DECL ('ncbigene', 'http://identifiers.org/ncbigene/', 2);
DB.DBA.XML_SET_NS_DECL ('ensembl', 'http://identifiers.org/ensembl/', 2);
DB.DBA.XML_SET_NS_DECL ('hgnc_symbol', 'http://identifiers.org/hgnc.symbol/', 2);
DB.DBA.XML_SET_NS_DECL ('kegg_compound', 'http://identifiers.org/kegg.compound/', 2);
DB.DBA.XML_SET_NS_DECL ('hmdb', 'http://identifiers.org/hmdb/', 2);
DB.DBA.XML_SET_NS_DECL ('lipidmaps', 'http://identifiers.org/lipidmaps/', 2);
DB.DBA.XML_SET_NS_DECL ('kegg_rdf', 'https://www.kegg.jp/entry/', 2);
DB.DBA.XML_SET_NS_DECL ('cid_rdf', 'http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID', 2);
DB.DBA.XML_SET_NS_DECL ('chebi_rdf', 'http://purl.obolibrary.org/obo/CHEBI_', 2);
DB.DBA.XML_SET_NS_DECL ('chebi_2', 'https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:', 2);
DB.DBA.XML_SET_NS_DECL ('chembl', 'http://identifiers.org/chembl.compound/', 2);
DB.DBA.XML_SET_NS_DECL ('chembl_rdf', 'http://rdf.ebi.ac.uk/resource/chembl/molecule/', 2);

DELETE FROM DB.DBA.RDF_QUAD ;

ld_dir_all ('./dumps/MetaNetX/', 'metanetx.ttl', 'http://database/ressources/MetaNetX/4.0');
ld_dir_all ('./dumps/MetaNetX/', 'HumanGEM.ttl', 'http://database/ressources/HumanGEM');

ld_dir_all ('./dumps/vocabulary/', 'vocabulary_mesh_1.0.0.ttl', 'http://database/inference-rules');
ld_dir_all ('./dumps/vocabulary/', 'skos.rdf', 'http://database/inference-rules');
ld_dir_all ('./dumps/vocabulary/', 'fabio.ttl', 'http://database/inference-rules');
ld_dir_all ('./dumps/vocabulary/', 'dublin_core_terms.ttl', 'http://database/inference-rules');
ld_dir_all ('./dumps/vocabulary/', 'cito.ttl', 'http://database/inference-rules');
ld_dir_all ('./dumps/vocabulary/', 'cheminf.owl', 'http://database/inference-rules');

ld_dir_all ('./dumps/vocabulary/', 'chebi.owl', 'http://database/ressources/ChEBI');
ld_dir_all ('./dumps/vocabulary/', 'ChemOnt_2_1.ttl', 'http://database/ressources/ChemOnt');

select * from DB.DBA.load_list;
rdf_loader_run();
checkpoint;
select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;

RDFS_RULE_SET ('schema-inference-rules', 'http://database/inference-rules');
RDFS_RULE_SET ('schema-inference-rules', 'http://database/ressources/ChEBI');
RDFS_RULE_SET ('schema-inference-rules', 'http://database/ressources/ChemOnt');


checkpoint;

EOF

    case $CMD in
        start)
            if [ -d ${DATA} ]; then
                echo " -- Already generated."
                echo " -- Start Container"
                ${COMPOSE_CMD} up -d
                waitStarted
            else
				download_resources
				#build
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