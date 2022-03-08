## Compound2MeSH :

use requesting_virtuoso.py

To compute enrichment tests and post-analyses on associations between different modalities of a variable X (ex: PubChem compounds) and another variable Y (ex: MeSH Descriptors), a contingency table must be build for each available combinations between modalities of X and Y. For example if X represent the variable *PubChem compounds*, modalities of X are the set of PubChem identifiers (CID) store in the RDF store. In the same way, if Y represent *MeSH Descriptors*, modalities of Y should be the set of available MeSH Descriptors in the current MeSH thesaurus.

To build a contingency table for a given combination of modalities between X and Y, named *x* and *y*, 4 counts are needed. These counts represent a number of publications that are associated to modalities of *x* and/or *y*. In FORUM, PMID (PubMed publications) are linked to PubChem compound by the predicate *cito:discusses* and to MeSH descritors by the predicate *fabio:hasSubjectTerm* in the RDF store.

So, the 4 needed counts to build the contingency table are :
- The total number of PMIDs having the *x* modality
- The total number of PMIDs having the *y* modality
- The total number of PMIDs having **both** the *x* and the *y* modality
- The total number of PMIDs

These 4 counts must be determined for each available combinations of *x* and *y* using SPARQL queries. To do so, in the configuration file 4 sections are provided to set parameters.

- The total number of PMIDs having the *x* modality: **[X] section**
  - The query return a csv file like: *modalility_x, total_counts_for_modality_x*. Ex: 'SELECT ?CID ?COUNT WHERE { ... }'
- The total number of PMIDs having the *y* modality: **[Y] section**
  - The query return a csv file like: *modalility_y, total_counts_for_modality_y*. Ex: 'SELECT ?MESH ?COUNT WHERE { ... }'
- The total number of PMIDs having **both** the *x* and the *y* modality: **[X_Y] section**
  - The query return a csv file like: *modality_x, modality_y, total_counts_for_coocurences_between_x_and_y*. Ex: 'SELECT ?CID ?MESH ?COUNT WHERE { ... }'. The order (*modality_x, modality_y*) is important as when building the final table, columns will be considered using the *X* variable for the first, and the *Y* variable for the second.
- The total number of PMIDs: **[U] section**

A *count request* just returns the total number of individuals (the 4 ones described above). E.g. 'SELECT ?CID  ?COUNT WHERE { ... }'
So, for each section *Request_name* contains the name of the variable in a *sparql_query.py* file, containing the string of the request to count individuals. But as this request may be really time and memory consuming, it's advised to run it in parallel. To do so, the structure of the sparql query provided in the *sparql_query.py* file is adapted to the parallelization. A first internal nested *SELECT* is used to order modalities of the Variable and use a combination of *LIMIT* and *OFFSET* clauses to divide the set of modalities in smaller sets with a size of *limit_pack_ids* for each request.

Then, each request is sent in parallel with a specific sub-set. For exeample if the request is sent with the *OFFSET a*, it computes the request for the *OFFSET a* 'th modality to the *OFFSET a + limit_pack_ids* 'th modality. The external *LIMIT* and *OFFSET* clauses are used to manage the pagination of outputted results by Virtuoso. Virtuoso max outputted rows is 2^20, so if for a particular sub-set there are more results, the request need to be re-send, incrementing the last offset from the maximal number of outputted lines (*limit_selected_ids*)

But in order to prepare the list of all offsets with a size of *limit_pack_ids*, that must be sent, the total number of modalities of the variable must be determined. So, for each variable a request counting the total number of modalities must be provided. Like the others request, it must be set in a variable in the *sparql_queries.py* file. The name of this variable is then specified in th configuration file at the *Size_Request_name* parameter.

For the co-occurences query ([X_Y]), one of the both variable should be used as a grouping variable, from which coocurences will be computed for each pack of modalities. For example, if X is used as the grouping variable, the nested SELECT in the associated SPARQL query must sort X's modalities and used *LIMIT* and *OFFSET* clauses to divided to total number of modalities of X in smaller groups. So, the counting request used for this request should be the same as the one provided in [X] section

A more detailed description of the configuration file is provided below.

For all computed offset of each query, csv results outputted by Virtuoso are stored in the corresponding *out_dir* as provided in the associated section of the configuration file at *out_path*.

After all queries have been completed, all results are merged to build a global data.frame containing counts for each combination such as:
*modalility_x, modalility_y, total_counts_for_modality_x, total_counts_for_modality_y, total_counts_for_coocurences_between_x_and_y, total_number_of_individuals*. As this data.frame can be really huge and to facilitate post-processes parallelization it can be divided in smaller data.frame according to the *file_size* and *split* parameters. The order of these columns is important for the next statistical analyses, as identifiers and corpus sizes of variable $X$ modalities need to be in column 1 and 4, in column 2 and 5 for variable $Y$ modalities, their co-occurrences in column 3, and the universe size in column 6. Also, for the weakness testing, the $X$ variable is used as reference to compute the Jeffrey's CI, according to co-occurrences in column 3 and the corpus size of variable $X$ modalities in column 4.

The data.frame is printed in *df_out_dir* at *out_path*

#### config file :

- [DEFAULT]
  - split: a boolean (True/False) that indicates if the resulting table should be split in smaller parts while exporting
  - file_size: number of lines per outputed table, if split is set to True
  - request_file: the name of the SPARQL request file containing queries, located in *app/computation/SPARQL*.
- [VIRTUOSO]
  - url: url of the Virtuoso SPARQL endpoint
  - graph_from: uri of data source graphs, one per line, Ex:
    https://forum.semantic-metabolomics.org/PMID_CID/2020
    https://forum.semantic-metabolomics.org/reference/2020-12-03
- **X_Y**
  - name: name of the coocurences variable (ex: CID_MESH)
  - Request_name: name of the variable in the SPARQL request file containing the string of the request that will be used to count the number of individuals associated to each combinations of modalities of X and Y
  - Size_Request_name: name of the variable in the SPARQL request file containing the string of the request which will be used to count the number of modalities in the grouping variable
  - limit_pack_ids: Modality pack size that will be used to divide modalities of the grouping variable in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. Use to manage pagination (ex: 1000000). Virtuoso max is 2^20
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for coocurences
- **X**
  - name: name of the X variable (ex: CID)
  - Request_name: name of the variable in the SPARQL request file containing the string of the request that will be used to count the number of individuals associated to each modalities of X
  - Size_Request_name:  name of the variable in the SPARQL request file containing the string of the request which will be used to count the number of modalities of the variable X
  - limit_pack_ids:  Modality pack size that will be used to divide modalities of X in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. By default it can be set to limit_pack_ids + 1
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for variable X
- **Y**
  - name: name of the Y variable (ex: CID)
  - Request_name: name of the variable in the SPARQL request file containing the string of the request that will be used to count the number of individuals associated to each modalities of Y
  - Size_Request_name: name of the variable in the SPARQL request file containing the string of the request which will be used to count the number of modalities of the variable Y
  - limit_pack_ids: Modality pack size that will be used to divide modalities of Y in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. By default it can be set to limit_pack_ids + 1
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for variable Y
- **U**
  - name: Name of the variable representing individuals (ex: PMID)
  - Size_Request_name: name of the variable in the SPARQL request file containing the string of the request which will be used to count the total number of individuals (presenting at least one modality of variable X and one modality of variable Y)
  - limit_pack_ids: Modality pack size that will be used to divide modalities of U in smaller groups to allow parallelization (ex: 100000)
  - limit_selected_ids: 2
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for variable Y

run from workdir:
```python
python3 app/computation/requesting_virtuoso.py --config="/path/to/config.ini" --out="path/to/out/dir"
```
- config: path to the configuration file
- out: path to the output directory
