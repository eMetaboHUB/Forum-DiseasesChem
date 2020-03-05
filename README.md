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
