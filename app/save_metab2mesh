#!/bin/bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')

sleep 1

echo " Start Metab2Mesh 2.0 ..."

docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" exec="
set blobs on;
sparql define output:format \"CSV\"
DEFINE input:inference \"schema-inference-rules\"
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
PREFIX voc: <http://myorg.com/voc/doc#>
prefix cito: <http://purl.org/spar/cito/>
prefix fabio:	<http://purl.org/spar/fabio/> 
prefix owl: <http://www.w3.org/2002/07/owl#> 
prefix void: <http://rdfs.org/ns/void#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>

select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) where {
    ?cid cito:isDiscussedBy ?pmid .
    ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
    ?mesh a meshv:TopicalDescriptor .
    ?mesh meshv:treeNumber ?tn .
    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
}
group by ?cid ?mesh 
;
" > ./dumps/pre_metab2mesh.csv '
docker exec -t $dockvirtuoso bash -c 'tail -n +10 ./dumps/pre_metab2mesh.csv | head -n -3 > ./dumps/metab2mesh.csv '

