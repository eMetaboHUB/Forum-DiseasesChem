## Requirements:

- Check that the docker virtuoso image is installed :
If not 
  - Pull tenforce/Virtuoso image: 
```bash
  docker pull tenforce/virtuoso
``` 

Before building the triplestore, you need to create two directories:
    - the **data** directory: it will contain all analysis result files, such as *Compound - MeSH* associations
    - the **docker-virtuoso** directory: it will contain the Virtuoso session files and data
      - a **docker-virtuoso/share** sub-directory: It will contain all data that need to be loaded in the Virtuoso triplestore. This sub-directory will be bind to the *dump* directory of the Virtuoso docker image, to ensure data loading.

So, for instance, you can execute:
```
mkdir data
mkdir -p docker-virtuoso/share
```

Two possibility to build the triplestore:
    - You can use the docker-image provided which contains all needed packages and libraries.
    - or you can execute them on your own environment, but check that all needed packages are installed.

If you want to use the docker image, first build it :

```bash
docker build -t forum/processes .
```

Then, you can launch it using:

```bash
docker run --name forum_scripts --rm -it --network="host" \
-v /path/docker-virtuoso/share:/workdir/share-virtuoso \
-v /path/to/data/dir:/workdir/out \
forum/processes bash
```
**Warnings:** Be sure to map the docker-virtuoso/share and the data directory inside your forum/processes container.
Also, if you use the docker forum/processes, you should use in your commands,  directories that bind on the previously created directories: *data* and *docker-virtuoso/share*, instead of using ./data and ./docker-virtuoso/share in the next examples.

### Prepare the triplestore

To build the initial triplestore, you can use the script w_buildTripleStore.sh

There are two configuration files related to this step:
- The first contains parameters about the creation of the triplestore. See README in the *build_RDF_store* sub-directory for option details.
- The second contains parameters to integrate chemont classes in the triplestore. See README in the *Chemont* sub-directory for option details.

Then, from *metdiseasedatabase* directory execute: 

```bash
 ./workflow/w_buildTripleStore.sh -b path/to/build_RDF_store/config -c path/to/Chemont/config -v version -p mdpForum -s path/to/virtuoso/shared/directory
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
pre_upload.sh is a light version of upload_data.sh which is loading only data needed to compute associations. Thus, it does only load a small part of PubChem Compound graph, setting compound types, and does not load PubChem Descriptor graph, which are huge graphs. This light upload version can be used to have a light version of the RDF triplestore, without all information about compounds, as it need approximately 500 G0 of RAM to load all graphs ! But, these both upload files contains duplicate information and **must not** be loaded on the same Virtuoso session ! 

### Compute chemical entities to MeSH assoctions

Once the initial data of the triplestore have been created, an initial session of the Virtuoso triplestore must be started in order to compute associations between chemical entities and MeSH descriptors.

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
  - d: path to the virtuoso directory. Here, it is advised to set the absolute path.
  - s: path to the shared directory **from** the virtuoso directory (eg. *share* if you use the proposed settings)

Several checks can be used to ensure that the loading was done correctly:

1) At the end of each laoding file, Virtuoso execute the command *select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;*. Globally, it asks Virtuoso to return graphs for which there was an error during rdf loading. Check that this request doesn't return any results ([Virtuoso Bulk Loading RDF](http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader#Checking%20bulk%20load%20status))

2) Several requests will be sent against the Virtuoso endpoint during the process, you can check that the central requests are working well. A good start could be to check requests used in the *X_Y* part of the process (Cf. configuration files), such as: *count_distinct_pmids_by_CID_MESH*, *count_distinct_pmids_by_ChEBI_MESH*, *count_distinct_pmids_by_ChemOnt_MESH*. In doing so, be sure to add the content of the prefix variable at the beginning of your request and use only the first 100 elements for instance by setting *limit* and *offset* parameters to 100 and 0 for instance. The first '%s' refers to the graphs that should be used in the request (the *FROM* part of the sparql request) but this can be removed for tests.

3) TODO: Implement tests

#### Set configuration files: 

For each analysis, there are two main configuration files: 
- The first refer to parameters required during the requesting process. See README in the *metab2mesh* sub-directory for option details.
- The second refer to parameters required in the conversion process of association results to RDF triples. See README in the *Analyzes/Enrichment_to_graph* sub-directory for option details.

#### Computation

To compute associations between chemical entities and MeSH descriptors, you can use: w_compound2mesh.sh

*Option details:*
  - v: version of the analysis.
  - m: path to the configuration file of the analysis requesting Virtuoso
  - t: path to the configuration file to convert association to triples
  - u: name of the computed resource
  - d: path to the data directory
  - s: path to the Virtuoso shared directory

For each analysis: all results and intermediary data will be exported in a dedicated sub-directory named as the resource (option u).
In this sub-directory, you can find count data associated with Chemical entities, MeSH descriptors and their co-occurrences (eg. directory MESH_PMID).
In the sub-directory results, you can find the table that resume counts for each association. It is this table that is used later to compute Fisher exact tests on each association. From this table to the final result table containing all statistical values, there are several intermediary files produced.

These intermediary files are:
- r_fisher.csv: correspond to the table containing results after the Fisher exact test computation.
- r_fisher_q.csv: correspond to the results after FDR computation by the Benjamini and Holchberg procedure
- r_fisher_q_w.csv: correspond to the results after computation of the fragility index. This file is the final result table.

At the end of this procedure all significant associations, according to the threshold in the configuration file, are converted in a triple formalism to be instantiated in the knowledge graph. See details of the procedure in the README of Analyzes/Enrichment_to_graph.

Some example of commands that can be used to compute each analysis are shown below:

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

New directory *Analyzes* should have been created at the end of the process in the virtuoso shared directory, instantiating associations between chemical entities and MeSH in a triple formalism, which can be then be load in a Virtuoso triplestore to explore relations.

In the data directory, you can also retrieved all processed results, such as the final results table: *r_fisher_q_w.csv* in each related directory

End !

#### Build a custom triplestore

To build a custom triplestore, you need to start a new virtuoso session. You can use the docker-compose file created in the docker-virtuoso directory by w_buildTripleStore.sh or build your own with different parameters. An example is presented:

For the configuration see details at *https://hub.docker.com/r/tenforce/virtuoso/* and *http://docs.openlinksw.com/virtuoso/*

```yml
version: '3.3'
services:
    virtuoso:
        image: tenforce/virtuoso
        container_name: container_name
        environment:
            VIRT_Parameters_NumberOfBuffers: 2720000   # See http://vos.openlinksw.com/owiki/wiki/VOS/VirtTipsAndTricksGuideRDFPerformanceTuning
            VIRT_Parameters_MaxDirtyBuffers: 2000000    # See http://vos.openlinksw.com/owiki/wiki/VOS/VirtTipsAndTricksGuideRDFPerformanceTuning
            VIRT_Parameters_MaxCheckpointRemap: 680000
            VIRT_Parameters_TN_MAX_memory: 2000000000
            VIRT_SPARQL_ResultSetMaxRows: 10000000000
            VIRT_SPARQL_MaxDataSourceSize: 10000000000
            VIRT_Flags_TN_MAX_memory: 2000000000
            VIRT_Parameters_StopCompilerWhenXOverRunTime: 1
            VIRT_SPARQL_MaxQueryCostEstimationTime: 0       # query time estimation
            VIRT_SPARQL_MaxQueryExecutionTime: 50000          # 5 min
            VIRT_Parameters_MaxMemPoolSize: 200000000
            VIRT_HTTPServer_EnableRequestTrap: 0
            VIRT_Parameters_ThreadCleanupInterval: 1
            VIRT_Parameters_ResourcesCleanupInterval: 1
            VIRT_Parameters_AsyncQueueMaxThreads: 1
            VIRT_Parameters_ThreadsPerQuery: 1
            VIRT_Parameters_AdjustVectorSize: 1
            VIRT_Parameters_MaxQueryMem: 2G
            DBA_PASSWORD: "DB_password"  # The password of the created triplestore
            SPARQL_UPDATE: "false"
            DEFAULT_GRAPH: "http://default#" # The default graph
        volumes:
           - /path/to/virtuoso/share/dir:/usr/local/virtuoso-opensource/var/lib/virtuoso/db/dumps # path to the docker-virtuoso share directory containing all triple files
           - /path/to/docker-virtuoso/data/virtuoso:/data # path to the Virtuoso data directory
        ports:
           - Listen_port:8890 # Set the port to be listen
        networks:
           - network_name # Set the network name

networks:
    network_name: # network name
```
**Warning:** the *data* directory which is bind in the docker-virtuoso is **not** the *data* directory of the results! Inside the directory *docker-virtuoso*, containing the docker-compose file, Virtuoso will create several directories to prepare to session. Among them, it will create a data/virtuoso sub-directory, which need to be mapped to data in the docker container.

Start Virtuoso:

```bash
docker-compose -f path/to/docker-compose.yml up -d 
```

A Virtuoso session should be available at your localhost:Listen_port

To load data in the triplestore, you can use upload files generated by the different previous steps as follows: 

```bash
docker exec -t container_name bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "DB_password" ./dumps/upload.sh'
```
The dumps directory of the Virtuoso container should be mapped on your docker-virtuoso/share.

The created upload files contains different information:
- *upload.sh*: contains ontologies, thesaurus and vocabularies
- *upload_data.sh*: contains triples from PubChem, MeSH and those extracted using Elink
- *pre_upload.sh*: is a light version of *upload_data.sh* using only PubChem Compounds triples indicating compound types and without loading PubChem Descriptor.
- *upload_ClassyFire.sh*: contains triples indicating the chemont classes of PubChem compounds with annotated literature
- *upload_Enrichment_ANALYSIS.sh*: contains triples instanciating relation between chemical entities and MeSh descriptors, there are *upload_Enrichment_CID_MESH.sh*, *upload_Enrichment_CHEBI_MESH.sh*, *upload_Enrichment_CHEMONT_MESH.sh* for the different chemical entities


## Share directory export:

Be sure to remove the *pre_upload.sh* before compressing the share directory