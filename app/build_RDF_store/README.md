
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

- [METANETX]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - version: the version of MetaNetX (See [MetaNetX ftp](ftp://ftp.vital-it.ch/databases/metanetx/MNXref/))
- [MESH]
  - todo: a boolean (True/False) telling if the data need to be downloaded
- [COMPOUND]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - dir_on_ftp: path to associated directory from *ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/* at PubChem ftp server (ex: compound/general)
- [DESCRIPTOR]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - dir_on_ftp: path to associated directory from *ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/* at PubChem ftp server (ex: descriptor/compound)
- [REFERENCE]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - dir_on_ftp: path to associated directory from *ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/* at PubChem ftp server (ex: reference)
- [INCHIKEY]
  - todo: a boolean (True/False) telling if the data need to be downloaded
  - dir_on_ftp: path to associated directory from *ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/* at PubChem ftp server (ex: inchikey)
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