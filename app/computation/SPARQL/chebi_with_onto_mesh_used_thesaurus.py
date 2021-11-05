prefix = """
    DEFINE input:inference \"schema-inference-rules\"
"""

count_distinct_pmids_by_ChEBI = """
select ?CHEBI ?count
%s
where
{
    {
        select ?CHEBI ?count
        where
        {
            {
                select (strafter(STR(?chebi),\"http://purl.obolibrary.org/obo/CHEBI_\") as ?CHEBI) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?chebi 
                        where 
                        {
                            {
                                select distinct ?chebi where
                                {
                                    ?chebi rdfs:subClassOf+ chebi:24431 .
                                    ?cid a+ ?chebi
                                }
                                group by ?chebi
                                having(count (distinct ?cid) <= 1000 && count(distinct ?cid) > 1)
                                order by ?chebi
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid a+ ?chebi .
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid (fabio:hasSubjectTerm/meshv:treeNumber|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:treeNumber) ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                    ?mesh meshv:treeNumber ?tn .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:active 1 .
                }
                group by ?chebi
            }
        }
        order by ?CHEBI
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
                            ?cid a chebi:24431
                        }
                    }
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
            ?cid a chebi:24431 .
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

count_distinct_pmids_by_ChEBI_MESH = """
select ?CHEBI ?MESH ?count
%s
where
{
    {
        select ?CHEBI ?MESH ?count
        where 
        {
                {
                    select (strafter(STR(?chebi),\"http://purl.obolibrary.org/obo/CHEBI_\") as ?CHEBI) (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 
                    where {
                        {
                            select ?chebi 
                            where 
                            {
                                {
                                    select distinct ?chebi where
                                    {
                                        ?chebi rdfs:subClassOf+ chebi:24431 .
                                        ?cid a+ ?chebi
                                    }
                                    group by ?chebi
                                    having(count (distinct ?cid) <= 1000 && count(distinct ?cid) > 1)
                                    order by ?chebi
                                }
                            }
                            limit %d
                            offset %d
                        }              
                        ?cid a+ ?chebi .
                        ?cid cito:isDiscussedBy ?pmid .
                        ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                        ?mesh_ini a meshv:TopicalDescriptor .
                        ?mesh_ini meshv:active 1 .
                        ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn .
                        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                        ?mesh meshv:treeNumber ?tn .
                        ?mesh a meshv:TopicalDescriptor .
                        ?mesh meshv:active 1 .
                    }
                    group by ?chebi ?mesh
                } 
            bind(uri(concat(\"https://forum.semantic-metabolomics.org/chebi2mesh/\", ?CHEBI, \"_\", ?MESH)) as ?id)
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
                select (concat(strafter(STR(?chebi),\"http://purl.obolibrary.org/obo/CHEBI_\"), \"_\", strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\")) as ?id) (strafter(str(?pmid), \"http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID\") as ?str_pmid)
                where 
                {
                    {
                        select ?chebi 
                        where 
                        {
                            {
                                select distinct ?chebi where
                                {
                                    ?chebi rdfs:subClassOf+ chebi:24431 .
                                    ?cid a+ ?chebi
                                }
                                group by ?chebi
                                having(count (distinct ?cid) <= 1000 && count(distinct ?cid) > 1)
                                order by ?chebi
                            }
                        }
                        limit %d
                        offset %d
                    }              
                    ?cid a+ ?chebi .
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                    ?mesh_ini a meshv:TopicalDescriptor .
                    ?mesh_ini meshv:active 1 .
                    ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                    ?mesh meshv:treeNumber ?tn .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:active 1 .  
                }
                group by ?chebi ?mesh
            }
        }
        order by ?id
    } 
}
limit %d
offset %d
"""

# Here chebi:23367 refer to chemical entity which is a chemical entity is a physical entity of interest in chemistry including molecular entities, parts thereof, and chemical substances.
count_number_of_ChEBI = """
select count(?chebi)
%s
where
{
    {
        select distinct ?chebi where
        {
            ?chebi rdfs:subClassOf+ chebi:24431 .
            ?cid a+ ?chebi
        }
        group by ?chebi
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
    ?pmid a fabio:Article
}
"""
