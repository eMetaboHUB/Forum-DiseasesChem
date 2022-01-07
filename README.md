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

We identify weak associations by computing a confidence interval on the co-occurrence proportion. For identified weak associations, you can get more details by hovering the (i) icon to display a measure of their weakness, which represent the minimum number of supporting articles withdraw that would make the association fall below our inclusion criteria. See our preprint for more details.

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

Before building the triplestore, you should create 5 directories:
- the **data** directory: it will contain all analysis result files, such as *Compound - MeSH* associations
- the **docker-virtuoso** directory: it will contain the Virtuoso session files and data
- the **docker-virtuoso/share** sub-directory: **The most important directory**. It will contain all the data that need to be loaded in the Virtuoso triplestore. This sub-directory will be bind to the *dumps* directory in the Virtuoso docker image.
- the **logs** directory: to store log files
- the **config** directory: to store config files

So, for instance, you can execute:
```
mkdir data
mkdir -p docker-virtuoso/share
mkdir logs
mkdir config
```

Two possibility to build the triplestore:
- You can use the provided docker-image which contains all needed packages and libraries.
- Or, you can execute them on your own environment, but check that all needed packages are installed (See Dockerfile).

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
- config: for custom config files

Then, you can launch it using:

```bash
docker run --name forum_scripts --rm -it --network="host" \
-v /path/docker-virtuoso/share:/workdir/share-virtuoso \
-v /path/to/data/dir:/workdir/out \
-v /path/to/log/dir:/workdir/logs-app \
-v /path/to/config/dir:/workdir/config \
forum/processes bash
```

or in detach mode :

```bash
docker run --detach --name forum_scripts --rm -t --network="host" \
-v /path/docker-virtuoso/share:/workdir/share-virtuoso \
-v /path/to/data/dir:/workdir/out \
-v /path/to/log/dir:/workdir/logs-app \
-v /path/to/config/dir:/workdir/config \
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

We deployed the FORUM KG using Virtuoso on a server with 16 cpus and 128 GB of memory. We strongly recommend to deploy it on a SSD-type storage as it can take more than 20 days on a classic storage (that's not a joke). 

Also, all metadata related to the FORUM KG are provided in a VoID file accessible at https://forum.semantic-metabolomics.fr/.well-known/void and directly queryable on the SPARQL endpoint.

To build the initial triplestore, you can use the scripts provided in the build directory or directly download the compressed *share* directory of the current release on the ftp server

#### 2.1 - Build the triplestore

##### 2.1.1 - The core triplestore

To build the triplestore, several scripts are available, each dedicated to a specific FORUM resource. Workflow scripts describing all steps of the current release construction are also availables in the *workflow directory*.

All the scripts use to create/import resources create at least:

- one or more data graphs containing triples in a format accepted by the Virtuoso's loading functions (see http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader). This data **must** be written to the *share* directory (*/workdir/share-virtuoso* in the docker)

- a void.ttl file, written in the same directory as the data graphs, describing the metadata.

- an upload file containing all the iSQL commands to load the graph in Virtuoso (See http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader). The upload files are **always** written at the root of the *share* directory.

In the following sections, all example commands are provided as like they are use in the *forum_scripts* Docker.

Configuration files for all scripts used in the current release are provided in the *config* directory.

##### The vocabularies:

The vocabulary directory contains files associated to the schema of used ontology, they can be download using the docker resource directory or at:

- MeSH: https://nlmpubs.nlm.nih.gov/projects/mesh/rdf/2021/vocabulary_1.0.0.ttl
- ChEBI: https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.owl.gz
- cito: http://purl.org/spar/cito.ttl
- fabio: http://purl.org/spar/fabio.ttl
- Dublin Core: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.nt
- Cheminf: http://www.ontobee.org/ontology/CHEMINF
- skos: https://www.w3.org/2009/08/skos-reference/skos.rdf
- ChemOnt: http://classyfire.wishartlab.com/downloads

The MeSH vocabulary file has been downloaded from the 2021 release of MeSH.

The ChEBI ontology file is often updated and the actual version of the ChEBI ontology used in the triplestore is: ChEBI Release version 205 (Release of 03 Nov. 2021), as refer in the URI of the ChEBI Graph in FORUM.

*Warnings:* For ChemOnt, ontology file was downloaded at http://classyfire.wishartlab.com/downloads, but to be loaded in Virtuoso, the file need to be converter in an other format than *.obo*. Using Protege (https://protege.stanford.edu/) ChemOnt_2_1.obo was converted in a turtle format and ChemOnt_2_1.ttl. The ChemOnt ontology seems to be stable.

To download the vocabulary files along with their upload file, use import_vocabulary.sh

The upload file also loads the namespaces in Virtuoso.

```bash
bash app/build/import_vocabulary.sh -s /workdir/share-virtuoso -f ftp.semantic-metabolomics.org:upload_2021.tar.gz -u forum -p Forum2021Cov!
```

##### MetaNetX

To import the MetaNetX resource in FORUM, use: import_MetaNetX.py

```bash
python3 -u app/build/import_MetaNetX.py --config="/workdir/config/release-2021/import_MetaNetX.ini" --out="/workdir/share-virtuoso" --log="/workdir/logs-app"
```
###### Config

- [DEFAULT]
  - upload_file = the name of the upload file
  - log_file = the name of the log file
- [METANETX]
  - version = The MetaNetX version (See https://www.metanetx.org/ftp/)
  - url = The download url. The version attribute complete the url (eg. https://www.metanetx.org/ftp/{version}/metanetx.ttl.gz)


##### MeSH

To import the MeSH resource in FORUM, use: import_MeSH.py

```bash
python3 -u app/build/import_MeSH.py --config="/workdir/config/release-2021/import_MeSH.ini" --out="/workdir/share-virtuoso" --log="/workdir/logs-app"
```

###### Config

- [DEFAULT]
  - upload_file = the name of the upload file
  - log_file = the name of the log file
- [MESH]
  - version = the version that should be loaded in Virtuoso. Indicate "latest", to download and load the latest available version of MeSH, or, provide an MeSH version already available in the share directory.
  - ftp = the ftp adress of MeSH
  - ftp_path_void = path to the void file from the ftp
  - ftp_path_mesh = path to the mesh data file from the ftp

##### PubChem

See https://pubchemdocs.ncbi.nlm.nih.gov/rdf

PubChem data are divided into subsets: compounds, descriptors, reference ...

Each subset is relevant but, depending on the requests, not all subsets (and all data files in a subset) need to be loaded at the same time. The script import_PubChem.py allow to download several PubChem subsets, but only load some of them, by specifying the file mask.

This script is therefore use two times:
- A first time to download all the PubChem subsets and create an uplod file containing only PubChem Compounds types and reference data (import_PubChem_min.ini)
- A Second time to create a new upload file to load all the PubChem data in Virtuoso (import_PubChem_full.ini).

```bash
python3 -u app/build/import_PubChem.py --config="/workdir/config/release-2021/import_PubChem_min.ini" --out="/workdir/share-virtuoso" --log="/workdir/logs-app"
```
###### Config

- [DEFAULT]
  - upload_file = the name of the upload file
  - log_file = the name of the log file
- [PUBCHEM]
  - dir_ftp = a list of the PubChem's subdomain directories to download from the ftp (eg. compound/general)
  - name = a list of the PubChem's subdomain name
  - out_dir = a list of the PubChem's subdomain directories to write data in the *share* dir
  - mask = a list of the masks of the files to be loaded. If false, the associated subdomain will not be loaded
  - version = a list of the version of the PubChem's subdomain. Indicate "latest", to download the latest available version, or, provide a version already available in the share directory.
  - ftp = path to the void file from the ftp
  - ftp_path_void = path to the void file from the ftp


##### PMID-CID

To integrate the linkSet PMID-CID providing triples that an article (pmid) *discusses* a PubChem Compound (CID), use: import_PMID_CID.py

Being a LinkSet, a valid path to the directories of the targeted PubChem compound and reference graph must also be provided.

This script produced two subset:

- PMID_CID: contains triples:
> PMIDX cito:discusses CIDY

- PMID_CID_endpoint contains information about the providers of these relations: 
> endpoint:PMIDX_CIDY obo:IAO_0000136 PMIDX ;
> dcterms:contributor C ;
> cito:isCitedAsDataSourceBy CIDY .

There are 3 types of contributors (source https://doi.org/10.1186/s13321-016-0142-6): 
- pccompound_pubmed_publisher: Links are provided to PubMed by publishers.
- pccompound_pubmed_mesh: Computationally generated links to PubMed articles that have a common MeSH annotation.
- pccompound_pubmed: Links generated from cross-references provided to PubChem by data contributors (eg. IBM Almaden Research Center).

```bash
python3 -u app/build/import_PMID_CID.py --config="/workdir/config/release-2021/import_PMID_CID.ini" --out="/workdir/share-virtuoso" --log="/workdir/logs-app"
```

As it is a long provess, you can use the following commands inside the detached container (forum_script) to output STDOUT in a log file.
```bash
echo "" > logs-app/global_log_PMID_CID.log
python3 -u app/build/import_PMID_CID.py --config="/workdir/config/release-2021/import_PMID_CID.ini" --out="/workdir/share-virtuoso" --log="/workdir/logs-app" 2>&1 | tee -a logs-app/global_log_PMID_CID.log &
```


###### Config

- [DEFAULT]
  - upload_file = the name of the upload file
  - log_file = the name of the log file
[ELINK]
  - version = the version. If this version already exists (a valid void.ttl file found at *share/PMID_CID/{version}/void.ttl), the computation will be skiped and only the upload file will be produced.
  - run_as_test = (True/False) indicating if the Elink processes have to be run as test (only the first 5000 pmids) or full
  - pack_size = the number of identifiers that will be send in the Elink request. For CID - PMID, 5000 is recommended. (please refer to https://eutils.ncbi.nlm.nih.gov/entrez/query/static/entrezlinks.html)
  - api_key = an apiKey provided by a NCBI account
  - timeout =  the period (in seconds) after which a request will be canceled if too long. For CID - PMID, 600 is recommended.
  - max_triples_by_files = the maximum number of associations exported in a file. For CID - PMID, 5000000 is recommended.
  - reference_uri_prefix = the prefix of the reference subdomain URIs for PMIDs
  - compound_path = path in the *share* directory to the targeted compound graph directory. This path will be used to access the void.ttl file containing information about the version of this PubChem compound graph.
  - reference_path = path in the *share* directory to the targeted reference graph directory. This path will also be used to search for "*_type*.ttl.gz" reference files. 


##### Chemont

In order to provide a MeSH enrichment from ChemOnt classes, the goal of this procedure is to retrieve ChemOnt classes associated to PubChem compounds, using only those for which a literature is available. The literature information is extracted from PMID - CID graphs, while the InchiKey annotation from PubChem InchiKey graphs.

A valid path to the directories of the targeted PubChem compound and PubChem InchiKey for annotations must be provided.

ChemOnt classes associated to a PubChem compound are accessible through their InchiKey at the URL http://classyfire.wishartlab.com/entities/INCHIKEY.json

For a molecule, ChemOnt classes are organised in 2 main categories: 
- A *Direct-parent* class: representing the most dominant structural feature of the chemical compounds

- Some *Alternative parents* classes: Chemical features that also describe the molecule but do not have an ancestor–descendant relationship with each other or with the *Direct Parent* class. 

These both types of classes are stored separately in two different graphs.


*Djoumbou Feunang, Y., Eisner, Wishart, D.S., 2016. ClassyFire: automated chemical classification with a comprehensive, computable taxonomy. J Cheminform 8, 61. https://doi.org/10.1186/s13321-016-0174-y*

How to run:
```python
python3 -u app/build/import_Chemont.py --config="config/release-2021/import_Chemont.ini" --out="/workdir/share-virtuoso" --log="/workdir/logs-app"
```

### Config file

- [DEFAULT]
  - upload_file = the name of the upload file
  - log_dir = the name of the log file
-[CHEMONT]
  - version = the version. If this version already exists (a valid void.ttl file found at *share/PMID_CID/{version}/void.ttl), the computation will be skiped and only the upload file will be produced.
  - n_processes = number of simultaneoulsly sent requests to ClassyFire
- [PMID_CID]
  - mask = the mask of the PMID_CID files to extract
  - path = path to the PMID_CID directory to extract the list of CID with available literature
- [INCHIKEY]
  - mask = the mask of the inchikey files to extract
  - path = path to the inchikey directory to extract the inchikey annotation of PubChem compounds




##### 2.1.2 - Integration of metabolic networks.

**See docs/sbml.md**

An workflow example file from the current release to import a SBML file with all the needed annotation graphs in Virtuoso is provided in the *workflow directory*


#### 2.2 - Or ... Download RDF files from FTP

- *user:* forum
- *password*: Forum2021Cov!



example :
```bash
sftp forum@ftp.semantic-metabolomics.org:/dumps/2021/share.tar.gz
```

All data and results can be downloaded from the sftp server.    

- A copy of the whole KG is store in the share.tar.gz archive.
- Raw results of associations between PubChem, Chemont, ChEBI and MeSH are accessible in directories: CID_MESH, CHEMONT_MESH, CHEBI_MESH, MESH_MESH
- Labels of PubChem compounds, chemical classes, MeSH and their respective tree-Numbers are available in the label directory

**We plan to update the FORUM Knowledge graph every year.**

### 3 - Compute chemical entities to MeSH associations

Once the initial data of the triplestore have been created, an initial session of the Virtuoso triplestore must be started in order to compute associations between chemical entities and MeSH descriptors.

#### Recommendations:

You may need to disable "Strict checking of void variables" in the SPARQL query editor when you use transitivity in queries.

#### 3.1 Virtuoso Triple store

##### 3.1.1 - Initialyze the Virtuoso session


**Warning:** The management script of the triplestore Virtuoso, *w_virtuoso.sh*, must be run directly **on the host**, without using the forum docker (forum/processes). Indeed, while starting the forum/processes container, the option *--network="host"* will allows that the container will use the host’s networking.

To start the virtuoso session, use: 

```bash
bash workflow/w_virtuoso.sh -d /path/to/virtuoso/dir -s share -c start upload1.sh upload2.sh ...
```
e.g

The current configuration deploy a Virtuoso triplestore on 64 GB (see *NumberOfBuffers* and *MaxDirtyBuffers*), also dedicating 8 GB per SPARQL query for computation processes (see *MaxQueryMem*). This configuration can be modify in the w_virtuoso.sh script.

*Warnings:* In the provided configuration, the port used by the docker-compose holding the Virtuoso triplestore is 9980. Thus, the url used to request the KG during the computation is http://localhost:9980/sparql/. So if you change the port in the docker-compose.yml, be sure to also changed it in the configuration file for requesting the endpoint.


- *Option details:*
  - d: path to the virtuoso directory. Here, it is advised to set the absolute path.
  - s: path to the shared directory **from** the virtuoso directory (usually *share* if you use the proposed settings)
  - c: the command *start* create a Virtuoso rdf store; *stop* end the virtuoso session; *clean* delete the Virtuoso session, to clean up before building a new one
  
When use *start* to create a new triplestore, pass to the command the list of the upload files for the data you want to load.

For instance, to load the vocabulary, MeSH, PubChem and PMID_CID, from the current release configuration files and compute associations, use: 

```bash
bash workflow/w_virtuoso.sh -d /path/to/virtuoso/dir -s share -c start upload.sh upload_PMID_CID.sh upload_MeSH.sh upload_PubChem_minimal.sh
```


Several checks can be used to ensure that the loading was done correctly:

1) At the end of each loading file, Virtuoso execute the command *select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;*. Globally, it asks Virtuoso to return graphs for which there was an error during rdf loading. Check that this request doesn't return any results ([Virtuoso Bulk Loading RDF](http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader#Checking%20bulk%20load%20status))

Several requests will be sent against the Virtuoso endpoint during the process, you can check that the central requests are working well. In the *test* directory, we prepare a list of SPARQL queries that test the main properties and paths use during the process. Be sure that each of these queries return results. A good start could also be to check requests used in the *X_Y* part of the process (Cf. configuration files), such as: *count_distinct_pmids_by_CID_MESH*, *count_distinct_pmids_by_ChEBI_MESH*, *count_distinct_pmids_by_ChemOnt_MESH*. In doing so, use only the first 100 elements by setting *limit* and *offset* parameters to 100 and 0 for instance. The first '%s' refers to the graphs that should be used in the request (the *FROM* part of the sparql request) but this can be removed for the tests.


##### 3.1.2 Monitoring

The FORUM triplestore is built from both triples created and collected from web services (eg. PMID_CID, CHEMONT) and aggregated from different external resources (eg. PubChem). In this way, inconsistency is the data can comes from different issues. Some advices are provided to detect and quantity potential errors or lack in the data: 

- **Check the void (and mainly the master void)**: The void files summarize useful metadata about the created graphs. A comparison of the main properties *void:distinctSubjects* and  *void:triples* of the graph between the old and the new release can provide a rough estimator of the changes. Basically, we expect that each year the total number of subjects and triples should increase. If it's not the case, corrections may have been brought by the providers but when a large amount of subjects/triples are drop, it is often the sign of an issue in the data recuperation process or from the providers themselves.

- **Check the properties**: To check that the schema of the data doesn't have change between two versions, you should check that all the used properties for SPARQL requests (eg. fabio:hasSubjectTerm) are still instantiated to the individuals. A comparison of the total number of subjects associated to each property can also allow to detection potential errors or missing properties in the data.

- **Manual check of a sample of associations:** Sometimes, a loss of data can be compensated by a greater gain and therefore this loss cannot be detected by comparing the void files. It is so advised to compare the results obtained between the both version for a sample of Chemical - MeSH pairs, by checking the amount of literature available for each, and their co-occurrences. For instance between PFOA (CID 9554) et Fetal development (MeSH D047109).





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

For more details on the computation processes see *computation.md* in docs.

The checkpointing of Virtuoso can disturb the requesting processes, because during the checkpoint the database will be inaccessible.

To avoid checkpointing when computing associations, you should disable the checkpointing.

A recommended plan is to :

- 1) Run the triples insertion with w_virtuoso.sh (see **3.1**). A checkpoint will be made after the insertion of each datasets.

- 2) Before sending queries and compute associations, **disable checkpointing** with

```bash
docker exec -it $CONTAINER_NAME bash
isql-v -U dba -P FORUM
checkpoint_interval(-1);
exit;
```

- 3) After the execution of the computation script, make a last checkpoint to avoid a long roll forward when restarting the triplestore.

```bash
docker exec -it $CONTAINER_NAME bash
isql-v -U dba -P FORUM
checkpoint;
exit;
```

- 4) You can now shutdown the triplestore with `workflow/w_virtuoso.sh -d /path/to/virtuoso/dir -s share -c stop`

When the triplestore is restarted to compute other associations, there should be no roll forward.


##### 3.3.1 - Compute PubChem compounds - MeSH associations

```bash
./workflow/w_computation.sh -v version -m /path/to/config/Compound2MeSH -t path/to/config/triplesConverter/Compound2MeSH -u CID_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```

eg.
```bash
./workflow/w_computation.sh -v 2021 -m config/release-2021/computation/CID_MESH/config.ini -t config/release-2021/enrichment_analysis/config_CID_MESH.ini -u CID_MESH -d /workdir/out -s /workdir/share-virtuoso -l /workdir/logs-app
```


##### 3.3.2 - Compute ChEBI - MeSH associations

```bash
./workflow/w_computation.sh -v version -m /path/to/config/ChEBI2MeSH -t path/to/config/triplesConverter/ChEBI2MeSH -u CHEBI_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```

eg.
```bash
./workflow/w_computation.sh -v 2021 -m config/release-2021/computation/CHEBI_MESH/config.ini -t config/release-2021/enrichment_analysis/config_CHEBI_MESH.ini -u CHEBI_MESH -d /workdir/out -s /workdir/share-virtuoso -l /workdir/logs-app
```

##### 3.3.3 - Compute Chemont - MeSH associations

```bash
./workflow/w_computation.sh -v version -m /path/to/config/Chemont2MeSH -t path/to/config/triplesConverter/Chemont2MeSH -u CHEMONT_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```

eg.
```bash
./workflow/w_computation.sh -v 2021 -m config/release-2021/computation/CHEMONT_MESH/config.ini -t config/release-2021/enrichment_analysis/config_CHEMONT_MESH.ini -u CHEMONT_MESH -d /workdir/out -s /workdir/share-virtuoso -l /workdir/logs-app
```

##### 3.3.4 - Compute MeSH - MeSH associations

```bash
./workflow/w_computation.sh -v version -m /path/to/config/MeSH2MeSH -t path/to/config/triplesConverter/MeSH2MeSH -u MESH_MESH -d /path/to/data/dir -s /path/to/virtuoso/share/dir -l /path/to/log/dir
```

eg.
```bash
./workflow/w_computation.sh -v 2021 -m config/release-2021/computation/MESH_MESH/config.ini -t config/release-2021/enrichment_analysis/config_MESH_MESH.ini -u MESH_MESH -d /workdir/out -s /workdir/share-virtuoso -l /workdir/logs-app
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
workflow/w_computation.sh -v 2021 -m config/release-2021/computation/SPECIE_MESH_Thesaurus/config.ini -t config/release-2021/enrichment_analysis/config_SPECIE_MESH.ini -u SPECIE_MESH -d /workdir/out -s /workdir/share-virtuoso -l /workdir/logs-app
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