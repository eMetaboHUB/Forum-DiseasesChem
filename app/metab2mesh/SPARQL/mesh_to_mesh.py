prefix = """
    DEFINE input:inference \"schema-inference-rules\"
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
    PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
    PREFIX voc: <http://myorg.com/voc/doc#>
    PREFIX cito: <http://purl.org/spar/cito/>
    PREFIX fabio:	<http://purl.org/spar/fabio/> 
    PREFIX owl: <http://www.w3.org/2002/07/owl#> 
    PREFIX void: <http://rdfs.org/ns/void#>
    PREFIX cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
    PREFIX sio: <http://semanticscience.org/resource/>
    PREFIX obo: <http://purl.obolibrary.org/obo/>
"""

count_distinct_pmids_by_MESH = """
select ?MESH ?count
%s
where
{
    {
        select ?MESH ?count
        where
        {
            {
                select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?mesh
                        where
                        {
                            {
                                select distinct ?mesh
                                where
                                {
                                    ?mesh a meshv:TopicalDescriptor .
                                    ?mesh meshv:active 1 .
                                    ?mesh meshv:treeNumber ?tn .
                                    FILTER(REGEX(?tn,\"(C|A|G|F|I|J|D20|D23|D26|D27)\"))
                                }
                                order by ?mesh
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?endp obo:IAO_0000136 ?pmid .
                    ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                    ?mesh_ini a meshv:TopicalDescriptor .
                    ?mesh_ini meshv:active 1 .
                    ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn .
                    ?mesh meshv:treeNumber ?tn .
                    
                }
                group by ?mesh
            }
        }
        order by ?MESH
    }
}
limit %d
offset %d
"""


count_distinct_pmids_by_MESH_MESH = """
select ?MESH1 ?MESH2 ?count
%s
where
{
    {
        select ?MESH1 ?MESH2 ?count
        where
        {
            {
                select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH1) (strafter(STR(?mesh_all),\"http://id.nlm.nih.gov/mesh/\") as ?MESH2) ?count 
                where
                {
                    {
                        select ?mesh ?mesh_all (count(distinct ?pmid) as ?count) 
                        where
                        {
                            {
                                select distinct ?mesh ?pmid
                                where
                                {

                                    {
                                        select ?mesh
                                        where
                                        {
                                            {
                                                select distinct ?mesh
                                                where
                                                {
                                                    ?mesh a meshv:TopicalDescriptor .
                                                    ?mesh meshv:active 1 .
                                                    ?mesh meshv:treeNumber ?tn .
                                                    FILTER(REGEX(?tn,\"(C|A|G|F|I|J|D20|D23|D26|D27)\"))
                                                }
                                                order by ?mesh
                                            }
                                        }
                                        limit %s
                                        offset %s
                                    }
                                    ?endp obo:IAO_0000136 ?pmid .
                                    ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                                    ?mesh_ini a meshv:TopicalDescriptor .
                                    ?mesh_ini meshv:active 1 .
                                    ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn .
                                    ?mesh meshv:treeNumber ?tn .
                                }
                            }
                            ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini_2 .
                            ?mesh_ini_2 a meshv:TopicalDescriptor .
                            ?mesh_ini_2 meshv:active 1 .
                            ?mesh_ini_2 (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn_all .
                            FILTER(REGEX(?tn_all,\"(C|A|G|F|I|J|D20|D23|D26|D27)\")) .
                            ?mesh_all meshv:treeNumber ?tn_all
                        }
                        group by ?mesh ?mesh_all
                    }
                    FILTER
                        ( 
                            NOT EXISTS
                            { 
                                ?mesh_all meshv:treeNumber/meshv:parentTreeNumber* ?tn .
                                ?mesh meshv:treeNumber ?tn 
                            } 
                            && 
                            NOT EXISTS
                            {
                                ?mesh meshv:treeNumber/meshv:parentTreeNumber* ?tn_annot .
                                ?mesh_all meshv:treeNumber ?tn_annot .
                            }
                        )
                }
            }
            bind(uri(concat(\"http://database/ressources/mesh2mesh/\", ?MESH1, \"_\", ?MESH2)) as ?id)
        }
        order by ?id
    }
}
limit %d
offset %d
"""

count_all_individuals = """
select ?COUNT
%s
where
{
    {
        select (count(distinct ?pmid) as ?COUNT)
        where
        {
            {
                select ?pmid 
                where
                {
                    ?pmid a fabio:Article
                }
                limit %d
                offset %d
            }
            ?endp obo:IAO_0000136 ?pmid .
            ?pmid (fabio:hasSubjectTerm/meshv:treeNumber|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:treeNumber) ?tn .
            FILTER(REGEX(?tn,\"(C|A|G|F|I|J|D20|D23|D26|D27)\")) .
            ?mesh meshv:treeNumber ?tn .
            ?mesh a meshv:TopicalDescriptor .
            ?mesh meshv:active 1 .
        }
    }
}
limit %d
offset %d
"""


count_number_of_MESH = """
select (count(distinct ?mesh) as ?count_MESH)
%s
where 
{
    ?mesh a meshv:TopicalDescriptor .
    ?mesh meshv:active 1 .
    ?mesh meshv:treeNumber ?tn .
    FILTER(REGEX(?tn,\"(C|A|G|F|I|J|D20|D23|D26|D27)\"))
}
"""


count_all_pmids = """
select count(?pmid) 
%s
where
{
    ?pmid a fabio:Article
}
"""