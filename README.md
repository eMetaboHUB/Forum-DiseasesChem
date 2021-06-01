# FORUM Knowledge graph Database

[<img width="200" height="200" src="FORUM_logo2.png">](https://github.com/eMetaboHUB/FORUM-MetDiseaseDatabase) FORUM is an open knowledge network aiming at supporting metabolomics results interpretation in biomedical sciences and automated reasoning.
Containing more than 8 billion statements, it federates data from several life-science resources such as PubMed, ChEBI and PubMed.
Leveraging the bridges in this linked dataset, we automatically extract associations between compound and biomedical concepts, using literature metadata enrichment.
Find more about the method in our preprint here: [BioXiv](https://www.biorxiv.org/content/10.1101/2021.02.12.430944v1)

The FORUM content can be exploited through this portal in two ways:
- The first one, *"Find associations"* allows to search for the relevant association extracted by the system. From a compound name or a chemical family, find related biomedical concepts. Alternatively, you can also, from a biomedical focus, find related compounds. The results provide measures of the association strength and link to the supporting articles in PubMed.
- The second one, *"Ask Anything"*, requires to be familiar with the SPARQL language and allow to directly query the content of the whole knowledge network using our endpoint interface.

The endpoint can also be accessed programmatically and built from source to support further developments. The source code for the Knowledge Network creation and computation of the association can be found on this repo here. Do not hesitate to contact us at [semantics-metabolomics AT inrae DOT fr] for more information.

The FORUM project is supported by **INRAE**, France's National Research Institute for Agriculture, Food and Environment, The H2020 **Goliath** project and the INRAE CATI **EMPREINTE**.

| | | |
|---|---|---|
| [<img style="" markdown="1" width="200" height="200" src="https://www.inrae.fr/themes/custom/inrae_socle/public/images/etat_logo.svg">](https://www.inrae.fr/) | [<img markdown="1" width="200" height="200" src="https://www.inrae.fr/themes/custom/inrae_socle/logo.svg">](https://www.inrae.fr/) | [<img style="" markdown="1" width="200" height="120" src="https://beatinggoliath.eu/wp-content/uploads/sites/343/2019/03/Goliath-logo-with-subtext.png">](https://beatinggoliath.eu/) |
  

## The FORUM team: 

 * **Maxime Delmas**, INRAE Toulouse              - [<img width="16" height="16" src="https://static-exp1.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">](https://www.linkedin.com/in/maxime-delmas-0642071a3/) [<img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png">](http://orcid.org/0000-0002-9352-0624)  [<img src="https://www.twitter.com/favicon.ico">](https://twitter.com/DelmasMaxime1)
 * **Christophe Duperier**, INRAE Clermont Fd    - [<img width="16" height="16" src="https://static-exp1.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">]() [<img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png">]()  [<img src="https://www.twitter.com/favicon.ico">]()  [<img width="16" height="16" src="https://github.com/fluidicon.png">]()
 * **Clément Frainay**, INRAE Toulouse           - [<img width="16" height="16" src="https://static-exp1.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">]() [<img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png">](https://orcid.org/0000-0003-4313-2786)  [<img src="https://www.twitter.com/favicon.ico">](https://twitter.com/clement_frainay?lang=en)  [<img width="16" height="16" src="https://github.com/fluidicon.png">](https://github.com/cfrainay)
 * **Olivier Filangi**, INRAE Rennes             - [<img width="16" height="16" src="https://static-exp1.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">]() [<img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png">]()  [<img src="https://www.twitter.com/favicon.ico">]()  [<img width="16" height="16" src="https://github.com/fluidicon.png">]()
 * **Franck Giacomoni**, INRAE Clermont Fd      - [<img width="16" height="16" src="https://static-exp1.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">](https://www.linkedin.com/in/franck-giacomoni-1979a074/?originalSubdomain=fr) [<img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png">](https://orcid.org/0000-0001-6063-4214) [<img src="https://www.twitter.com/favicon.ico">](https://twitter.com/franckgiacomoni) [<img width="16" height="16" src="https://github.com/fluidicon.png">](https://github.com/fgiacomoni)
 * **Nils Paulhe**, INRAE Clermont Fd           - [<img width="16" height="16" src="https://static-exp1.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">](https://www.linkedin.com/in/nils-paulhe-06713059/) [<img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png">](https://orcid.org/0000-0003-4550-1258)  [<img src="https://www.twitter.com/favicon.ico">](https://twitter.com/nilspaulhe)  [<img width="16" height="16" src="https://github.com/fluidicon.png">](https://github.com/npaulhe)
 * **Florence Vinson**, INRAE Toulouse          - [<img width="16" height="16" src="https://static-exp1.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca">]() [<img src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png">]()  [<img src="https://www.twitter.com/favicon.ico">]()  [<img width="16" height="16" src="https://github.com/fluidicon.png">]()




## About the association results

FORUM provides well grounded associations between MeSH terms and compounds, through their PubChem Compound identifier (CID). FORUM also provide associations with chemical classes using ChEBI and ChemOnt ontologies (note that classes describing a single compound are ignored, as well as the broadest ones). FORUM choose to retain only the strongest associations by applying stringent inclusion criteria, thus, please bear in mind that the absence of an association do not mean a non-association.

The strength of an association is estimated from the frequency of compound mention and biomedical topic co-occurrence in PubMed article. We test for independence using right-tailed Fisher Exact test adjusted for multiple comparisons using the Benjamini-Hochberg procedure, and report the obtained q-value.

We also report the Odds ratio to gauge the relative effect size, as well as the raw number of papers mentioning both the compound and the biomedical topic.

We identify weak associations by computing a confidence interval on the co-occurence proportion. For identified weak associations, you can get more details by hovering the (i) icon to display a measure of their weakness, which represent the minimum number of supporting articles withdraw that would make the association fall below our inclusion criteria. See our preprint for more details.

The results provide associations with most domains of the MeSH thesaurus. The MeSH root allows to easily filter out by top-level categories:

- Anatomy [A]
- Organisms [B]
- Diseases [C]
- Chemicals and Drugs [D]
- Psychiatry and Psychology [F]
- Biological Sciences [G]
- Anthropology, Education, Sociology and Social Phenomena [I]
- Technology and Food and Beverages [J] 

The remaining categories are ignored during computation, but can nonetheless appear in the results for terms belonging to multiple categories that include at least one of the above. More fine-grained filtering can be done from the MeSH tree numbers provided in the export file.

## License

The FORUM association dataset is publically available without license restrictions. Licensing information of external resources used by FORUM can be accessed at the links below:

- [PubChem](https://pubchemdocs.ncbi.nlm.nih.gov/downloads)
- [MeSH](https://www.nlm.nih.gov/databases/download/terms_and_conditions.html) Courtesy of the U.S. National Library of Medicine
- [ChEBI](https://www.ebi.ac.uk/chebi/aboutChebiForward.do)
- [MetaNetX](https://www.metanetx.org/mnxdoc/mnxref.html)
- [CheMont](http://classyfire.wishartlab.com/downloads)

## Acknowledgement

We thank the teams behind [PubChem](https://pubchem.ncbi.nlm.nih.gov/), [PubMed](https://pubmed.ncbi.nlm.nih.gov/), [MeSH](https://meshb.nlm.nih.gov/search), [CheBI](https://www.ebi.ac.uk/chebi/), [MetaNetX](https://www.metanetx.org/) and [ChemOnt](http://classyfire.wishartlab.com) for gratefully providing open data as well as great support for their use, which has made FORUM possible. The FORUM project is not affiliated with any of the cited source. The FORUM project is supported by INRAE, France's National Research Institute for Agriculture, Food and Environment, The H2020 Goliath project and the INRAE CATI EMPREINTE. 

## Technical information 

### 1 - Install environment

#### 1.1 - Install Docker:

Follow instructions at https://docs.docker.com/engine/install/ubuntu/

#### 1.2 - Install Virtuoso Docker container :

- Check that the docker virtuoso image is installed :
If not 
  - Pull tenforce/Virtuoso image: 
```bash
  docker pull tenforce/virtuoso
``` 
Documentation at [tenforce/virtuoso](https://hub.docker.com/r/tenforce/virtuoso)

Before building the triplestore, you need to create 4 directories:
- the **data** directory: it will contain all analysis result files, such as *Compound - MeSH* associations
- the **docker-virtuoso** directory: it will contain the Virtuoso session files and data
- the **docker-virtuoso/share** sub-directory: It will contain all data that need to be loaded in the Virtuoso triplestore. This sub-directory will be bind to the *dump* directory of the Virtuoso docker image.
- the **logs** directory: to store logs.

So, for instance, you can execute:
```
mkdir data
mkdir logs
mkdir -p docker-virtuoso/share
```

Two possibility to build the triplestore:
- You can use the provided docker-image which contains all needed packages and libraries.
- Or, you can execute them on your own environment, but check that all needed packages are installed.

If you want to use the docker image, first build it :

```bash
docker build -t forum/processes \
  --build-arg USER_ID=$(id -u) \
  --build-arg GROUP_ID=$(id -g) .
```
This allow to build an image with correct permissions that correspond to the local host. (https://vsupalov.com/docker-shared-permissions/)

In this container, three directories are intented to be bind with the host:
- out: to export results in data (**data** on host)
- share-virtuoso: to create new RDF files in the Virtuoso shared directory (**docker-virtuoso/share** on host)
- logs-app: to export logs (**logs** on host)

Then, you can launch it using:

```bash
docker run --name forum_scripts --rm -it --network="host" \
-v /path/docker-virtuoso/share:/workdir/share-virtuoso \
-v /path/to/data/dir:/workdir/out \
-v /path/to/log/dir:/workdir/logs-app \
forum/processes bash
```

or in detach mode :

```bash
docker run --detach --name forum_scripts --rm -t --network="host" \
-v /path/docker-virtuoso/share:/workdir/share-virtuoso \
-v /path/to/data/dir:/workdir/out \
-v /path/to/log/dir:/workdir/logs-app \
forum/processes bash
```
When using detach mode, the container is running in the background, which can be really convinient to avoid *Broken pipe*, for instance if your are working on a server.
You can open an interactive bash shell on the container running in the background by using :

```bash
docker exec -it forum_scripts bash
```
You can then navigate in the container (like in a classic docker) to modify configuration files, make tests on scripts, check mount directories, etc ...

Finally, all commands can be launch in a detach mode from the host, like :

```bash
docker exec --detach forum_scripts ./command -param v1 -param2 v2 ...
```
eg.
```bash
docker exec --detach forum_scripts ./workflow/w_computation.sh -v version -m /path/to/config/Compound2MeSH -t path/to/config/triplesConverter/Compound2MeSH -u CID_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```
This command will be execute in the container, running in the background.

Finally, the forum/processes container must not be used to start/stop/clean the Virtuoso triplestore (See 3.1)

**Warnings:** Be sure to map the docker-virtuoso/share and the data directory inside your forum/processes container.
Also, if you use the docker forum/processes, you should use in your commands, directories that bind on the previously created directories: *out* and *share-virtuoso*, instead of using *data* and *docker-virtuoso/share* in the next examples.

**If you want to restart an analysis from scratch, be sure to remove all logs before!**

### 2 - Prepare the triplestore

The building of the KG from scratch can take several days, including the download of the raw data, and the computation of relations between chemical compounds/classes and MeSH descriptors. The building of the KG was achieved on a server using 189GB of memory and 12 cpus.

We deployed the FORUM KG using Virtuoso on a server with 16 cpus and 128 GB of memory. We strongly recommend to deploy it on a SSD-type storage as it can take more than 20 days on a classic storage. 

Also, all metadata related to the FORUM KG are provided in a VoID file accessible at https://forum.semantic-metabolomics.fr/.well-known/void and directly queryable on the SPARQL endpoint.

To build the initial triplestore, you can use the script w_buildTripleStore.sh or directly download RDF files from the FTP server.

#### 2.1 - Build the triplestore

##### 2.1.1 - The core triplestore

There are two configuration files related to this step:
- The first contains parameters about the creation of the triplestore. See README in the *build_RDF_store* sub-directory for option details.
- The second contains parameters to integrate chemont classes in the triplestore. See README in the *Chemont* sub-directory for option details.

Then, from the base directory execute: 

```bash
./workflow/w_buildTripleStore.sh -b path/to/build_RDF_store/config -c path/to/Chemont/config -v version -s path/to/virtuoso/shared/directory -l /path/to/log/dir
```
eg.:

```bash
./workflow/w_buildTripleStore.sh -b app/build_RDF_store/config/config.ini -c app/ChemOnt/config/2020-08-14/config.ini -v test -s ./docker-virtuoso/share -l ./logs-app
```

- *Option details:*
  - b: path to the config file of build_rdf_store (eg. app/build_RDF_store/config/config.ini)
  - c: path to the config file of Chemont processes (eg.  app/ChemOnt/config/version/config.ini)
  - v: The version of the analysis. This is optional, if nothing is set, the date will be used
  - s: path to the Virtuoso shared directory (eg ./docker-virtuoso/share)
  - l: path to log dir (eg ./logs)

This process should have created several sub-directories in the Virtuoso shared directory: ClassyFire, MeSH, MetaNetX, PMID_CID, PMID_CID_endpoints, PubChem_Compound, PubChem_Descriptor, PubChem_InchiKey, PubChem_References, vocabulary

The vocabulary directory contains files associated to the schema of used ontology, they can be download using the docker resource directory or at:

- MeSH: ftp://ftp.nlm.nih.gov/online/mesh/rdf/vocabulary_1.0.0.ttl
- ChEBI: ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.owl
- cito: http://purl.org/spar/cito.ttl
- fabio: http://purl.org/spar/fabio.ttl
- Dublin Core: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.nt
- Cheminf: http://www.ontobee.org/ontology/CHEMINF
- skos: https://www.w3.org/2009/08/skos-reference/skos.rdf
- ChemOnt: http://classyfire.wishartlab.com/downloads

The ChEBI ontology file is often updated and the actual version of the ChEBI ontology used in the triplestore is ChEBI 193 (Release of 01 Nov. 2020), as refer in the URI of the ChEBI Graph in FORUM.

*Warnings:* For ChemOnt, ontology file was downloaded at http://classyfire.wishartlab.com/downloads, but to be loaded in Virtuoso, the file need to be converter in an other format than *.obo*. Using Protege (https://protege.stanford.edu/) ChemOnt_2_1.obo was converted in a turtle format and ChemOnt_2_1.ttl. The ChemOnt ontology seems to be stable.

**Warnings:** This procedure creates two upload files: pre_upload.sh and upload_data.sh.
pre_upload.sh is a light version of upload_data.sh, only loading data needed to compute associations. Thus, it does only load a small part of PubChem Compound graph, setting compound types, and does not load PubChem Descriptor graphs, which are huge graphs. Also, these both upload files contains duplicate information and **must not** be loaded on the same Virtuoso session ! 


##### 2.1.2 - Integration of metabolic networks.

Metabolic networks could also be integrated into the triplestore using the workflow script: w_upload_metabolic_network.
During this process Id-mapping graphs from the metabolic network itself but also from PubChem and MetaNetX are also integrated. See the directory *SBML_upgrade* for more details.

```bash
workflow/w_upload_metabolic_network.sh -a /path/to/metablic/network -b SBLM_version -c path/to/config/file -d MetaNetX_version -e PubChem_version -s /path/to/virtuoso/share/directory -l /path/to/log/dir
```

eg.

```bash
workflow/w_upload_metabolic_network.sh -a out/HumanGEM/rdf/v1.6/HumanGEM.ttl -b Human1/1.6 -c app/SBML_upgrade/config/config_SBML.ini -d 4.1 -e 2020-12-03 -s /workdir/share-virtuoso -l /workdir/logs-app
```

#### 2.2 - Or ... Download RDF files from FTP

- *user:* forum
- *password*: Forum2021Cov!

example :
```bash
sftp forum@ftp.semantic-metabolomics.org:/share.tar.gz
```

All data and results can be downloaded from the sftp server.    

- A copy of the whole KG is store in the share.tar.gz archive.
- Raw results of associations between PubChem, Chemont, ChEBI and MeSH are accessible in directories: CID_MESH, CHEMONT_MESH, CHEBI_MESH, MESH_MESH
- RDF triples associated with significant relations are available in the EnrichmentAnalysis directory (included in share.tar.gz)
- Created triples to instantiate relations between PubChem compounds, PubMed articles or Chemont classes are stored respectively in directories: PMID_CID, PMID_CID_endpoints and ClassyFire (included in share.tar.gz)
- Labels of PubChem compounds, chemical classes, MeSH and their respective tree-Numbers are available in the label directory



### 3 - Compute chemical entities to MeSH associations

Once the initial data of the triplestore have been created, an initial session of the Virtuoso triplestore must be started in order to compute associations between chemical entities and MeSH descriptors.

#### Recommendations:

You may need to disable "Strict checking of void variables" in the SPARQL query editor when you use transitivity in queries.


#### 3.1 - Initialyze the Virtuoso session


**Warning:** The management script of the triplestore Virtuoso, *w_virtuoso.sh*, must be run directly **on the host**, without using the forum docker (forum/processes). Indeed, while starting the forum/processes container, the option *--network="host"* will allows that the container will use the host’s networking.

To start the virtuoso session, use: 
```bash
./workflow/w_virtuoso.sh -d /path/to/virtuoso/dir -s /path/to/share/dir/from/virtuoso/dir start
```

eg.
```bash
workflow/w_virtuoso.sh -d ./docker-virtuoso -s share start
```

The current configuration deploy a Virtuoso triplestore on 64 GB (see *NumberOfBuffers* and *MaxDirtyBuffers*), also dedicating 8 GB per SPARQL query for computation processes (see *MaxQueryMem*). This configuration can be modify in the w_virtuoso.sh script.

*Warnings:* In the provided configuration, the port used by the docker-compose holding the Virtuoso triplestore is 9980. Thus, the url used to request the KG during the computation is http://localhost:9980/sparql/. So if you change the port in the docker-compose.yml, be sure to also changed it in the configuration file for requesting the endpoint.

- *Option details:*
  - d: path to the virtuoso directory. Here, it is advised to set the absolute path.
  - s: path to the shared directory **from** the virtuoso directory (eg. *share* if you use the proposed settings)

Several checks can be used to ensure that the loading was done correctly:

1) At the end of each loading file, Virtuoso execute the command *select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;*. Globally, it asks Virtuoso to return graphs for which there was an error during rdf loading. Check that this request doesn't return any results ([Virtuoso Bulk Loading RDF](http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader#Checking%20bulk%20load%20status))

2) Several requests will be sent against the Virtuoso endpoint during the process, you can check that the central requests are working well. A good start could be to check requests used in the *X_Y* part of the process (Cf. configuration files), such as: *count_distinct_pmids_by_CID_MESH*, *count_distinct_pmids_by_ChEBI_MESH*, *count_distinct_pmids_by_ChemOnt_MESH*. In doing so, be sure to add the content of the prefix variable at the beginning of your request and use only the first 100 elements by setting *limit* and *offset* parameters to 100 and 0 for instance. The first '%s' refers to the graphs that should be used in the request (the *FROM* part of the sparql request) but this can be removed for tests.

3) TODO: Implement tests

#### 3.2 - Set configuration files: 

For each analysis, there are two main configuration files: 
- The first refer to parameters required during the requesting process. See README in the *computation* sub-directory for option details.
- The second refer to parameters required in the conversion process of association results to RDF triples. See README in the *Analyzes/Enrichment_to_graph* sub-directory for option details.

#### 3.3 - Computation

To compute associations between chemical entities and MeSH descriptors, you can use: w_computation.sh

*Option details:*
- **Mandatory options**:
  - m: path to the configuration file of the analysis requesting Virtuoso
  - t: path to the configuration file to convert association to triples
  - u: name of the computed resource
  - d: path to the data directory
  - s: path to the Virtuoso shared directory
  - l: path to log directory
- **Optionals:**
  - v: version of the analysis (optional, date used as default).
  - c: chunksize for parsing files (optional, default 100000). We recommend not to increase this parameter much because it could greatly increase the computation time.
  - p: number of used cores (optional, default 5)
  - o: threshold used in fragility index (optional, default 1e-6)
  - i: alpha of Jeffrey's CI for fragility index computation (optional, default 0.05)
  

For each analysis: all results and intermediary data will be exported in a dedicated sub-directory named as the resource (option u).
In this sub-directory, you can find count data associated with Chemical entities, MeSH descriptors and their co-occurrences (eg. directory MESH_PMID).
In the sub-directory results, you can find the table that resume counts for each association. This table is used later to compute Fisher exact tests on each association. From this table to the final result table containing all statistical values, there are several intermediary files produced.

These intermediary files are:
- r_fisher.csv: correspond to the table containing results after the Fisher exact test computation.
- r_fisher_q.csv: correspond to the results after FDR computation by the Benjamini and Holchberg procedure
- r_fisher_q_w.csv: correspond to the results after computation of the fragility index. This file is the final result table.

At the end of this procedure all significant associations, according to the threshold in the configuration file, are converted in a triple formalism to be instantiated in the knowledge graph. See details of the procedure in the README of Analyzes/Enrichment_to_graph.

**RQ:** To release memory for Virtuoso temp files and others, you can also stop and start again the triplestore using the w_virtuoso.sh script between each computation.

Some example of commands that can be used to compute each analysis are shown below, using default values options c,p,o,i :

##### 3.3.1 - Compute PubChem compounds - MeSH associations

```bash
./workflow/w_computation.sh -v version -m /path/to/config/Compound2MeSH -t path/to/config/triplesConverter/Compound2MeSH -u CID_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```
eg.
```bash
./workflow/w_computation.sh -v 2020 -m app/computation/config/CID_MESH/release-2020/config.ini -t app/Analyzes/Enrichment_to_graph/config/CID_MESH/release-2020/config.ini -u CID_MESH -d ./data -s ./docker-virtuoso/share -l ./logs-app
```


##### 3.3.2 - Compute ChEBI - MeSH associations

```bash
./workflow/w_computation.sh -v version -m /path/to/config/ChEBI2MeSH -t path/to/config/triplesConverter/ChEBI2MeSH -u CHEBI_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```

eg.
```bash
./workflow/w_computation.sh -v 2020 -m app/computation/config/CHEBI_MESH/release-2020/config.ini -t app/Analyzes/Enrichment_to_graph/config/CHEBI_MESH/release-2020/config.ini -u CHEBI_MESH -d ./data -s ./docker-virtuoso/share -l ./logs-app
```

##### 3.3.3 - Compute Chemont - MeSH associations

```bash
./workflow/w_computation.sh -v version -m /path/to/config/Chemont2MeSH -t path/to/config/triplesConverter/Chemont2MeSH -u CHEMONT_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```

eg.
```bash
./workflow/w_computation.sh -v 2020 -m app/computation/config/CHEMONT_MESH/release-2020/config.ini -t app/Analyzes/Enrichment_to_graph/config/CHEMONT_MESH/release-2020/config.ini -u CHEMONT_MESH -d ./data -s ./docker-virtuoso/share -l ./logs-app
```

##### 3.3.4 - Compute MeSH - MeSH associations

```bash
./workflow/w_computation.sh -v version -m /path/to/config/MeSH2MeSH -t path/to/config/triplesConverter/MeSH2MeSH -u MESH_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```

eg.
```bash
./workflow/w_computation.sh -v 2020 -m app/computation/config/MESH_MESH/release-2020/config.ini -t app/Analyzes/Enrichment_to_graph/config/CHEMONT_MESH/release-2020/config.ini -u CHEMONT_MESH -d ./data -s ./docker-virtuoso/share -l ./logs-app
```

Rq: The computation of relations between MeSH descriptors is a particular case, for which the sparql request imposes supplementary filters. Thus, we only compute associations for MeSH descriptors that belong in a sub set of MeSH Trees that do not represent chemicals, as this would be redundant with the CID-MESH analysis, or Organisms, as only few entities are correctly represented in our KG. The list of MeSH tree codes is *C|A|G|F|I|J|D20|D23|D26|D27*. Secondly, we also look for relations that do not involved a parent-child relation (in both ways) between the requested MeSH and the MeSH found.


##### 3.3.5 - Compute SPECIE - MeSH associations

Metabolic networks data (*workflow/w_upload_metabolic_network.sh*)
eg.
```bash
workflow/w_computation.sh -v version -m path/to/Specie2MeSH/config/file -t path/to/config/triplesConverter/Specie2MeSH -u SPECIE_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```
 
eg.
```bash
workflow/w_computation.sh -v 2020 -m app/computation/config/SPECIE_MESH_Thesaurus/release-2020/config.ini -t app/Analyzes/Enrichment_to_graph/config/SPECIE_MESH/release-2020/config.ini -u SPECIE_MESH -d /workdir/out -s /workdir/share-virtuoso -l /workdir/logs-app
```

#### 3.4 - Shutdown Virtoso session

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

**Note**: the Virtuoso session could be stop directly after the counts calculation and is not necessary for the post-processes.

New directory *EnrichmentAnalysis* should have been created at the end of the process in the virtuoso shared directory, instantiating associations between chemical entities and MeSH in a triple formalism, which then can be load in a Virtuoso triplestore to explore relations.

In the data directory, you can also retrieved all processed results, such as the final results table: *r_fisher_q_w.csv* in each related directory

#### 3.5 MeSH, Chemont, ChEBI and CID labels

Identifiers are not always convenient to explore results and therefore, labels of MeSH descriptors, Chemont and ChEBI classes, or PubChem compounds can be more useful.
To retrieve labels of MeSH descriptors, Chemont and ChEBI classes, you can use the SPARQL endpoint by sending requests as indicated in the labels.rq file.
Unfortunately, this can't be done for PubChem compounds as labels are not part of PubChem RDF data, only the IUPAC name being specify, but those can be retrieved using the [pubchem identifier exchange](https://pubchemdocs.ncbi.nlm.nih.gov/identifier-exchange-service). Label files are also provided on the sftp server (See on web-portal).


### 4 - Build a custom triplestore

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
**Warning:** the *data* directory which is bind in the docker-virtuoso is **not** the *data* directory of the results! Inside the directory *docker-virtuoso*, containing the docker-compose file, Virtuoso will create several directories to prepare to session. Among them, it will create a *data/virtuoso* sub-directory, which need to be mapped to data in the docker container.

Start Virtuoso:

```bash
docker-compose -f path/to/docker-compose.yml up -d 
```

A Virtuoso session should be available at your localhost:Listen_port

To load data in the triplestore, you can use upload files generated by the different previous steps as follows: 

```bash
dockvirtuoso=$(docker ps | grep virtuoso | awk '{print $1}')
docker exec $dockvirtuoso isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/*upload_file*.sh
```
The dumps directory of the Virtuoso container should be mapped on your docker-virtuoso/share.

The created upload files contains different information:
- *upload.sh*: contains ontologies, thesaurus and vocabularies
- *upload_data.sh*: contains triples from PubChem, MeSH, MetaNetX and those extracted using Elink
- *pre_upload.sh*: is a light version of *upload_data.sh* using only PubChem Compounds triples indicating compound types and without loading PubChem Descriptor.
- *upload_ClassyFire.sh*: contains triples indicating the chemont classes of PubChem compounds with annotated literature
- *upload_Enrichment_ANALYSIS.sh*: contains triples instanciating relations between chemical entities and MeSH descriptors, there are *upload_Enrichment_CID_MESH.sh*, *upload_Enrichment_CHEBI_MESH.sh*, *upload_Enrichment_CHEMONT_MESH.sh* for the different chemical entities


### 5 - Share directory export:

Be sure to remove the *pre_upload.sh* before compressing the share directory


### 6 - Versioning:

Created graphs are *named graphs* for which the associated uri identify the graph and triples it contains in the triplestore. By this specific uri, each graph represent a version of a specific resource. There are several main resources such as: *MeSH*, *PubChem references*, *PubChem Descriptor*, *PubChem compounds*, *PMID_CID*, etc ... 

When a new graph is created, a new version of the associated resource is created. For example, if a new version of PubChem compounds is build using the *build_RDF_store* script, a new graph with the uri *https://forum.semantic-metabolomics.org/PubChem/compound/version_X* is created as a version of the resource *https://forum.semantic-metabolomics.org/PubChem/compound*.

Several other types of metadata are associated to the created graph. All this metadata information is indicated in a metadata-graph, named *void.ttl*, which is automatically created with the graph in the same directory. An example of a *void.ttl* associated to a PubChem reference resource is described bellow:

```sql
<https://forum.semantic-metabolomics.org/PubChem/reference> dcterms:hasVersion <https://forum.semantic-metabolomics.org/PubChem/reference/2020-11-04> .

<https://forum.semantic-metabolomics.org/PubChem/reference/2020-11-04> a void:Dataset ;
    dcterms:created "2020-12-01"^^xsd:date ;
    dcterms:description "The reference subset contains RDF triples for the type and basic metadata of a given PMID."@en ;
    dcterms:subject <http://dbpedia.org/page/Reference> ;
    dcterms:title "PubChemRDF reference subset"@en ;
    void:dataDump <ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference/pc_reference2chemical_disease_000001.ttl.gz>,
        <ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference/pc_reference2chemical_disease_000002.ttl.gz>,
        <ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference/pc_reference2chemical_disease_000003.ttl.gz>,
        <ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference/pc_reference2chemical_disease_000004.ttl.gz>,
        <ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference/pc_reference2meshheading_000001.ttl.gz>,
        ...
        <ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference/pc_reference_type.ttl.gz> ;
    void:distinctSubjects "13783773"^^xsd:long ;
    void:exampleResource <http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID10395478> ;
    void:triples "313705646"^^xsd:long ;
    void:uriLookupEndpoint <http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> ;
    void:uriSpace "http://rdf.ncbi.nlm.nih.gov/pubchem/reference/"^^xsd:string 
```