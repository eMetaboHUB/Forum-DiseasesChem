prefix1 = """
DEFINE input:inference "schema-inference-rules"
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
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
prefix dcterms: <http://purl.org/dc/terms/>
PREFIX chemont: <http://purl.obolibrary.org/obo/CHEMONTID_>
PREFIX chebi: <http://purl.obolibrary.org/obo/CHEBI_>
"""

prefix2 = """
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
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
prefix dcterms: <http://purl.org/dc/terms/>
PREFIX chemont: <http://purl.obolibrary.org/obo/CHEMONTID_>
PREFIX chebi: <http://purl.obolibrary.org/obo/CHEBI_>
"""

cid_mesh = """
select distinct (strafter(STR(?selected_cid),"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID") as ?CID) ("related" as ?predicate)  (strafter(STR(?mesh),"http://id.nlm.nih.gov/mesh/") as ?MESH) 
%(from)s
where
{

	VALUES ?selected_cid { %(cid)s }
	?selected_cid skos:related ?mesh .
	?mesh meshv:treeNumber ?tn .
    FILTER(REGEX(?tn,"(C|A|G|F|I|J|D20|D23|D26|D27)"))
	

}
"""


mesh_hierarchical_relations = """
select distinct (strafter(STR(?mesh),"http://id.nlm.nih.gov/mesh/") as ?MeSH_child) ("hasParent" as ?predicate) (strafter(STR(?mesh_p),"http://id.nlm.nih.gov/mesh/") as ?MeSH_parent)
%(from)s
where
{

	?mesh a meshv:TopicalDescriptor .
	?mesh meshv:active 1 .
	?mesh meshv:treeNumber ?tn .
	?tn meshv:parentTreeNumber ?mesh_p_tn .
	?mesh_p meshv:treeNumber ?mesh_p_tn .
	?mesh_p meshv:active 1 .
}
"""


mesh_label = """
select distinct (strafter(STR(?mesh), "http://id.nlm.nih.gov/mesh/") as ?MESH) (str(?label) as ?MESH_LABEL)
%(from)s
where
{
    ?mesh a meshv:TopicalDescriptor .
    ?mesh meshv:active 1 .
    ?mesh rdfs:label ?label
}
"""

cid_mesh_related_mesh = """
select distinct (strafter(STR(?mesh1),"http://id.nlm.nih.gov/mesh/") as ?MESH1) ("related" as ?predicate) (strafter(STR(?mesh2),"http://id.nlm.nih.gov/mesh/") as ?MESH2)
%(from)s
where
{
	VALUES ?set { %(cid)s }
	?set skos:related ?mesh1 .
    ?mesh1 a meshv:TopicalDescriptor .
    ?mesh1 meshv:treeNumber ?tn1 .
    FILTER(REGEX(?tn1,"(C|A|G|F|I|J|D20|D23|D26|D27)"))
	?mesh1 skos:related ?mesh2 .
    ?mesh2 a meshv:TopicalDescriptor .
    ?mesh2 meshv:treeNumber ?tn2 .
    FILTER(REGEX(?tn2,"(C|A|G|F|I|J|D20|D23|D26|D27)"))
	?mesh2 skos:related ?set
}
"""

cid_chebi = """
select distinct (strafter(STR(?cid),"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID") as ?CID) ("is_a" as ?predicate) (strafter(STR(?chebi),"http://purl.obolibrary.org/obo/CHEBI_") as ?CHEBI)
%(from)s
where
{
    VALUES ?cid { %(cid)s }
	?cid a ?chebi .
    FILTER(STRSTARTS(str(?chebi), "http://purl.obolibrary.org/obo/CHEBI_"))
}
"""

chebi_hierarchical_relations = """
select distinct (strafter(STR(?chebi),"http://purl.obolibrary.org/obo/CHEBI_") as ?CHEBI) ("subClassOf" as ?predicate) (strafter(STR(?chebi_ancestor),"http://purl.obolibrary.org/obo/CHEBI_") as ?CHEBI_PARENT) 
%(from)s
where
{
	{
		select distinct ?chebi
		where
		{
			?chebi rdfs:subClassOf* chebi:24431
		}
	}
?chebi rdfs:subClassOf ?chebi_ancestor .
?chebi_ancestor a owl:Class
}
"""

chebi_label = """
select distinct (strafter(STR(?chebi),"http://purl.obolibrary.org/obo/CHEBI_") as ?CHEBI) (str(?chebi_label) as ?CHEBI_NAMES)
%(from)s
where
{
    ?chebi rdfs:subClassOf* chebi:24431 .    
    ?chebi rdfs:label ?chebi_label
}
"""

cid_related_chebi_related_mesh = """
select distinct (strafter(STR(?chebi),"http://purl.obolibrary.org/obo/CHEBI_") as ?CHEBI) ("related" as ?predicate) (strafter(STR(?mesh),"http://id.nlm.nih.gov/mesh/") as ?MESH)
%(from)s
where
{
	{
		select distinct ?chebi
		where
		{
			?cid a ?chebi
			VALUES ?cid { %(cid)s }
		}
	}
?chebi skos:related ?mesh
}
"""

cid_chemont = """
select distinct (strafter(STR(?cid),"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID") as ?CID) ("is_a" as ?predicate) (strafter(STR(?chemont),"http://purl.obolibrary.org/obo/") as ?CHEMONT) 
%(from)s
where
{
    ?cid a ?chemont
    VALUES ?cid { %(cid)s }
}
"""

chemont_hierarchical_relations = """
select distinct (strafter(STR(?chemont),"http://purl.obolibrary.org/obo/") as ?CHEMONT) ("subClassOf" as ?predicate) (strafter(STR(?chemont_ancestor),"http://purl.obolibrary.org/obo/") as ?CHEMONT_PARENT) 
%(from)s
where
{
	{
		select distinct ?chemont
		where
		{
			?chemont rdfs:subClassOf* chemont:9999999
		}
	}
?chemont rdfs:subClassOf ?chemont_ancestor .
?chemont_ancestor a owl:Class
}
"""

chemont_label = """
select distinct (strafter(STR(?chemont),"http://purl.obolibrary.org/obo/") as ?CHEMONT) (str(?chemont_label) as ?CHEMONT_NAMES)
%(from)s
where
{

    ?chemont rdfs:subClassOf* chemont:9999999 .
    ?chemont rdfs:label ?chemont_label
}
"""

cid_related_chemont_related_mesh = """
select distinct (strafter(STR(?chemont),"http://purl.obolibrary.org/obo/") as ?CHEMONT) (strafter(STR(?mesh),"http://id.nlm.nih.gov/mesh/") as ?MESH)
%(from)s
where
{
	{
		select distinct ?chemont
		where
		{
			?cid a ?chemont
			VALUES ?cid { %(cid)s }
		}
	}
?chemont skos:related ?mesh
}
"""