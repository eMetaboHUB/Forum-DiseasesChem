## Metab2mesh

### First Step: Extarct data from RDF Store and create data.frame :
Construction of the contingency table, needed to execute enrichment tests (like fisher, chi2, ...) is based on the number of coocurences between two set of elements.  For each indivual in an the ensembl **X** (Ex: PubChem Compounds) and each individuals in an ensembl **Y** (Ex: MeSH) a set of publications mentionning them and the intersection of this two set will be used to build the contigency table. 
There is a lot of combinations between the differents individuals of each ensembl and this type of requests may be really time and memory consuming if it is realized in a single request and so, need to be parallelized. This huge request can be divide in sub-requests each one dealing with a precise number of individuals of the set **X** and lookig for all the coocurences with all indivduals of the set **Y** (or reciprocally from a group of **Y** indivuduals to all indivuduals of **X**).
So to extract intersections, there is one of the two sets that must be choose as a starting point, from which all individuals will be divided in groups and then, smaller groups will be treated in parallel. 

After getting all the intersection, the size of each set of individuals in the **X** and **Y** ensembl must be compute. This requests can also be paralelized and the starting point ensembl, is the ensembl itself.

Finaly, to complete the data needed to build the contingency table, the total size of the universe must be computed.

The configuration of the parallelization of the four needed requests is describe below:

 - The configuration file (.ini):
   - *DEFAULT Section:*
     - out_path: path_to_out_directory
     - df_out_dir: directory name where finals dataframes will be saved
     - file_size: the final dataframe may be really huge and to allow parallelization for next steps it can divide into several files with *file_size* as number of lines
   - *VIRTUOSO Section:*
     - url: the url of the sparql endpoint (Ex: http://localhost:9980/sparql/)
   - *QUERY Section:*
     - [X_Y] represent the intersection of two sets of elements associated to an individual in the ensembl **X** and an individual in an ensembl **Y**.
        - name: the name of the intersection (Ex CID_MESH)
        - Request_name: the request which extract the number of coocurences, and return the identifier of the individuals of **X**, **Y** and the number of coocurences 
        - Size_Request_name: the request which give the total number of individuals from the ensembl (**X** or **Y**) choosed to be the starting point and which is going to be divided and compute in parallel
        - limit_pack_ids = the number of individuals in one group (max is 2^20). If limit_pack_ids bigger than the number of individuals, the request is not send as parralel
        - limit_selected_ids = the maximum number of results that is allow to be returned by one request (Virtuoso max is 2^20)
        - n_processes = the number of groups that will be treated in parallel
        - out_dir = the name of the output directory
      - [X] represent the size size of each set in the ensembl **X**
        - name: the name of the ensembl **X** (Ex: CID)
        - Request_name: the request which return the identifier of the individuals of **X** and the size of the set, for each given individuals
        - Size_Request_name: the request which give the total number of individuals from the ensembl **X**
        - limit_pack_ids = the number of individuals in one group (max is 2^20). If limit_pack_ids bigger than the number of individuals, the request is not send as parralel
        - limit_selected_ids = the maximum number of results that is allow to be returned by one request (Virtuoso max is 2^20)
        - n_processes = the number of groups that will be treated in parallel
        - out_dir = the name of the output directory
      - [Y] represent the size size of each set in the ensembl **Y**
        - name: the name of the ensembl **Y** (Ex: CID)
        - Request_name: the request which return the identifier of the individuals of **X** and the size of the set, for each given individuals
        - Size_Request_name: the request which give the total number of individuals from the ensembl **Y**
        - limit_pack_ids = the number of individuals in one group (max is 2^20). If limit_pack_ids bigger than the number of individuals, the request is not send as parralel
        - limit_selected_ids = the maximum number of results that is allow to be returned by one request (Virtuoso max is 2^20)
        - n_processes = the number of groups that will be treated in parallel
        - out_dir = the name of the output directory
      - [U]
        - name: the name of elements that compose the univers (Ex: PMID)
        - Size_Request_name = the request which give the total number of elements

Finaly, all requests must be store in the sparql_qeuries.py and declare with the name used in the configuration file, Ex:

```python
count_distinct_pmids_by_CID = """
select ?CID ?count
where
{
    {
        select ?CID ?count
        where
        {
            {
                select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (count(distinct ?pmid) as ?count) 
                where 
                {
                    {
                        select ?cid 
                        where 
                        {
                            {
                                select distinct ?cid where
                                {
                                    ?cid cito:isDiscussedBy ?pmid .
                                }
                                order by ?cid
                            }
                        }
                        limit %d
                        offset %d
                    }
                    ?cid cito:isDiscussedBy ?pmid .
                    ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                    ?mesh a meshv:TopicalDescriptor .
                    ?mesh meshv:treeNumber ?tn .
                    FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                }
                group by ?cid
            }
        }
        order by ?CID
    }
}
limit %d
offset %d
"""

count_number_of_CID = """
    select (count(distinct ?cid) as ?count_CID)
    where 
    {
        ?cid cito:isDiscussedBy ?pmid .
    }
"""
```
To allow parallelization each request must be build in two different blocs organized around the *OFFSET* and *LIMIT* clauses. In the innermost bloc there is a sub-query that allow to select the current group of individuals (with a size of *limit_pack_ids*) from the starting ensembl using the the *OFFSET* and *LIMIT* clauses. This set of individuals is then used in the external part of the queries.
The *OFFSET* and *LIMIT* clauses in the outermost part of the query allow to deal with pagination when the number of results exceed the *limit_selected_ids*.

To build the contingency table and compute tests, use scripts in post-processes:
- compute_fisher_exact_test.R: to compute all the needed tests in parallel
- post_process_metab2mesh: to build the final table

Also, other types of request can be send using this process and the configuration file.
This type of request can be store and launch using *additional_requests.py*
For example, in the name way the request extracting the label of each MeSH term may be send in parallel as follow:

```python
[MESH_NAMES]
name = MESH_label
Request_name = MESH_name
Size_Request_name = count_number_of_MESH
limit_pack_ids = 3000
limit_selected_ids = 3001
n_processes = 8
out_dir = MESH_NAMES2


MESH_name = """
select ?MESH str(?str_f_label)
where
{
    {
        select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) MIN(str(?label)) as ?str_f_label
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
                            ?mesh meshv:treeNumber ?tn .
                            FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                        }
                        order by ?mesh
                    }
                }
                limit %d
                offset %d
            }
        ?mesh rdfs:label ?label
        }
        group by ?mesh
        order by ?mesh
    }
}
limit %d
offset %d
"""

count_number_of_MESH = """
    select (count(distinct ?mesh) as ?count_MESH) 
    where 
    {
        ?mesh a meshv:TopicalDescriptor .
        ?mesh meshv:treeNumber ?tn .
        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
    }
"""
```