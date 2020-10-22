#!/bin/bash

ENDPOINT="http://endpoint-metabolomics.ara.inrae.fr/met_disease_v2/sparql"
NB_GRAPH_LOADED_BEFORE_CHEMONT=7
WAIT_SEC=20s

LOG_GRAPH_VIRTUOSO=$0.graph_loaded.txt
ERROR_FILE=$0.find_error.txt

#http://database/ressources/MeSHRDF/
#http://database/ressources/PMID_CID/


#init
ret=0

while [ "$ret" -lt "${NB_GRAPH_LOADED_BEFORE_CHEMONT}" ]
do 
	sleep ${WAIT_SEC}
	echo "["$(date)"]curl --> ${ENDPOINT}"
	curl --silent -H "Accept: application/json" -G ${ENDPOINT} --data-urlencode query='
select distinct ?g where {
Graph ?g {?a a ?c}
filter( STRSTARTS(str(?g), "http://database/ressources") )
 } LIMIT 100
'>${LOG_GRAPH_VIRTUOSO}
	ret=$(cat ${LOG_GRAPH_VIRTUOSO}| jq ".results.bindings[].g.value" 2> ${ERROR_FILE} | wc -l)
	[ ! -s ${ERROR_FILE} ] || (echo "Error \n- `cat ${LOG_GRAPH_VIRTUOSO}`" && exit -1)
done
echo "======= graphes is available on tps ==========="
echo $(cat ${LOG_GRAPH_VIRTUOSO} | jq ".results.bindings[].g.value")
