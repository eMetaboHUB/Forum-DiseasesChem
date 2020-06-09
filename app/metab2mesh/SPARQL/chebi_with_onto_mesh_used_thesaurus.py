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
    PREFIX chebi: <http://purl.obolibrary.org/obo/CHEBI_>
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
                                having(count (distinct ?cid) <= 10000)
                                order by ?chebi
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid a+ ?chebi .
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:broaderDescriptor+|fabio:hasSubjectTerm/meshv:hasDescriptor|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:broaderDescriptor+) ?mesh .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:treeNumber ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
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
                    ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:broaderDescriptor+|fabio:hasSubjectTerm/meshv:hasDescriptor|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:broaderDescriptor+) ?mesh .
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
select (count(distinct ?pmid) as ?count)
%s
where {
    {
        select ?mesh 
        where {
            ?mesh a meshv:TopicalDescriptor .
            ?mesh meshv:treeNumber ?tn .
            FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
        }
    }
    ?cid rdf:type chebi:24431 .
    ?cid cito:isDiscussedBy ?pmid .
    ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:broaderDescriptor+|fabio:hasSubjectTerm/meshv:hasDescriptor|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:broaderDescriptor+) ?mesh .
}
"""

count_distinct_pmids_by_CID_MESH = """
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
                                    }
                                    order by ?chebi
                                }
                            }
                            limit %d
                            offset %d
                        }              
                        ?cid rdf:type ?chebi .
                        ?cid cito:isDiscussedBy ?pmid .
                        ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:broaderDescriptor+|fabio:hasSubjectTerm/meshv:hasDescriptor|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:broaderDescriptor+) ?mesh .
                        ?mesh a meshv:TopicalDescriptor .
                        ?mesh meshv:treeNumber ?tn .
                        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))    
                    }
                    group by ?chebi ?mesh
                } 
            bind(uri(concat(\"http://database/ressources/metab2mesh/\", ?CHEBI, \"_\", ?MESH)) as ?id)
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
                select (concat(strafter(STR(?chebi),\"http://purl.obolibrary.org/obo/CHEBI_\"), \"_\", strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\")) as ?id) (strafter(str(?pmid), \"http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID\") as ?str_pmid)
                where {
                    {
                        select ?chebi 
                        where 
                        {
                            {
                                select distinct ?chebi where
                                {
                                    ?chebi rdfs:subClassOf+ chebi:24431 .
                                }
                                order by ?chebi
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid rdf:type ?chebi .
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:broaderDescriptor+|fabio:hasSubjectTerm/meshv:hasDescriptor|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:broaderDescriptor+) ?mesh .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:treeNumber ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
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
select count(distinct ?chebi)
%s
where{
    ?chebi rdfs:subClassOf+ chebi:24431 .
}
"""

count_number_of_MESH = """
select (count(distinct ?mesh) as ?count_MESH)
%s
where 
{
    ?mesh a meshv:TopicalDescriptor .
    ?mesh meshv:treeNumber ?tn .
    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
}
"""