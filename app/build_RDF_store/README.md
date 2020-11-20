
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

To faciliate to loading of these data graph in Virtuoso the output directory should be the shared directory of Virtuoso, corresponding to his *dumps* directory.

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
  - timeout: The period (in seconds) after which a request will be canceled if too long. For CID - PMID, 600 is recommended.
  - additional_files_out_path: a path to a directory where the *additional_files* directory will be created.
  - max_triples_by_files: The maximum number of associations exported in a file. For CID - PMID, 5000000 is recommended.
- [FTP]
  - ftp: The ftp server address on which created data will be stored. A valid adress is not mandatory as data will not be automatically upload to the ftp server, but this will be used to provide metadata (*void:dataDump* triples) in corresponding void.ttl files.

run from workdir:
```python
python3 app/build_RDF_store/build_RDF_store.py --config="/path/to/config_file.ini" --out="path/to/out/dir" --log="path/to/log/dir" --version="version"
```

- config: path to the configuration file
- out: path to output directory, should be the docker-virtuoso shared directory
- log: path to the log directory
- version: The version of the builded ressource. If nothing is indicated, date will be used