prefix = """
    DEFINE input:inference \"schema-inference-rules\"
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
                    ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber) ?tn .
                    ?mesh_ini a meshv:TopicalDescriptor .
                    ?mesh_ini meshv:active 1 .
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


count_distinct_pmids_by_SCR = """
select ?SCR ?count
%s
where
{
    {
        select ?SCR ?count
        where
        {
            {
                select (strafter(STR(?SCR_Disease),\"http://id.nlm.nih.gov/mesh/\") as ?SCR) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?SCR_Disease
                        where
                        {
                            {
                                select distinct ?SCR_Disease
                                where
                                {
                                    ?SCR_Disease a meshv:SCR_Disease .
                                    ?SCR_Disease meshv:active 1 .
                                }
                                order by ?SCR_Disease
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?endp obo:IAO_0000136 ?pmid .
                    ?pmid cito:discusses ?SCR_Disease.
                }
                group by ?SCR_Disease
            }
        }
        order by ?SCR
    }
}
limit %d
offset %d
"""

count_distinct_pmids_by_MESH_SCR = """
select ?MESH1 ?SCR ?count
%s
where
{
    {
        select ?MESH1 ?SCR ?count
        where
        {
            {
                select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH1) (strafter(STR(?SCR_Disease),\"http://id.nlm.nih.gov/mesh/\") as ?SCR) ?count 
                where
                {
                    {
                        select ?mesh ?SCR_Disease (count(distinct ?pmid) as ?count) 
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
                                    ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber) ?tn .
                                    ?mesh_ini a meshv:TopicalDescriptor .
                                    ?mesh_ini meshv:active 1 .
                                    ?mesh meshv:treeNumber ?tn .
                                }
                            }
                            ?pmid cito:discusses ?SCR_Disease.
                            ?SCR_Disease a meshv:SCR_Disease .
                            ?SCR_Disease meshv:active 1 .
                        }
                        group by ?mesh ?SCR_Disease
                    }
                }
            }
            bind(uri(concat(\"https://forum.semantic-metabolomics.org/mesh2mesh/\", ?MESH1, \"_\", ?SCR)) as ?id)
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
                    ?pmid <http://prismstandard.org/namespaces/basic/3.0/contentType> ?typec .
                    filter(contains(?typec,"Journal Article")) .
                }
                limit %d
                offset %d
            }
            ?endp obo:IAO_0000136 ?pmid .
            {
                ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                ?mesh a meshv:TopicalDescriptor .
                ?mesh meshv:treeNumber ?tn .
                ?mesh meshv:active 1 .
                FILTER(REGEX(?tn,\"(C|A|G|F|I|J|D20|D23|D26|D27)\")) .
            }
            UNION
            {
                ?pmid cito:discusses ?SCR_Disease .
                ?SCR_Disease a meshv:SCR_Disease .
                ?SCR_Disease meshv:active 1 .
            }
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

count_number_of_SCR = """
select (count(distinct ?SCR_Disease) as ?count_SCR)
%s
where 
{
    ?SCR_Disease a meshv:SCR_Disease .
    ?SCR_Disease meshv:active 1 .
}
"""


count_all_pmids = """
select count(?pmid) 
%s
where
{
    ?pmid <http://prismstandard.org/namespaces/basic/3.0/contentType> ?typec .
    filter(contains(?typec,"Journal Article")) .
}
"""