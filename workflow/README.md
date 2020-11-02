## Requierements:

- Check that the docker virtuoso image is installed :
If not 
  - Pull tenforce/Virtuoso image: 
  ```bash
  docker pull tenforce/virtuoso
  ``` 

Two possibility to build the triple store:
    - You can use the docker-image provided which contains all needed packages and librairies.
    - or you can execute them on your own environment, but check that all needed packages are installed.

if you want to use the docker image, first build it :

```bash
docker build -t forum/processes .
```

Then, launch it:

```bash
docker run --name forum_scripts --rm -it --network="host" \
-v /path/docker-virtuoso/share:/workdir/share-virtuoso \
-v /path/to/data/dir:/workdir/out \
forum/processes bash
```

### 1) Build the initial triple store

Before building the triplestore, you need to create 2 directory:
    - the **data** directory: it will contain all analysis result files, such as *Compound - MeSH* associations
    - the **docker-virtuoso** directory: it will contains the Virtuoso session files and data
      - a **share** sub-directory: It will contains all data that need to be loaded in the Virtuoso triple store. This sub-directory will be bind to the *dump* directory of the Virtuoso docker image, to ensure data loading.

So, for instance, you can execute:
```
mkdir data
mkdir docker-virtuoso/share
```

**Warnings:** If you use the docker forum/processes, you should use in your commands directories that bind on the previously created directories: *data* and *docker-virtuoso/share*, instead of using ./data and ./docker-virtuoso/share in the next examples.

To build the intial triple-store, you can use the script w_buildTripleStore.sh

There are two configuration files related to this step:
- The first contains parameters about the creation of the triple store. See README in the *build_RDF_store* sub-directory for option details.
- The second contains parameters to integrate chemont classes in the triple store. See README in the *build_RDF_store* sub-directory for option details.

From *metdiseasedatabase* directory execute: 

```bash
 ./workflow/w_buildTripleStore.sh -b path/to/building/config -c path/to/chemont/config -v version -p mdpForum -s path/to/virtuoso/shared/directory
```
eg.:

```bash
./workflow/w_buildTripleStore.sh -b app/build_RDF_store/config/config.ini -c app/ChemOnt/config/2020-08-14/config.ini -p mdpForum -s ./docker-virtuoso/share
```

- *Option details:*
  - b: path to the config file of build_rdf_store (eg. app/build_RDF_store/config/config.ini)
  - c: path to the config file of Chemont processes (eg.  app/ChemOnt/config/version/config.ini)
  - v: The version of the analysis. This is optional, if nothing is set, the date will be used
  - p: pydio password to get data
  - s: path to the Virtuoso shared directory (eg ./docker-virtuoso/share)

This process should have created several sub-directories in the Virtuoso shared directory: ClassyFire, MeSH, MetaNetX, PMID_CID, PMID_CID_endpoints, PubChem_Compound, PubChem_Descriptor, PubChem_InchiKey, PubChem_References, vocabulary

**Warnings:** This procedure creates two upload files: pre_upload.sh and upload_data.sh.
pre_upload.sh is a light version of upload_data.sh which is loading only needed data to compute associations. It does only load a small part of PubChem Compound graph, setting compound types, and does not load PubChem Descriptor graph, which are huge graphs. This light upload version can be used to have light version of the RDF store, without all information about compounds, as it need approximately 500 G0 of RAM to load all graphs ! Thus, these both upload files contains duplicates information and **must not** be uploaded on the same Virtuoso session ! 

### Compute chemical entities to MeSH assoctions

Once the initial data of the triple store have been created, an intial session of the Virtuoso triple store must be started in order to compute associations between chemical entities and MeSH descriptors.

#### Initialyze Virtoso session

To start the virtuoso session, use: 
```bash
./workflow/w_virtuoso.sh -d /path/to/virtuoso/dir -s /path/to/share/dir/from/virtuoso/dir start
```

eg.
```bash
workflow/w_virtuoso.sh -d ./docker-virtuoso -s share start
```

- *Option details:*
  - d: path to the virtuoso directory (eg. ./docker-virtuoso)
  - s: path to the shared directory **from** the virtuoso directory (eg. *share* if you use the proposed settings)

Several checks can be used to ensure that the loading was done correctly:

1) At the end of each laoding file, Virtuoso execute the command *select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;*. Globally, it asks Virtuoso to return graphs for which there was an error during rdf loading. Check that this request doesn't return any results ([Virtuoso Bulk Loading RDF](http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader#Checking%20bulk%20load%20status))

2) Several request will be send against the Virtuoso endpoint during the process, you can check that the central requests are working well. A good start could be to check requests used in the *X_Y* part of the process (Cf. configuration files), such as: *count_distinct_pmids_by_CID_MESH*, *count_distinct_pmids_by_ChEBI_MESH*, *count_distinct_pmids_by_ChemOnt_MESH*. In doing so, be sure to add the content of the prefix variable at the beginning of your request and use only the first 100 elements for instance by setting *limit* and *offset* paramenters to 100 and 0 for instance. The first '%s' refers to the graphs that should be used in the request but this can be removed for tests.

3) TODO: Implement tests

#### Set configuration files: 

For each analysis, there are two main configuration files: 
- The first refer to parameters required during the requesting process. See README in the *metab2mesh* sub-directory for option details.
- The second refer to parameters required in the conversion process of association results to RDF triples. See README in the *Analyzes/Enrichment_to_graph* sub-directory for option details.

#### Computation

To compute associations between chemical entities and MeSH descriptors, you can use: w_compound2mesh.sh

*Option details:*
  - v: version of the analysis. This is optional, if nothing is set, the date will be used
  - m: path to the configuration file of the analysis requesting Virtuoso
  - t: path to the configuration file to convert association to triples
  - u: name of the computed ressource
  - d: path to the data directory
  - s: path to the Virtuoso shared directory

For each analysis: all results and intermediary data will be exported in a dedicated sub-directory named as the ressource (option u).
In this sub-directory, you can find count data associated with Chemical entities, MeSH descriptors and their co-occurrences.
In the sub-directory results, you can find the table that resume counts for each associations.

The files:
- r_fisher.csv: correspond to the table containing results of the fisher exact test.
- r_fisher_q.csv: correspond to the results with computed *q-value* for each association.
- r_fisher_q_w.csv: correspond to the results with the fragility index

At the end of this procedure all significant associations, according to the threshold in the configuration file, are converted in a triple formalism 




##### Compute PubChem compounds - MeSH associations

```bash
./workflow/w_compound2mesh.sh -v version -m /path/to/config/Compound2MeSH -t path/to/config/triplesConverter/Compound2MeSH -u CID_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir
```
eg.:
```bash
./workflow/w_compound2mesh.sh -v 2020-10-10 -m app/metab2mesh/config/CID_MESH/2020-10-10/config.ini -t app/Analyzes/Enrichment_to_graph/config/CID_MESH/2020-10-10/config.ini -u CID_MESH -d ./data -s ./docker-virtuoso/share
```


##### Compute ChEBI - MeSH associations

```bash
./workflow/w_compound2mesh.sh -v version -m /path/to/config/ChEBI2MeSH -t path/to/config/triplesConverter/ChEBI2MeSH -u CHEBI_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir
```

eg.:
```bash
./workflow/w_compound2mesh.sh -v 2020-10-10 -m app/metab2mesh/config/CHEBI_MESH/2020-10-10/config.ini -t app/Analyzes/Enrichment_to_graph/config/CHEBI_MESH/2020-10-10/config.ini -u CHEBI_MESH -d ./data -s ./docker-virtuoso/share
```

##### Compute Chemont - MeSH associations

```bash
./workflow/w_compound2mesh.sh -v version -m /path/to/config/Chemont2MeSH -t path/to/config/triplesConverter/Chemont2MeSH -u CHEMONT_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir
```

eg.:
```bash
./workflow/w_compound2mesh.sh -v 2020-10-10 -m app/metab2mesh/config/CHEMONT_MESH/2020-10-10/config.ini -t app/Analyzes/Enrichment_to_graph/config/CHEMONT_MESH/2020-10-10/config.ini -u CHEMONT_MESH -d ./data -s ./docker-virtuoso/share
```

#### Shutdown Virtoso session

When all computations have been achieved, the temporary Virtuoso session can be down, using: 

```bash
./workflow/w_virtuoso.sh -d /path/to/virtuoso/dir -s /path/to/share/dir/from/virtuoso/dir stop
./workflow/w_virtuoso.sh -d /path/to/virtuoso/dir -s /path/to/share/dir/from/virtuoso/dir clean
```
eg.:
```bash
workflow/w_virtuoso.sh -d ./docker-virtuoso -s share stop
workflow/w_virtuoso.sh -d ./docker-virtuoso -s share clean
```

New directory *Analyzes* should have been created at the end of the process in the virtuoso shared directory, instanciating associations between chemical entities and MeSH in a triple formalism, which can be then be load in a Virtuoso triple store to explore relations.

In the data directory, you can also retrived all processed results, such as the final results table: *r_fisher_q_w.csv* in each related directory

End !

#### Build a custom triple store

To build a custom triple store, you need to start a new virtuoso session. You can use the docker-compose file created in the docker-virtuoso directory by w_buildTripleStore.sh or build your own with different parameters.
Start Virtuoso:

```bash
docker-compose up -d -f docker-compose.yml
```

To load data, you can use the following commands: 

```bash
# Get Virtuoso container name
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
# Load data in upload file
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/upload.sh'
```