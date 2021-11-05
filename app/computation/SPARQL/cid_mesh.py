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
                    ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:treeNumber ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                    ?mesh meshv:active 1 .
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
                                    ?mesh meshv:treeNumber ?tn .
                                    ?mesh meshv:active 1 .
                                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                                }
                                order by ?mesh
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?endp obo:IAO_0000136 ?pmid .
                    ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
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
            ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
            ?mesh a meshv:TopicalDescriptor .
            ?mesh meshv:treeNumber ?tn .
            ?mesh meshv:active 1 .
            FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
        }
    }
}
limit %d
offset %d
"""

count_distinct_pmids_by_CID_MESH = """
select ?CID ?MESH ?count
%s
where
{
    {
        select ?CID ?MESH ?count
        where 
        {
                {
                    select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 
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
                        ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                        ?mesh a meshv:TopicalDescriptor .
                        ?mesh meshv:active 1 .
                        ?mesh meshv:treeNumber ?tn .
                        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))    
                    }
                    group by ?cid ?mesh
                } 
            bind(uri(concat(\"https://forum.semantic-metabolomics.org/compound2mesh/\", ?CID, \"_\", ?MESH)) as ?id)
        }
        order by ?id
    }
}
limit %d
offset %d
"""


list_of_distinct_pmid_by_CID_MeSH = """
select ?id ?str_pmid
%s
where
{
    {
        select ?id ?str_pmid
        where
        {
            {
                select (concat(strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\"), \"_\", strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\")) as ?id) (strafter(str(?pmid), \"http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID\") as ?str_pmid)
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
                    ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:active 1 .
                    ?mesh meshv:treeNumber ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                }
                group by ?cid ?mesh
            }
        }
        order by ?id
    } 
}
limit %d
offset %d
"""


MESH_name = """
select ?MESH str(?str_f_label)
%s
where
{
    {
        select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) MIN(str(?label)) as ?str_f_label
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
                            ?mesh meshv:treeNumber ?tn .
                            ?mesh meshv:active 1 .
                            FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                        }
                        order by ?mesh
                    }
                }
                limit %d
                offset %d
            }
        ?mesh rdfs:label ?label
        }
        group by ?mesh
        order by ?mesh
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

count_number_of_MESH = """
select (count(distinct ?mesh) as ?count_MESH)
%s
where 
{
    ?mesh a meshv:TopicalDescriptor .
    ?mesh meshv:treeNumber ?tn .
    ?mesh meshv:active 1 .
    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
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