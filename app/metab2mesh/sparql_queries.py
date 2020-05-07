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
"""

count_distinct_pmids_by_CID = """
select ?CID ?count
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
                                    ?cid cito:isDiscussedBy ?pmid .
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
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
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
                                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                                }
                                order by ?mesh
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid cito:isDiscussedBy ?pmid .
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

count_all_distinct_pmids = """
    select (count(distinct ?pmid) as ?count) where {
        {
            select ?mesh 
            where {
                ?mesh a meshv:TopicalDescriptor .
                ?mesh meshv:treeNumber ?tn .
                FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
            }
        }
        ?cid cito:isDiscussedBy ?pmid .
        ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
    }
"""

count_distinct_pmids_by_CID_MESH = """
select ?CID ?MESH ?count
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
                                        ?cid cito:isDiscussedBy ?pmid .
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
                        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))    
                    }
                    group by ?cid ?mesh
                } 
            bind(uri(concat(\"http://database/ressources/metab2mesh/\", ?CID, \"_\", ?MESH)) as ?id)
        }
        order by ?id
    }
}
limit %d
offset %d
"""


list_of_distinct_pmid_by_CID_MeSH = """
select ?id ?str_pmid
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
                                    ?cid cito:isDiscussedBy ?pmid .
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
    where 
    {
        ?cid cito:isDiscussedBy ?pmid .
    }
"""

count_number_of_MESH = """
    select (count(distinct ?mesh) as ?count_MESH) 
    where 
    {
        ?mesh a meshv:TopicalDescriptor .
        ?mesh meshv:treeNumber ?tn .
        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
    }
"""