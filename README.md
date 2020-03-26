## Metabolite - Diseases Graph Database

This repository contains some usefull methods to provides links between PubChem compound identifiers, litteratures (PMIDs) and MeSH

*GetCID_PMID_associations* is the main test file, where I test the developped functions.

-   **The Database_ressource_version object:**
  This object provide a way to create a new version of a ressource. Information are contained in two majors files:
-   ```ressource_info file```: is the file containing all the descriptive information associated to the created version of the ressource, such as the linkded ressource, the creation date, a description, the list of the associated RDF graphs, etc ...
-   ```data_graph```: Each ressource vesion is composed of a set of triples, organized in one or several named graph. Each of these named-graph are linked to the new version of the ressource in the ```ressource_info file```. A schema representing the process is presented below :

![**Description of the versioning process**](SchemaVersioningRDF.png)

-   **The Ensemble_pccompound object:** 

This objects provide a way to fetch the pmids associated to a list of PubChem compounds (CID). Tow ressources are linked to this object: 
- CID_PMID: is the ressource referencing all the cid - pmids associated using the cito:isDiscussedBy predicate.
- CID_PMID_enpoint: is the ressources referencing all the additionnal information linked to each cid-pmid associations such as contributors

```python
Ensemble_pccompound()
``` 
Allow to create an empty Ensemble_pccompound object. Once this object is created, all the selected CID can integrated to this object using the *append_pccompound* method.

```python
Ensemble_pccompound.append_pccompound(cid, query_builder)
```

- ```cid``` :
  a cid (PubChem compound CID ) to append to the Ensemble_pccompound object. Ex: 6036 for Galactose
- ```query_builder``` : 
a Eutils QueryService used to request to NCBI server, whcih can be created as :
    
```python
    apiKey = "0ddb3479f5079f21272578dc6e040278a508"
    query_builder = eutils.QueryService(cache = False, default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'}, api_key = apiKey)
```
    
The Api_key can be found on the NCBI account.

When an PubChem CID is append to the Ensemble_pccompound objects, a *Eutils* (*Elink* function) request is send to get all the pmids associated to the current cid. If the request failed (serveur error, bad request, ...) or if it seems to be no pmids associated to the cid, the cid is directly added to the *append_failure* cid list for future try or correction.

A cid-pmid association is describe with the contributor associated to this association. Contributors represent the three main sources of litterature annotation in the PubChem database: *NLM Mesh Curated association*, *Depositor provided association* and *Publisher provided association.* Once all the selected CID have been added by the ```append_pccompound``` method, results can be exported.

```python
Ensemble_pccompound.get_all_pmids()
```
Return union of all the pmids fetched for all the cid appened to the Ensemble_pccompound object

```python
Ensemble_pccompound.get_all_cids()
```
When all the cid have been added to the Ensemble_pccompound object, associated ressources version may be created.

```python
create_CID_PMID_ressource(self, namespace_dict, out_dir, version)
```
This function is used to create a new version of the CID_PMID and CID_PMID_enpoint ressources, by creating all the ressource and named graph associated to from information contained in the object.
-   ```namespace_dict```: dict containing all the used namespaces.
-   ```out_dir```: a path to an directory to write output files.
-   ```version```: the version name. If None, the date will be choose by default.   

This function will created two types of files for each ressource:

-   ```ressource_info_*``` files containing all the information associated to the new version of the ressources and the associated named-graphs
-   ```cid_pmid{_endpoint}.trig``` files containing all the triples in an associated named graph


So as exemple, to get all the literature association for two PubChem compoound such as Galactose (cid:6036) and (KDO)2-lipid A (cid:11355423) :

```python
apiKey = "0ddb3479f5079f21272578dc6e040278a508"
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)

new_Ensemble_pccompound = Ensemble_pccompound()
new_Ensemble_pccompound.append_pccompound("11355423", query_builder)
new_Ensemble_pccompound.append_pccompound("6036", query_builder)
# Creating ressources files.
new_Ensemble_pccompound.create_CID_PMID_ressource(namespaces, "data/", None)

all_pmids = new_Ensemble_pccompound.get_all_pmids()
all_cids = new_Ensemble_pccompound.get_all_cids()
```
* * *

PubChem provides RDF files from his ftp server which can be dowload and associated to a ressource using the ```dowload_pubChem```.
This function allow to dowload all the files associated to a particular directory in the ftp server and to create a new version of the associated ressource, bringing information from the void.ttl file.

```python
dowload_pubChem(dir, request_ressource, out_path)
```
-   ```dir```: the path to the directory/file to fetch in the ftp server from ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/
-   ```request_ressource```: the name of the ressource as indicated in the void.ttl file.
-   ```out_path```: a path to a directory to write output files

Using: 
```python
dowload_pubChem("reference", "reference", "path/to/out/")
```
A new version of the ressource *reference* is created from the RDF files dowloaded from the ftp server.
* * *

But these files contains a huge amount of data and only a part is related to our compounds.
```parse_pubchem_RDF``` is a function which is used to create a new ressource, from an exisyting reference ressource, by parsing files and extract only triples for which the subjet is contains in a set of defined subject. By default this new ressource shoud be called '*xxxFiltered*'.
By providing the ressource_info file (containing the graph describing the reference ressource), a path to the directory containing all the associated named graphs and a set of identifiers, this function create a *Filtered* ressource from the reference ressource, with ressource_info graph and all the associated named graph derived from the originals. 

```python
parse_pubchem_RDF(input_ressource_directory, all_ids, prefix, input_ressource_file, input_ressource_uri, out_dir, filtered_ressource_name, input_ids_uri, isZipped, namespace_dict, version, separator)
```

-   ```input_ressource_directory```: a path to the directory containing all the RDF files referenced has 'partOf' the reference source in the input_ressource_file
-   ```input_ressource_file```: a ressource_info file containing informations about the reference ressource.
-   ```all_ids```: a list of all the ids that should be used to parse the RDF files associated to the ressource.
-   ```prefix```: the string representing the prefix that shoud be added to the id to create the URI of subjects in the file.
-   ```input_ressource_uri```: the rdflib.UriRef associated to the reference ressource in the input_ressource_file
-   ```out_dir```: a path to an directory to write output files.
-   ```filtered_ressource_name```: the name of the new ressource, creating from the parsing of the reference file.
-   ```input_ids_uri```: the rdflib.UriRef associated to the reference ressource from which the set of all_ids was created.
-   ```isZipped```: is the reference files are zipped: True/False.
-   ```namespace_dict```: dict containing all the used namespaces.
-   ```version```: the version name. If None, the date will be choose by default.
-   ```separator```: the separator used in triples (.ttl) files to separated subject/predicate/object: \t or ' '
    """


As Exemple, to filter the reference ressource to only have thoose involving with the studied compounds: 
```python
parse_pubchem_RDF(input_ressource_directory = "path/to/reference/version_X/", 
                  all_ids = all_pmids,
                  prefix = "reference:PMID", 
                  out_dir = "path/out/",
                  input_ressource_file = "data/PubChem_References/reference/ressource_info_reference_version_X.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/reference/version_X"),
                  filtered_ressource_name = "referenceFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/version_X"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = None,
                  separator = '\t')
```
* * *
A issue was also found in the pc_reference2chemical_diseases.ttl files. This files provides associations between pmids and Supplementary Concept MeSH Records (SCRs) which are composed of two principals types Diseases and Chemicals. The predicated used in this associations was *cito:discusses* whcih is the reverse property of *cito:isDiscussedBy*. But, *cito:isDiscussedBy* was already used to annotated associations between cid and pmids, so to prevent errors with inferences, I choose to change all the *cito:discusses* predicates in this files with *fabio:hasSubjectTerm* which is explicitly defined to be used with MeSH terms.

* * *
The main issue about PubChem RDF Reference files provided in the ftp server, is that they only provide triples with the *fabio:hasSubjectTerm* predicates, which correspond to secondary mesh associated to the pmid but don't provide the *fabio:hasPrimarySubjectTerm* which represent the main topics of the artcile, which is an import source of information.


The function ```REST_ful_bulk_download``` is designed to send request to the PubChem RDFful REST server and get this missing information. Using a specified domain and predicate a request will be send to get all the associated triples. But, the server can't send more than 10000 records at the same time, so the function will export each packets of 10000 triples in different files and increment the offset parameter o the request until get all the triples. The function return a list of offsets for which there was a server errors (HTTP status > 200), for which it would be necessary to relaunch the function. All the fetched triples will be used to create a new version of the related ressource. Due to the large amount of data which can be retrieved, triples are distributed in succesives named graph with a maximal size of 10.000.000 triples.

```python
REST_ful_bulk_download(graph, predicate, out_name, start_offset, out_dir, ressource_name, namespaces_list, namespaces_dict, version):
```

-   ```graph```: the subject database of the triples to fetch from the REST api of PubChem.
-   ```predicate```: the predicate of the triple (with the prefix in a turtle syntax)
-   ```out_name```: the name of output RDF file
-   ```start_offset```: the offset used to start (Cf. PubChem REST api doc)
-   ```out_dir```: a path to an directory to write output files
-   ```ressource_name```: the name of the created ressource
-   ```namespace_list```: a list of the namespaces that should be associated to the named-graph
-   ```namespace_dict```: a dict containing all the used namespaces.
-   ```version```: the version name. If None, the date will be choose by default.


If for any reasons the function failed, the function can be restarted at the last offset using the ```start_offset``` parameter.
As, example, to get all the triples from the *reference* database containing the *fabio:hasPrimarySubjectTerm* predicate, we can use: 

```python
requests_failed = REST_ful_bulk_download(graph = 'reference', predicate = 'fabio:hasPrimarySubjectTerm', out_name = 'PrimarySubjectTerm',
                                         start_offset = 0, out_dir = "path/to/out/",
                                         ressource_name = "PrimarySubjectTerm", namespaces_list = ["reference", "fabio", "mesh"],
                                         namespaces_dict = namespaces,
                                         version = None)
```

With this function 52178606 (v.2020-03-20) of triples involving a pmid and a mesh with the predicate *fabio:hasPrimarySubjectTerm* was found.
After this, all the files may be collapse as one, compress and send to the function ```parse_pubchem_RDF``` to only extract thoose for which we have an associated PubChem CID.

And then we can use the ```parse_pubchem_RDF``` to parse the file.
For all named graph which were wrote using an rdflib serialize process, the separator in the resulting turtle file is always ' '.
```python
parse_pubchem_RDF(input_ressource_directory = "path/to/PrimarySubjectTerm/version_X/",
                  all_ids = all_pmids,
                  prefix = "reference:PMID",
                  out_dir = "path/to/out/",
                  input_ressource_file = "path/to/PrimarySubjectTerm/ressource_info_PrimarySubjectTerm_version_X.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PrimarySubjectTerm/version_X"),
                  filtered_ressource_name = "PrimarySubjectTermFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/version_X"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = None,
                  separator = ' ')
```
* * *
MeSH RDF triples must also be download in the same way. This can be do using the function ```dowload_MeSH```:
```python
dowload_MeSH(out_dir, namespaces_dict)
```
-   ```out_dir```: a path to an directory to write output files
-   ```namespaces_dict```: a dict containing all the used namespaces.
So to download the whole MeSH RDF, ce can simply do :

```python
dowload_MeSH("path/to/out/", namespaces)
```


* * *
The same process can be done for pubChem compounds.
## Ontology

The differents RDF stores and RDFS/OWL Schema can be dowload in: 
- MeSH
  - RDF: ```ftp://ftp.nlm.nih.gov/online/mesh/rdf/mesh.nt.gz```
  - Schema: ```ftp://ftp.nlm.nih.gov/online/mesh/rdf/vocabulary_1.0.0.ttl```
- ChEBI:
  - Schema: ```ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.owl```
- cito
  - Schema: ```http://purl.org/spar/cito.ttl```
- fabio:
  - Schema: ```http://purl.org/spar/fabio.ttl```
- Dublin Core:
  - Schema: ```https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.nt```

Then, a owl file was build to provide logical links between entity to infer association between PubChem CID and MeSH associated to a diseases. The file is in new_inferences/doc_voc_test.ttl (details in notes)

After loading all th named graph associated to ressources: cid_pmid, cid_pmid_endpoint, referenceFiltered, PrimarySubjectTermFitlered, compoundFiltered, the folowing request may be used to get to cid - mesh diseases asociations.

```
select ?cid ?mesh (count(?pmid) as ?c) where {
	?cid cito:isDiscussedBy ?pmid
	?pmid fabio:hasSubjectTerm ?mesh
	?mesh a voc:DiseaseLinkedMesH
} group by (?mesh) ORDER BY DESC(?c)
```
This request actualy work on corese !

## Virtuoso:

Docker compose is available using the workflow.sh
The *share* directory must contains all the data that have to be imported in virtuoso.
Data are organized in different directory, each corresponding to a particular ressource.
CID_PMID: contains all *.trig* RDF files the corresponding metadata *.ttl* files associated to the ressource CID_PMID you want to load.

During the loading of the service it's important to check the result of the command *select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;* which is checking about import errors.
the service will be available at *http://localhost:9980/sparql* 

The query which may be used to get all the cid - MeSH diseases assocaition with the number of associated pmid is :  

```
DEFINE input:inference 'schema-inference-rules'
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
PREFIX voc: <http://myorg.com/voc/doc#>
prefix cito: <http://purl.org/spar/cito/>
prefix fabio:	<http://purl.org/spar/fabio/> 
prefix owl: <http://www.w3.org/2002/07/owl#> 

select ?cid ?mesh ?name ?countdist where {
	
	?mesh rdfs:label ?name .	
	{
		select ?mesh ?cid (count(distinct ?pmid) as ?countdist) where {
		?cid cito:isDiscussedBy ?pmid .
		?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
		?mesh a meshv:TopicalDescriptor .
		
		?mesh meshv:treeNumber ?tn .
		FILTER(REGEX(?tn,"C"))
		}
		group by ?mesh ?cid
		
	}
}ORDER BY DESC(?countdist)

```
Quelques explications :
    - Si on découpe la requête en deux partie c'est parce que sinon on ne peut pas groupby ?mesh ?cid et aussi affichier directement le name associé car il ne s'agit pas d'un élément d'aggrégation.
    - on doit **absolument** utilisé un *distinct* sur le comptage des pmids car : 1) Un même MeSH peut être inclus plusieurs fois (ex avec différents Qualifiers) et surtout quand 1 MeSH a souvent plusieurs tree number, ce qui fait que tout cela duplique les lignes ! et si on compte direct le nombre de pmid c'est faux !!

