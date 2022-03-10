# FORVM release checklist 

### 1 -  Update vocabularies

* Ontologies that could be updated: chebi, MeSH, cheminf
* Ontologies that are stable (but do a check anyway): cito, dcterms, fabio, skos, chemont 

All the vocabularies must be placed in the same directory.
> Create an archive with the new vocabulary directory and upload it on the ftp at : ftp.semantic-metabolomics.org:/dumps/*release_date*/

### 2 - FORVM triplestore

See:

* 2 - Prepare the triplestore
* 3 - Compute chemical entities to MeSH associations
* 4 - Create the master Void
* 5 - Monitoring
* 6 - MeSH, Chemont, ChEBI and CID labels

> Upload the share.tar.gz next to the vocabulary directory at ftp.semantic-metabolomics.org:/dumps/*release_date*/

Check that the path to the *share.tar.gz* file in the ftp directory correspond to what is specified in the *void:dataDump* property for the FORVM dataset URI: <https://forum.semantic-metabolomics.org/void> in the master void.

> Update the master void.ttl

### 3 - Update the triplestore

See 5 - Monitoring for sanity checks

### 4 - FORVM raw results

> Update all the *r_fisher_q_w.csv* **and** the *metadata.txt* files in their corresponding release directory in the ftp. Eg. for CID_MESH, upload the *r_fisher_q_w.csv* and  *metadata.txt* in ftp.semantic-metabolomics.org:/CID_MESH/*release\_date*/

In the 2021's release FORVM results include: CHEBI_MESH, CHEMONT_MESH, CID_MESH, MESH_MESH, CID_SCR_Disease, MESH_SCR_Disease

Check that for each association file (*r_fisher_q_w.csv*) the path in ftp directory correspond to what is specified in the *dcat:downloadURL* property of the corresponding void.ttl. For instance in the 2021 release, the void file of the associations between CID and MeSH (at EnrichmentAnalysis/CID_MESH/2021/void.ttl) indicated <https://forum.semantic-metabolomics.org/CID_MESH/2021/data> dcat:downloadURL <ftp.semantic-metabolomics.org:/CID_MESH/2021/r_fisher_q_w.csv>

> Upload also the label directory on the ftp

### 5 - Prepare data for the upload in the database:

For all raw result files (*r_fisher_q_w.csv*) of each resource (CHEBI_MESH, CHEMONT_MESH, CID_MESH, MESH_MESH, CID_SCR_Disease, MESH_SCR_Disease):
    
> Filter by selecting significant relations (q.value <= 1e-6) The threshold could be re-evaluated if the number of associations drastically increase

> Remove the columns *TOTAL_PMID* and *p.value*

> Labels See *6 - MeSH, Chemont, ChEBI and CID labels*
>> For CHEBI: add "CHEBI:" at the beginning of each identifier (Also for label files)

>> For CHEMONT: replace the prefix "CHEMONTID_" by "C" for each identifier (Also for label files)

Warning: For molecule labels (Chebi, Chemont and pubchem) there could be some quotes (' or ") inside the label, which can disturb writing and reading csv files.