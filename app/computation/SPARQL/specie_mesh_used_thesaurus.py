prefix = """
    DEFINE input:inference \"schema-inference-rules\"
    DEFINE input:same-as \"yes\"
"""

count_distinct_pmids_by_SPECIE = """
select ?SPECIE ?count
%s
where
{
    {
        select ?SPECIE ?count
        where
        {
            {
                select (strafter(STR(?specie),\"http:doi.org/10.1126/scisignal.aaz1482#\") as ?SPECIE) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?specie 
                        where 
                        {
                            {
                                select distinct ?specie where
                                {
                                    ?specie a SBMLrdf:Species
                                }
                                order by ?specie
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?specie (bqbiol:is|bqbiol:is/skos:closeMatch) ?cid .
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid (fabio:hasSubjectTerm/meshv:treeNumber|fabio:hasSubjectTerm/meshv:hasDescriptor/meshv:treeNumber) ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\")) .
                    ?mesh meshv:treeNumber ?tn .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:active 1 .
                }
                group by ?specie
            }
        }
        order by ?SPECIE
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
                            ?specie a SBMLrdf:Species .
                            ?specie (bqbiol:is|bqbiol:is/skos:closeMatch) ?cid .
                            ?cid cito:isDiscussedBy ?pmid .
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
                    ?pmid a fabio:Article
                }
                limit %d
                offset %d
            }
            ?specie a SBMLrdf:Species .
            ?specie (bqbiol:is|bqbiol:is/skos:closeMatch) ?cid .
            ?cid cito:isDiscussedBy ?pmid .
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

count_distinct_pmids_by_SPECIE_MESH = """
select ?SPECIE ?MESH ?count
%s
where
{
    {
        select ?SPECIE ?MESH ?count
        where 
        {
                {
                    select (strafter(STR(?specie),\"http:doi.org/10.1126/scisignal.aaz1482#\") as ?SPECIE) (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 
                    where {
                        {
                            select ?specie 
                            where 
                            {
                                {
                                    select distinct ?specie where
                                    {
                                        ?specie a SBMLrdf:Species
                                    }
                                    order by ?specie
                                }
                            }
                            limit %d
                            offset %d
                        }
                        ?specie (bqbiol:is|bqbiol:is/skos:closeMatch) ?cid .
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
                    group by ?specie ?mesh
                } 
            bind(uri(concat(\"https://forum.semantic-metabolomics.org/specie2mesh/\", ?SPECIE, \"_\", ?MESH)) as ?id)
        }
        order by ?id
    }
}
limit %d
offset %d
"""


list_of_distinct_pmid_by_SPECIE_MeSH = """
select ?id ?str_pmid
%s
where
{
    {
        select ?id ?str_pmid
        where
        {
            {
                select (concat(strafter(STR(?specie),\"http:doi.org/10.1126/scisignal.aaz1482#\"), \"_\", strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\")) as ?id) (strafter(str(?pmid), \"http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID\") as ?str_pmid)
                where {
                    {
                        select ?specie 
                        where 
                        {
                            {
                                select distinct ?specie where
                                {
                                    ?specie a SBMLrdf:Species
                                }
                                order by ?specie
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?specie (bqbiol:is|bqbiol:is/skos:closeMatch) ?cid .
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
                group by ?specie ?mesh
            }
        }
        order by ?id
    } 
}
limit %d
offset %d
"""



count_number_of_SPECIE = """
select (count(distinct ?specie) as ?count_SPECIE)
%s
where 
{
    ?specie a SBMLrdf:Species
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