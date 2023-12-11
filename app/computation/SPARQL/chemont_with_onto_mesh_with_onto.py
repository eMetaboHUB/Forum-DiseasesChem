prefix = """
    DEFINE input:inference \"schema-inference-rules\"
"""


count_distinct_pmids_by_ChemOnt = """
select ?CHEMONT ?count
%s
where
{
    {
        select ?CHEMONT ?count
        where
        {
            {
                select (strafter(STR(?chemont),\"http://purl.obolibrary.org/obo/\") as ?CHEMONT) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?chemont 
                        where 
                        {
                            {
                                select distinct ?chemont where
                                {
                                    ?chemont rdfs:subClassOf+ chemont:9999999 .
                                    ?cid a+ ?chemont
                                }
                                group by ?chemont
                                having(count (distinct ?cid) <= 1000 && count(distinct ?cid) > 1)
                                order by ?chemont
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid a+ ?chemont .
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid (fabio:hasSubjectTerm/meshv:treeNumber|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:treeNumber) ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                    ?mesh meshv:treeNumber ?tn .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:active 1 .
                }
                group by ?chemont
            }
        }
        order by ?CHEMONT
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
                                    ?mesh meshv:active 1 .
                                    ?mesh meshv:treeNumber ?tn .
                                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                                }
                                order by ?mesh
                            }
                        }
                        limit %d
                        offset %d
                    }
                    {
                        select ?pmid
                        where
                        {
                            ?cid cito:isDiscussedBy ?pmid .
                            ?cid a chemont:9999999
                        }
                    }
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
            ?cid a chemont:9999999 .
            ?pmid cito:discusses ?cid .
            ?pmid (fabio:hasSubjectTerm/meshv:treeNumber|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:treeNumber) ?tn .
            FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
            ?mesh meshv:treeNumber ?tn .
            ?mesh a meshv:TopicalDescriptor .
            ?mesh meshv:active 1 .
        }
    }
}
limit %d
offset %d
"""



count_distinct_pmids_by_ChemOnt_MESH = """
select ?CHEMONT ?MESH ?count
%s
where
{
    {
        select ?CHEMONT ?MESH ?count
        where 
        {
                {
                    select (strafter(STR(?chemont),\"http://purl.obolibrary.org/obo/\") as ?CHEMONT) (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 
                    where {
                        {
                            select ?chemont 
                            where 
                            {
                                {
                                    select distinct ?chemont where
                                    {
                                        ?chemont rdfs:subClassOf+ chemont:9999999 .
                                        ?cid a+ ?chemont
                                    }
                                    group by ?chemont
                                    having(count (distinct ?cid) <= 1000 && count(distinct ?cid) > 1)
                                    order by ?chemont
                                }
                            }
                            limit %d
                            offset %d
                        }              
                        ?cid a+ ?chemont .
                        ?cid cito:isDiscussedBy ?pmid .
                        ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                        ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber) ?tn .
                        ?mesh_ini a meshv:TopicalDescriptor .
                        ?mesh_ini meshv:active 1 .
                        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                        ?mesh meshv:treeNumber ?tn .
                        ?mesh a meshv:TopicalDescriptor .
                        ?mesh meshv:active 1 .
                    }
                    group by ?chemont ?mesh
                } 
            bind(uri(concat(\"https://forum.semantic-metabolomics.org/chemont2mesh/\", ?CHEMONT, \"_\", ?MESH)) as ?id)
        }
        order by ?id
    }
}
limit %d
offset %d
"""


list_of_distinct_pmid_by_ChEBI_MeSH = """
select ?id ?str_pmid
%s
where
{
    {
        select ?id ?str_pmid
        where
        {
            {
                select (concat(strafter(STR(?chemont),\"http://purl.obolibrary.org/obo/\"), \"_\", strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\")) as ?id) (strafter(str(?pmid), \"http://rdf.ncbi.nlm.nih.gov/pubchem/reference/\") as ?str_pmid)
                where 
                {
                    {
                        select ?chemont 
                        where 
                        {
                            {
                                select distinct ?chemont where
                                {
                                    ?chemont rdfs:subClassOf+ chemont:9999999 .
                                    ?cid a+ ?chemont
                                }
                                group by ?chemont
                                having(count (distinct ?cid) <= 1000 && count(distinct ?cid) > 1)
                                order by ?chemont
                            }
                        }
                        limit %d
                        offset %d
                    }              
                    ?cid a+ ?chemont .
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                    ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber) ?tn .
                    ?mesh_ini a meshv:TopicalDescriptor .
                    ?mesh_ini meshv:active 1 .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                    ?mesh meshv:treeNumber ?tn .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:active 1 .  
                }
                group by ?chemont ?mesh
            }
        }
        order by ?id
    } 
}
limit %d
offset %d
"""


# Here chemont:9999999 refer to chemical entities which is a chemical entity is the root of the classification
count_number_of_ChemOnt = """
select count(?chemont)
%s
where
{
    {
        select distinct ?chemont where
        {
            ?chemont rdfs:subClassOf+ chemont:9999999 .
            ?cid a+ ?chemont
        }
        group by ?chemont
        having(count (distinct ?cid) <= 1000 && count(distinct ?cid) > 1)
    }
}
"""

count_number_of_MESH = """
select (count(distinct ?mesh) as ?count_MESH)
%s
where 
{
    ?mesh a meshv:TopicalDescriptor .
    ?mesh meshv:active 1 .
    ?mesh meshv:treeNumber ?tn .
    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
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