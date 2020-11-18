## Compound2MeSH :

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

So, for each section *Request_name* contains the name of the variable in a *sparql_query.py* file, containing the string of the request couting individuals. But as this request may be really time and memory consumming, it's advised to run this query in parallel. To do so, the structure of the sparql query provided in the *sparql_query.py* file is adapted to the parallelization. A first internal nested *SELECT* is used to order modalities of the Variable and use a combination of *LIMIT* and *OFFSET* clauses to divide the set of modalities in smaller sets with a size of *limit_pack_ids* for each request.

Then, each request is send in parallel with a specific sub-set. For exemple if the request is send with the *OFFSET a*, it computes the request for the *OFFSET a* 'th modality to the *OFFSET a + limit_pack_ids* 'th modality. The external *LIMIT* and *OFFSET* clauses are used to manage the pagination of outputed results by Virtuoso. Virtuoso max outputed rows is 2^20, so if for a particular sub-set there are more results, the request need to be re-send, incrementing the last offset from the maximal number of outputed lines (*limit_selected_ids*)

But in order to prepare the list of all offsets with a size of *limit_pack_ids*, that must be send, the total number of modalities of the variable must be determined. So, for each variable a request couting the total number of modalities must be provided. Like the others request, it must be set in a variable in the *sparql_queries.py* file. The name of this variable is then specified in th configuration file at the *Size_Request_name* parameter. *Counting requests* only return the count, like : 'SELECT ?COUNT WHERE { ... }'

For the coocurences query, one of the both variable should be used as a grouping variable, from which coocurences will be computed for each pack of modalities of this grouping variable. For example, if X is used as the grouping variable, the nested SELECT in the associated SPARQL query must sort X modalities and used *LIMIT* and *OFFSET* clauses to divided to total number of modalities of X in smaller groups. So, the counting request used for this request should be the same as the one provided in [X] section

A more detailed description of the configuration file is provided below.

For all computed offset of each queries, csv results outputed by Virtuoso are stored in the corresponding *out_dir* as provided in the associated section of the configuration file at *out_path*.

After all queries have been completed, all results are merged to build a global data.frame containing counts for each combination such as:
*modalility_x, modalility_y, total_counts_for_modality_x, total_counts_for_modality_y, total_counts_for_coocurences_between_x_and_y, total_number_of_individuals*. As this data.frame can be really huge and to facilitate post-processes parallelization it can be divided in smaller data.frame according to the *file_size* parameters. The order of these columns is important for the next statistical analyses, as identifiers and corpus sizes of variable $X$ modalities need to be in column 1 and 4, in column 2 and 5 for variable $Y$ modalities, their co-occurrences in column 3, and the univers size in column 6. Also, for the weakness testing, the $X$ variable is used as reference to compute the Jeffrey's CI, according to co-occurrences in column 3 and the corpus size of variable $X$ modalities in column 4.

The data.frame is printed in *df_out_dir* at *out_path*

#### config file :

- [DEFAULT]
  - split: a boolean (True/False) that indicates if the resulting table should be split in smaller parts while exporting
  - file_size: number of lines per outputed table, if split is set to True
  - request_file: the name of the *sparql_queries.py* file containg queries variable. This file **must** be place in the dedicated SPARQL directory
- [VIRTUOSO]
  - url: url of the Virtuoso SPARQL endpoint
  - graph_from: uri of data source graphs, one per line, Ex: 
             http://database/ressources/PMID_CID/2020-04-20
             http://database/ressources/reference/2020-04-19
- **X_Y**
  - name: name of the coocurences variable (ex: CID_MESH)
  - Request_name: name of the variable in sparql_queries.py containing the string of the request that will be used to count the number of individuals associated to each combinations of modalities of X and Y
  - Size_Request_name: name of the variable in sparql_queries.py containing the string of the request which will be used to count the number of modalities in the grouping variable
  - limit_pack_ids: Modality pack size that will be used to divide modalities of the grouping variable in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. Use to manage pagination (ex: 1000000). Virtuoso max is 2^20
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for coocurences
- **X**
  - name: name of the X variable (ex: CID)
  - Request_name: name of the variable in sparql_queries.py containing the string of the request that will be used to count the number of individuals associated to each modalities of X
  - Size_Request_name:  name of the variable in sparql_queries.py containing the string of the request which will be used to count the number of modalities of the variable X
  - limit_pack_ids:  Modality pack size that will be used to divide modalities of X in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. By default it can be set to limit_pack_ids + 1
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for variable X
- **Y**
  - name: name of the Y variable (ex: CID)
  - Request_name: name of the variable in sparql_queries.py containing the string of the request that will be used to count the number of individuals associated to each modalities of Y
  - Size_Request_name: name of the variable in sparql_queries.py containing the string of the request which will be used to count the number of modalities of the variable Y
  - limit_pack_ids: Modality pack size that will be used to divide modalities of Y in smaller groups to allow parallelization (ex: 10000)
  - limit_selected_ids: Maximal number of lines return by Virtuoso in one request. By default it can be set to limit_pack_ids + 1
  - n_processes: Number of processes that will be used to send queries in parallel
  - out_dir: output directory name for variable Y
- **U**
  - name: Name of the variable representing individuals (ex: PMID)
  - Size_Request_name: name of the variable in sparql_queries.py containing the string of the request which will be used to count the number of individuals in all the concerned set: that present at least one modality of variable X and one modality of variable Y

run from workdir:
```python
python3 app/metab2mesh/metab2mesh_requesting_virtuoso.py --config="/path/to/config.ini" --out="path/to/out/dir"
```
- config: path to the configuration file
- out: path to the output directory

Using the same workflow to parallelize queries, additional queries (Get MESH Names, etc ...) are provided in the additional_request.py and config parameters are the same.

