
## Build RDF Store:
Use build_RDF_store.py
This process is used to build a complete RDF Store containing data graphs from PubChem Compounds, PubChem References, PubChem Descriptors, PubChem InchiKey, MeSH, MetaNetX and to identify links between PubChem compounds (CID) and PubMed publications (PMIDS). If needed, only some data graphs can be selected and dowloaded.

For PubChem and MeSH resources, this version is determined from the modification date of associated files on the ftp server. If the last version of the resource has already been downloaded, the program will skip this step. Log files are also produced for each downloaded resource.

For the resource describing links between PubChem Compounds and PubMed publications, the version can be defined by the user. If nothing is set, the date will be used by default. Like previous resources, if the version have already been created, the program will skip the step. To allow overwriting, be sure to delete the associated directory in the *additional_files*.

The *additional_files* directory contains lists of identifiers treated by the program and caches metadata files, which can be used as back-up by the program.

This directory contains :
  - all_linked_ids: a list of all the linked identifiers found by the Elink process (ex: PubChem Compounds identifiers)
  - all_linking_ids.txt: a list of all input identifiers used in the Elink process for which available links to *linked_ids* will be researched
  - linking_ids_request_failed.txt: a list of all linking ids for which the request failed (Timeout, Server Errors, etc ...). At the end of the process this list must be empty.
  - linking_ids_without_linked_ids.txt: a list of all the linking identifiers for which no link to a linked identifier was found
  - successful_linking_ids.txt: a list of all the linking identifiers for which at least one link to a *linked_ids* was found.
  - s_metdata.txt: a cache metadata file which may also be used for back-up.

To facilitate the loading of these data graph in Virtuoso the output directory should be the shared directory of Virtuoso, corresponding to the *dumps* directory.

At the end of the process, two files are created: pre_upload.sh and upload_data.sh. These files contain all the *ISQL* commands that should be executed by Virtuoso to properly load graphs and metadata. pre_upload.sh is a light version of upload_data.sh which is loading only data needed to compute associations. Thus, it does only load a small part of PubChem Compound graph, setting compound types, and does not load PubChem Descriptor graphs, which are huge graphs. This light upload version can be used to have a light version of the RDF triplestore, without all information about compounds. Also, these both upload files contains duplicate information and **must not** be loaded on the same Virtuoso session ! 

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/upload.sh'
```

#### Config file:

In the configuration file, precise the section title to create the associate resource.

Each section has its own properties detailed below. For instance, to download the MetaNetX resource, you must provide this section in the configuration file with its required attribute: *version*. The MeSH section does not required any attribute.

For PubChem subsets, attributes are ordered lists of properties dedicated to each resource to be included. The order of element is key as the i*th* entry in all the list attribute must correspond to the same resource. As all the PubChem resources are not required to compute the FORUM associations, thoses subset resources are organised into two sets: 

  -- the minimal core (*MINCORE*) loading only the PubChem subset resources that are required to compute the associations, such as: *References*, *PMID_CID*, etc ...

  -- the maximal (or full) core (*MAXCORE*) which load all the PubChem subsets to mount the global endpoint.

The *mincore* and *maxcore* attributes of the PubChem section are used to specified which content of each resource needs to be loaded for the *MINCORE* and/or *MAXCORE*. For instance, in the PubChem compound graph, only the triples setting the ChEBI classes of the compounds are required to compute the FORUM associations. Therefore in the *mincore* attribute, the mask provided for the PubChem compound resource is "*_type*.ttl.gz", whereas it is "*.ttl.gz" in the *MAXCORE* when we load all the data. 

#### Configuration file in detail:

- [METANETX]:
  - version: the version of MetaNetX (See [MetaNetX ftp](ftp://ftp.vital-it.ch/databases/metanetx/MNXref/))
- [MESH]: set this section to download MeSH
- [PUBCHEM]
  - dir_ftp: a list of paths to the directory associated with the PubChem subset resources from *ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/* to be included. Eg. ["compound/general", "descriptor/compound", "reference", "inchikey", "synonym", "source", "concept"]
  - name: a list of the names of the PubChem subset resources. Eg. ["compound", "descriptor", "reference", "inchikey", "synonym", "source", "concept"]
  - out_dir: a list of output directories to store resources in the Virtuoso shared directory. Eg. ["PubChem_Compound", "PubChem_Descriptor", "PubChem_Reference", "PubChem_InchiKey", "PubChem_Synonym", "PubChem_Source", "PubChem_Concept"]
  - mincore: a list of mask patterns to match against the files in the resource directory (See http://docs.openlinksw.com/virtuoso/fn_ld_dir_all/). If a mask is provided, the corresponding files will be integrated for the minimal dataset of FORUM (the *MINCORE* set) and therefore in the *pre_upload.sh* file. If 'false' is indicated, it will not be included. Eg. ["*_type*.ttl.gz", false, "*.ttl.gz", false, false, false, false]
  - maxcore: a list of mask patterns to match against the files in the resource directory (See http://docs.openlinksw.com/virtuoso/fn_ld_dir_all/). If a mask is provided, the corresponding files will be integrated for the full dataset of FORUM (the *MAXCORE* set) and therefore in the *upload_data.sh* file. If 'false' is indicated, it will not be included. Eg. ["*.ttl.gz", "*.ttl.gz", "*.ttl.gz", "*.ttl.gz", "*.ttl.gz", "*.ttl.gz", "*.ttl.gz"]
  - version: a list of the required version for each PubChem subset. If nothing is provided (""), the latest version available online will be downloaded. If one is provided and is available in the share directory, it will be integrated in the upload files.
- [ELINK]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - run_as_test: a boolean (True/False) indicating if the Elink processes have to be run as test (only the first 30000 pmids) or full
  - pack_size: the number of identifiers that will be send in the Elink request. For CID - PMID, 5000 is recommended. (please refer to https://eutils.ncbi.nlm.nih.gov/entrez/query/static/entrezlinks.html)
  - api_key: an apiKey provided by a NCBI account 
  - timeout: The period (in seconds) after which a request will be canceled if too long. For CID - PMID, 600 is recommended.
  - additional_files_out_path: a path to a directory where the *additional_files* directory will be created.
  - max_triples_by_files: The maximum number of associations exported in a file. For CID - PMID, 5000000 is recommended.
- [FTP]
  - ftp: The ftp server address on which created data will be stored. A valid adress is not mandatory as data will not be automatically upload to the ftp server, but this will be used to provide metadata (*void:dataDump* triples) in corresponding void.ttl files.

To get an API Key, you can need a [NCBI account](https://www.ncbi.nlm.nih.gov/account/register/).

run from workdir:
```python
python3 app/build_RDF_store/build_RDF_store.py --config="/path/to/config_file.ini" --out="path/to/out/dir" --log="path/to/log/dir" --version="version"
```

- config: path to the configuration file
- out: path to output directory, should be the docker-virtuoso shared directory
- log: path to the log directory
- version: The version of the builded resource. If nothing is indicated, date will be used

pre_upload.sh or upload_data.sh, can then be loaded in the Virtuoso triplestore using :

```bash
dockvirtuoso=$(docker ps | grep virtuoso | awk '{print $1}')
docker exec $dockvirtuoso isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/*upload_file*.sh
```