prefix = """
    DEFINE input:inference \"schema-inference-rules\"
"""

PubChem = """
    select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) ?label ?count
    %s
    where
    {
        {
            select ?mesh (count(distinct ?pmid) as ?count) 
            where
            {
                {
                    select ?pmid
                    where{
                        %s cito:isDiscussedBy ?pmid .
                        ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                        ?mesh_ini a meshv:TopicalDescriptor .
                        ?mesh_ini meshv:active 1 .
                        ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn .
                        %s meshv:treeNumber ?tn .
                    }
                }
                ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh .
                ?mesh a meshv:TopicalDescriptor .
                ?mesh meshv:active 1 .
                ?mesh meshv:treeNumber ?tn .
                FILTER(REGEX(?tn,\"(%s)\")) .
                
            }
            group by ?mesh
        }
        ?mesh rdfs:label ?label .
    }
"""

# (strafter(STR(?chebi),\"http://purl.obolibrary.org/obo/CHEBI_\") as ?CHEBI) (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 

ChEBI = """
    select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) ?label ?count
    %s
    where
    {
        {
            select ?mesh (count(distinct ?pmid) as ?count)
            where
            {
                {
                    select ?pmid
                    where
                    {        
                        ?cid a %s .
                        ?cid cito:isDiscussedBy ?pmid .
                        ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                        ?mesh_ini a meshv:TopicalDescriptor .
                        ?mesh_ini meshv:active 1 .
                        ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn .
                        %s meshv:treeNumber ?tn .
                    }
                }
                ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh .
                ?mesh a meshv:TopicalDescriptor .
                ?mesh meshv:active 1 .
                ?mesh meshv:treeNumber ?tn .
                FILTER(REGEX(?tn,\"(%s)\")) .
            }
            group by ?mesh
        }
        ?mesh rdfs:label ?label .
    }
"""


ChemOnt = """
select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) ?label ?count
%s
where
    {
        {
            select ?mesh (count(distinct ?pmid) as ?count)
            where
            {
                {
                    select ?pmid
                    where
                    {        
                        ?cid a %s .
                        ?cid cito:isDiscussedBy ?pmid .
                        ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh_ini .
                        ?mesh_ini a meshv:TopicalDescriptor .
                        ?mesh_ini meshv:active 1 .
                        ?mesh_ini (meshv:treeNumber|meshv:treeNumber/meshv:parentTreeNumber+) ?tn .
                        %s meshv:treeNumber ?tn .
                    }
                }
                ?pmid (fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor) ?mesh .
                ?mesh a meshv:TopicalDescriptor .
                ?mesh meshv:active 1 .
                ?mesh meshv:treeNumber ?tn .
                FILTER(REGEX(?tn,\"(%s)\")) .
            }
            group by ?mesh
        }
        ?mesh rdfs:label ?label .
    }
"""