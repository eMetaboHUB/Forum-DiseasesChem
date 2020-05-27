## Metabolite - Diseases Graph Database

This repository contains some usefull methods to provides links between PubChem compound identifiers, litteratures (PMIDs) and MeSH

## Install
### Install Docker Virtuoso :

- Pull tenforce/Virtuoso image: 
```bash
docker pull tenforce/virtuoso
```
Documentation at https://hub.docker.com/r/tenforce/virtuoso

### Build metdisease Docker :

```bash
docker build -t forum/metdisease .
```

### Run
```bash
docker run --rm -it --network="host" \
-v path/to/docker-ressource:/workdir/data \
-v path/to/config/dir:/workdir/config \
-v /path/to/virtuoso-share/dir:/workdir/share-virtuoso \
-v /path/to/out/dir:/workdir/out/ \
forum/metdisease bash
```

## Build RDF Store:
Use build_RDF_store.py
This process is used to build a complete RDF Store containing data graphs from PubChem Compounds, PubChem References, PubChem Descriptors, MeSH and to identify links between PubChem compounds (CID) and PubMed publications (PMIDS). If needed, only certain data graphs can be selected and dowloaded.
A version is always attach to a data graph.

For PubChem and MeSH ressources, this version is determine from the modification date of concerned files on the ftp server. If the last version of the ressource has already been downloaded, the program will skip this step.

For the ressource describing links between PubChem Compounds and PubMed publications, the version can be define by the user. If nothing is set, the date will be used by default. Like previous ressources, if the version have already been created, the program will skip the step. To allow overwrting, be sure to delete the associated directory in the *additional_files*.

The *additional_files* directory contains lists of identifires treated by the program and caches metadata files, which can be used as back-up by the program if exit too early. 
This directory contains :
  - all_linked_ids: a list of all the linked identifiers found by the Elink process (ex: PubChem Compounds identifiers)
  - all_linking_ids.txt: a list of all input identifiers used in the Elink process for which available links to linked_ids will be determined
  - linking_ids_request_failed.txt: a list of all linking ids for which the request failed (Timeout, Server Errors, etc ...). At the end of the process this list must be empty
  - linking_ids_without_linked_ids.txt: a list of all the linking identifiers for which at least one link to a linked identifier was found
  - successful_linking_ids.txt: a list of all the linking identifiers for which no link to a linked identifier was found
  - s_metdata.txt: a cache metadata file which may also be used for back-up.

To faciliate to loading of these data graph in Virtuoso the output directory should be the share directory of Virtuoso, corresponding to his *dumps* directory.

At the end of the process, a *upload.sh* file is also build in the output directory. This file contains all the *ISQL* commands that should be execute by Virtuoso to properly load all graphs and metadata.

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/upload.sh'
```

#### Config file:

- [GENERAL]
  - path_out: /path/to/output/directory. Shoud be /workdir/share-virtuoso/ which have to be mapped to the dumps directory of Virtuoso, corresponding to his *dumps* directory
- [MESH]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - out_dir_name: output directory name (ex: MeSH)
- [COMPOUND]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - out_dir_name: output directory name (ex: PubChem_compound)
  - dir_on_ftp: path to associated directory from *ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/* at PubChem ftp server (ex: compound/general)
  - ressource_name: name of the ressource as specified in the void.ttl file of PubChem (ex: compound)
- [DESCRIPTOR]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - out_dir_name: output directory name (ex: PubChem_Descriptor)
  - dir_on_ftp: path to associated directory from *ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/* at PubChem ftp server (ex: descriptor/compound)
  - ressource_name: name of the ressource as specified in the void.ttl file of PubChem (ex: descriptor)
- [REFERENCE]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - out_dir_name: output directory name (ex: PubChem_References)
  - dir_on_ftp: path to associated directory from *ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/* at PubChem ftp server (ex: reference)
  - ressource_name: name of the ressource as specified in the void.ttl file of PubChem (ex: reference)
- [ELINK]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - run_as_test: a boolean (True/False) indicating if the Elink processes have to be run as test (only the first 30000 pmids) or full
  - pack_size: the number of identifiers that will be send in the Elink request. For CID - PMID, 5000 is recommended. (please refer to https://eutils.ncbi.nlm.nih.gov/entrez/query/static/entrezlinks.html)
  - api_key: an apiKey provided by a NCBI account 
  - version: The version of the builded ressource. If nothing is indicated, date will be used
  - timeout: The period (in seconds) after which a request will be canceled if too long. For CID - PMID, 600 is recommended.
  - additional_files_out_path: a path to a directory where the *additional_files* directory will be created.
  - max_triples_by_files: The maximum number of associations exported in a file. For CID - PMID, 5000000 is recommended.

run from workdir:
```python
python3 app/build_RDF_store/build_RDF_store.py --config="/path/to/config_file.ini"
```

## metab2mesh :
use metab2mesh_requesting_virtuoso.py

To compute enrichment tests and post-analysis on associations between differents modalities of a variable X (ex: PubChem compounds) and an other variable Y (ex: MeSH Descriptors), a contengency table must be build for each available combinations between modalities of X and Y. For exemple if X represent the variable *PubChem compounds*, modalities of X are the set of PubChem identifiers (CID) store in the RDF store. In the same way, if Y represent *MeSH Descriptors*, modalities of Y should be the set of available MeSH Descirptors in the current MeSH thesaurus.
To build a contengency table for given combination of modalities between X and Y, named *x* and *y*, 4 counts are needed. This counts represent a number of individuals which have properties associated to modalities of *x* and/or *y*. In the previous example, PMID (PubMed publications) should be used as individuals as they are linked to PubChem compound by a propery *cito:discusses* and linked to MeSH by the property *fabio:hasSubjectTerm* in the RDF store.
So, the 4 needed counts to build the contengency table are :
- The total number of individuals (pmids) having the *x* modality
- The total number of individuals (pmids) having the *y* modality
- The total number of individuals (pmids) having **both** the *x* and the *y* modality
- The total number of individuals (pmids) having at least one modalirty of X and one modality of Y

This 4 counts must be determine for each available combinations of *x* and *y* using SPARQL queries. To do so, in the configuration file 4 sections are provided to set parameters for each of this 4 needed SPARQL queries

- The total number of individuals (pmids) having the *x* modality: **[X] section**
  - The query return a csv file like: *modalility_x, total_counts_for_modality_x*. Ex: 'SELECT ?CID ?COUNT WHERE { ... }'
- The total number of individuals (pmids) having the *y* modality: **[Y] section**
  - The query return a csv file like: *modalility_y, total_counts_for_modality_y*. Ex: 'SELECT ?MESH ?COUNT WHERE { ... }'
- The total number of individuals (pmids) having **both** the *x* and the *y* modality: **[X_Y] section**
  - The query return a csv file like: *modalility_x, modaliity_y, total_counts_for_coocurences_between_x_and_y*. Ex: 'SELECT ?CID ?MESH ?COUNT WHERE { ... }'
- The total number of individuals (pmids) having at least one modality of X and one modality of Y: **[U] section**
  - A *counting request* which just return the total number of individuals. Ex: 'SELECT ?COUNT WHERE { ... }'

So, for each section *Request_name* contains the name of the variable in the sparql_query.py file, containing the string of the request couting individuals. But as this request may be really time and memory consumming, it's advised to run this query in parallel. To do so, the structure of the sparql query provided in the sparql_query.py file is adapted to the parallelization. A first internal nested *SELECT* is used to order modalities of the Variable and use a combination of *LIMIT* and *OFFSET* clauses to divide the set of modalities in smaller sets with a size of *limit_pack_ids* for each request.

Then, each request is send in parallel with a specific sub-set. For exemple if the request is send with the *OFFSET a*, it computes the request for the *OFFSET a* 'th modality to the *OFFSET a + limit_pack_ids* 'th modality. The external *LIMIT* and *OFFSET* clauses are used to manage the pagination of outputed results by Virtuoso. Virtuoso max outputed rows is 2^20, so if for a particular sub-set there are more results, the request need to be re-send, incrementing the last offset from the maximal number of outputed lines (*limit_selected_ids*)

But in order to prepare the list of all offsets with a size of *limit_pack_ids*, that must be send, the total number of modalities of the variable must be determined. So, for each variable a request couting the total number of modalities must be provided. Like the others request, it must be set in a variable in the *sparql_queries.py* file. The name of this variable is then specified in th configuration file at the *Size_Request_name* parameter. *Counting requests* only return the count, like : 'SELECT ?COUNT WHERE { ... }'

For the coocurences query, one of the both variable should be used as a grouping variable, from which coocurences will be computed for each pack of modalities of this grouping variable. For example, if X is used as the grouping variable, the nested SELECT in the associated SPARQL query must sort X modalities and used *LIMIT* and *OFFSET* clauses to divided to total number of modalities of X in smaller groups. So, the counting request used for this request should be the same as the one provided in [X] section

A more detailed description of the configuration file is provided below.

For all computed offset of each queries, csv results outputed by Virtuoso are stored in the corresponding *out_dir* as provided in the associated section of the configuration file at *out_path*.

After all queries have been completed, all results are merged to build a global data.frame containing counts for each combination such as:
*modalility_x, modalility_y, total_counts_for_modality_x, total_counts_for_modality_y, total_counts_for_coocurences_between_x_and_y, total_number_of_individuals*. As this data.frame can be reallu huge and to facilitate post-processes parallelization it can be divided in smaller data.frame according to the *file_size* parameters

The data.frame is printed in *df_out_dir* at *out_path*

#### config file :

- [DEFAULT]
  - out_path = /path/to/output/directory/
  - df_out_dir = name of metab2mesh data.frame output directory
  - file_size = number of lines per outputed data.frames
- [VIRTUOSO]
  - url = url of the Virtuoso SPARQL endpoint
  - graph_from = uri of data source graphs, one per line, Ex: 
             http://database/ressources/PMID_CID/2020-04-20
             http://database/ressources/reference/2020-04-19
- [X_Y]
  - name: name of the coocurences variable (ex: CID_MESH)
  - Request_name: name of the variable in sparql_queries.py containing the string of the request that will be used to count the number of individuals associated to each combinations of modalities of X and Y
  - Size_Request_name: name of the variable in sparql_queries.py containing the string of the request which will be used to count the number of modalities in the grouping variable
  - limit_pack_ids: Modality pack size that will be used to divide modalities of the grouping variable in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. Use to manage pagination (ex: 1000000). Virtuoso max is 2^20
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for coocurences
- [X]
  - name: name of the X variable (ex: CID)
  - Request_name: name of the variable in sparql_queries.py containing the string of the request that will be used to count the number of individuals associated to each modalities of X
  - Size_Request_name:  name of the variable in sparql_queries.py containing the string of the request which will be used to count the number of modalities of the variable X
  - limit_pack_ids:  Modality pack size that will be used to divide modalities of X in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. By default it can be set to limit_pack_ids + 1
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for variable X
- [Y]
  - name: name of the Y variable (ex: CID)
  - Request_name: name of the variable in sparql_queries.py containing the string of the request that will be used to count the number of individuals associated to each modalities of Y
  - Size_Request_name: name of the variable in sparql_queries.py containing the string of the request which will be used to count the number of modalities of the variable Y
  - limit_pack_ids: Modality pack size that will be used to divide modalities of Y in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. By default it can be set to limit_pack_ids + 1
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for variable Y
- [U]
  - name = Name of the variable representing individuals (ex: PMID)
  - Size_Request_name = name of the variable in sparql_queries.py containing the string of the request which will be used to count the number of individuals in all the concerned set: that present at least one modality of variable X and one modality of variable Y

run from workdir:
```python
python3 app/metab2mesh/metab2mesh_requesting_virtuoso.py --config="/path/to/config.ini/file"
```

Using the same workflow to parallelize queries, additional queries (Get MESH Names, etc ...) are provided in the additional_request.py and parameters are the same.