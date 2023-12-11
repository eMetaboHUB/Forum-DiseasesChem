prefix = """
    DEFINE input:inference \"schema-inference-rules\"
"""

count_distinct_pmids_by_CID = """
select ?CID ?count
%s
where
{
    {
        select ?CID ?count
        where
        {
            {
                select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?cid 
                        where 
                        {
                            {
                                select distinct ?cid where
                                {
                                    ?endp cito:isCitedAsDataSourceBy ?cid .
                                }
                                order by ?cid
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid cito:isDiscussedBy ?pmid .
                    {
                        ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                        ?mesh a meshv:TopicalDescriptor .
                        ?mesh meshv:treeNumber ?tn .
                        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                        ?mesh meshv:active 1 .
                    }
                    UNION
                    {
                        ?pmid cito:discusses ?SCR_Disease.
                        ?SCR_Disease a meshv:SCR_Disease .
                        ?SCR_Disease meshv:active 1 .
                    }
                }
                group by ?cid
            }
        }
        order by ?CID
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
                FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
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



count_distinct_pmids_by_CID_SCR = """
select ?CID ?SCR ?count
%s
where
{
    {
        select ?CID ?SCR ?count
        where 
        {
                {
                    select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (strafter(STR(?SCR_Disease),\"http://id.nlm.nih.gov/mesh/\") as ?SCR) (count(distinct ?pmid) as ?count) 
                    where {
                        {
                            select ?cid where {
                                {
                                    select distinct ?cid where {
                                        ?endp cito:isCitedAsDataSourceBy ?cid .
                                    }
                                    order by ?cid
                                }
                            }
                            limit %d
                            offset %d
                        }              
                        ?cid cito:isDiscussedBy ?pmid .
                        ?pmid cito:discusses ?SCR_Disease .
                        ?SCR_Disease a meshv:SCR_Disease .
                        ?SCR_Disease meshv:active 1 .
                    }
                    group by ?cid ?SCR_Disease
                } 
            bind(uri(concat(\"https://forum.semantic-metabolomics.org/compound2SCR/\", ?CID, \"_\", ?SCR)) as ?id)
        }
        order by ?id
    }
}
limit %d
offset %d
"""

SCR_name = """
select ?SCR str(?str_f_label)
%s
where
{
    {
        select (strafter(STR(?SCR_Disease),\"http://id.nlm.nih.gov/mesh/\") as ?SCR) MIN(str(?label)) as ?str_f_label
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
        ?SCR_Disease rdfs:label ?label
        }
        group by ?SCR_Disease
        order by ?SCR_Disease
    }
}
limit %d
offset %d
"""

count_number_of_CID = """
select (count(distinct ?cid) as ?count_CID)
%s
where 
{
    ?endp cito:isCitedAsDataSourceBy ?cid .
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
}
"""