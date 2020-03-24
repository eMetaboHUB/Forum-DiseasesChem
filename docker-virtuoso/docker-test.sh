sudo docker run --name my-virtuoso \
    -p 8890:8890 \
    -e DBA_PASSWORD=myDBTest \
    -e SPARQL_UPDATE=false \
    -e DEFAULT_GRAPH=http://database/ressources/ \
    -v /home/mxdelmas/Documents/Thèse/building_database/FORUM/metdiseasedatabase/data:/usr/local/virtuoso-opensource/var/lib/virtuoso/db/dumps \
    -d tenforce/virtuoso


sudo docker exec -it my-virtuoso bash

isql-v -U dba -P myDBTest


DELETE FROM DB.DBA.RDF_QUAD ;
ld_dir_all ('./dumps/CID_PMID/', '*.ttl', 'http://database/ressources/');
ld_dir_all ('./dumps/CID_PMID/', '*.trig', '');

ld_dir_all ('./dumps/CID_PMID_endpoints/', '*.ttl', 'http://database/ressources/');
ld_dir_all ('./dumps/CID_PMID_endpoints/', '*.trig', '');

ld_dir_all ('./dumps/PubChem_Compound/CompoundFiltered/', '*.ttl', 'http://database/ressources/');
ld_dir_all ('./dumps/PubChem_Compound/CompoundFiltered/', '*.trig', '');

ld_dir_all ('./dumps/PubChem_References/PrimarySubjectTermFiltered/', '*.ttl', 'http://database/ressources/');
ld_dir_all ('./dumps/PubChem_References/PrimarySubjectTermFiltered/', '*.trig', '');

ld_dir_all ('./dumps/PubChem_References/referenceFiltered/', '*.ttl', 'http://database/ressources/');
ld_dir_all ('./dumps/PubChem_References/referenceFiltered/', '*.trig', '');

ld_dir_all ('./dumps/MeSH/', '*.nt', 'http://id.nlm.nih.gov/mesh');

ld_dir_all ('./dumps/vocabulary/', '*.ttl', 'http://database/inference-rules/');
ld_dir_all ('./dumps/vocabulary/', '*.rdf', 'http://database/inference-rules/');
ld_dir_all ('./dumps/vocabulary/', '*.owl', 'http://database/inference-rules/');
ld_dir_all ('./dumps/new_inferences/', '*.ttl', 'http://database/inference-rules/');

select * from DB.DBA.load_list;
rdf_loader_run();
checkpoint;
select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;

# Set rules inferences
RDFS_RULE_SET ('schema-inference-rules', 'http://database/inference-rules/');
checkpoint;

# Check if there was errors during loading



sudo docker stop my-virtuoso

sudo docker rm  my-virtuoso




# Usefull request
  SELECT  DISTINCT ?g
   WHERE  { GRAPH ?g {?s ?p ?o} } 
ORDER BY  ?g

# Load voca with inferences : 
DEFINE input:inference 'schema-inference-rules'
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

SELECT ?p ?o
WHERE 
{
    GRAPH <http://database/inference-rules/> 
    {
        voc:DiseaseMeSH ?p ?o .
    }
}