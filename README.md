## Metabolite - Diseases Graph Database

This repository contains some usefull methods to provides links between PubChem compound identifiers, litteratures (PMIDs) and MeSH

*GetCID_PMID_associations* is the main test file, where I test the developped functions.

-   **The Ensemble_pccompound object:** This objects provide a way to fetch the pmids associated to a list of PubChem compounds (CID).
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

```python
Ensemble_pccompound.export_cids_pmids_triples_ttl(output_file)
```
-   ```output_file```: /path/to/triple/file

This function create a turtle (.ttl) to represent all the cid - pmids associations contained in the Ensemble_pccompound objects, just as PubChem does. Subjects represent cid (compound prefix), predicate is a property derived from the cito ontology (cito:isDiscussedBy) and object represent pmid (reference prefix)
```
@prefix cito:	<http://purl.org/spar/cito/> .
@prefix compound:	<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/> .
@prefix reference:	<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> .
compound:CID11355423	cito:isDiscussedBy	reference:PMID29559686 ,
```
```python
Ensemble_pccompound.export_cid_pmid_endpoint(output_file)
```
This function allow to export triples in a turtle syntax linking the cid-pmid associations to the contributors who provide this association.
For each cid - pmid association, information are organized as follows:
```
@prefix endpoint:	<http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/> .
@prefix cito:	<http://purl.org/spar/cito/> .
@prefix obo:	<http://purl.obolibrary.org/obo/> .
@prefix compound:	<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/> .
@prefix reference:	<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> .
@prefix dcterms:	<http://purl.org/dc/terms/> .
endpoint:CID11355423_PMID29559686	obo:IAO_0000136	compound:CID11355423 ;
		cito:citesAsDataSource	reference:PMID29559686 ;
		dcterms:contributor	"pccompound_pubmed_mesh" .
```
```obo:IAO_0000136``` represent a *is_about* link

So as exemple, to get all the literature association for two PubChem compoound such as Galactose (cid:6036) and (KDO)2-lipid A (cid:11355423) :

```python
apiKey = "0ddb3479f5079f21272578dc6e040278a508"
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)

new_Ensemble_pccompound = Ensemble_pccompound()
new_Ensemble_pccompound.append_pccompound("11355423", query_builder)
new_Ensemble_pccompound.append_pccompound("6036", query_builder)

new_Ensemble_pccompound.export_cids_pmids_triples_ttl("cid_to_pmids.ttl")
new_Ensemble_pccompound.export_cid_pmid_endpoint("cid_to_pmids_endpoint.ttl")

all_pmids = new_Ensemble_pccompound.get_all_pmids()
all_cids = new_Ensemble_pccompound.get_all_cids()
```
* * *
```parse_pubchem_RDF``` is a function which is designed to parse the PubChem RDF triples files to only extract triples involving a identifier as Subject

```parse_pubchem_RDF(PubChem_ref_folfer, all_ids, prefix, out_dir)```
- ```PubChem_ref_folfer```: a path to folder containing all PubChem RDF files to parse in a .ttl.gz format
- ```prefix```:  the prefix associated to the selected identifiers (*compound:CID* for cid, *reference:PMID* for pmids, etc ...) 
- ```all_ids```: identfiers used to parse the triples
- ```out_dir```: a path to a folder to write the filtered turtle files.

To parse PubChem reference RDF files, the ```PubChem_ref_folfer``` can be dowload with ```wget -r -A ttl.gz -nH --cut-dirs=2 ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference```
As Exemple, to get all the triples describing the pubmed publications (such as *reference2mesheading*, *date*, *title*, etc ...) for the studied compound (Galactose and (KDO)2-lipid A)
```python
parse_pubchem_RDF("data/PubChem_References/reference/", all_pmids, "reference:PMID", "pccompound_references_filtered/")
```

Also, to parse PubChem RDF Compound files, we can use:
```python
parse_pubchem_RDF("data/PubChem_compound/", all_cids, "compound:CID", "pccompound_filered/")
```
PubChem Compound files can be found at ```ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/compound/general/``` (In my cas i'm only interested in the file: pc_compound_type.ttl.gz which contains information about the *rdf:type* of the compound using the ChEBI Ontology)

* * *
The main issue about PubChem RDF Reference files provided in the ftp server, is that they only provide triples with the *fabio:hasSubjectTerm* predicates, which correspond to secondary mesh associated to the pmid but don't provide the *fabio:hasPrimarySubjectTerm* which represent the main topics of the artcile, which is an import source of information.


The function ```REST_ful_bulk_download``` is designed to send request to the PubChem RDFful REST server and get this missing information. Using a specified domain and predicate a request will be send to get all the associated triples. But, the server can't send more than 10000 records at the same time, so the function will export each packets of 10000 triples in different files and increment the offset parameter o the request until get all the triples. The function return a list of offsets for which there was a server errors (HTTP status > 200), for which it would be necessary to relaunch the function.

```REST_ful_bulk_download(graph, predicate, out_dir, start_offset)```
-   ```graph```: the domain associated to the triples
-   ```predicate```: the predicate to the triples
-   ```out_dir```: the path to write the triples files
-   ```start_offset```: the offset to start (by default 0)
If for any reasons the function failed, the function can be restarted at the last offset using the ```start_offset``` parameter.
As, example, to get all the triples containing the *fabio:hasPrimarySubjectTerm* predicate, we can use: 

```python
requests_failed = REST_ful_bulk_download(graph = 'reference', predicate = 'fabio:hasPrimarySubjectTerm', out_dir = 'data/PubChem_PrimarySubjectTermsTriples/', start_offset = 0)
```
With this function 52178606 of triples involving a pmid and a mesh with the predicate *fabio:hasPrimarySubjectTerm* was found.
After this, all the files may be collapse as one, compress and send to the function ```parse_pubchem_RDF``` to only extract thoose for which we have an associated PubChem CID.