## Metabolite - Diseases Graph Database

This repository contains some usefull methods to provides links between PubChem compound identifiers, litteratures (PMIDs) and MeSH

## Install
### Install Docker Virtuoso :

- Pull tenforce/Virtuoso image: 
```bash
docker pull tenforce/virtuoso
```
Documentation at https://hub.docker.com/r/tenforce/virtuoso

### Build metdisease Docker :

```bash
docker build -t forum/metdisease .
```

### Run
```bash
docker run --rm -it --network="host" \
-v path/to/docker-ressource:/workdir/data \
-v path/to/config/dir:/workdir/config \
-v /path/to/virtuoso-share/dir:/workdir/share-virtuoso \
-v /path/to/out/dir:/workdir/out/ \
forum/metdisease bash
```

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
  - version: The version of the builded ressource. If nothing is indicated, date will be used
  - timeout: The period (in seconds) after which a request will be canceled if too long. For CID - PMID, 600 is recommended.
  - additional_files_out_path: a path to a directory where the *additional_files* directory will be created.
  - max_triples_by_files: The maximum number of associations exported in a file. For CID - PMID, 5000000 is recommended.

run from workdir:
```python
python3 app/build_RDF_store/build_RDF_store.py --config="/path/to/config_file.ini"
```

## metab2mesh :
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
*modalility_x, modalility_y, total_counts_for_modality_x, total_counts_for_modality_y, total_counts_for_coocurences_between_x_and_y, total_number_of_individuals*. As this data.frame can be really huge and to facilitate post-processes parallelization it can be divided in smaller data.frame according to the *file_size* parameters

The data.frame is printed in *df_out_dir* at *out_path*

#### config file :

- [DEFAULT]
  - out_path: /path/to/output/directory/
  - df_out_dir: name of metab2mesh data.frame output directory
  - file_size: number of lines per outputed data.frames
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
python3 app/metab2mesh/metab2mesh_requesting_virtuoso.py --config="/path/to/config.ini"
```

Using the same workflow to parallelize queries, additional queries (Get MESH Names, etc ...) are provided in the additional_request.py and config parameters are the same.

## SBML Import & SBML annotation :

Methods describe below provide a way to import and annotate SBML file in the RDF store. 

There are two types of provided annotation for SBML graphs: Id mapping and Inchi/SMILES annotations.
### Id mapping: 

In the SBML graph, metabolite are represented as *SBMLrdf:Species* and links to external references (such as ChEBI, BiGG, KEGG, etc ...) are described using the *bqbiol:is* predicate, associated to an uri representing an external ressource identifier, ex :

*M_m02885c a  SBMLrdf:Species ;*
          *bqbiol:is chebi:18170 .*

From intial external references present in the SBML graph, the program will try to extend this annotation using Id-mapping graphs. The extend of external uris identifiers in the SBML can be done when the SBML and some Id-mapping graphs are imported in the Virtuoso RDF Store.

Id-mapping graphs are RDF graphs providing uris equivalences. There are two type of uris equivalences:

* Inter-uris equivalences:
  It defines equivalences between uris from different external ressources, where identifiers correspond to the same molecule. For example, the ChEBI id 37327 is equivalent to Pubchem CID 5372720, in the Id-mapping graph, this equivalence will be represented as : *http://identifiers.org/chebi/CHEBI:37327* *skos:closeMatch* *http://identifiers.org/pubchem.compound/5372720*. *skos:closeMatch* indicates that two concepts are sufficiently similar and that the two can be used interchangeably, nevertheless, this  is not transitive, to avoid spreading  equivalence errors.

* Intra-uris equivalences:
  For each identifires of an external ressource, it defines equivalences between uris pattern associated to this same external ressource. For exemple, for one ChEBI id 18170, 3 different uris are availables: *http://purl.obolibrary.org/obo/CHEBI_18170*, *https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:18170*, *http://identifiers.org/chebi/CHEBI:18170*. In this case *http://identifiers.org/chebi/CHEBI:18170* is used by default in the SBML graph, but *http://purl.obolibrary.org/obo/CHEBI_18170* is the uri which is used in the ChEBI ontology, and, in order to propagate information from the ontology, the uri *http://purl.obolibrary.org/obo/CHEBI_18170* needs to be added into the graph. In the Id-mapping graph this equivalence will be represented as : *https://identifiers.org/CHEBI:18170* *skos:exactMatch* *http://purl.obolibrary.org/obo/CHEBI_18170*. *skos:exactMatch* indicating that the both concepts have exactly the same meaning, so we can pass from one to each other directly without errors, it's a transitive property.

The set of all external ressources and associated uris used in the process is indicated in the configuration file: *table_info.csv*. 
The columns are:
- ressource name
- ressource UniChem id
- all ressource available uris (comma separated)
- URI used in the SBML
- URI used in MetaNetX
- URI used in PubChem

Id-mapping graphs can be build using different sources, currently, two types of Id-mapping graphs can be build using MetaNetX and PubChem, both providing Inter and Intra uris equivalences.

#### Import SBML:

use import_SBML.py

During the SBMl import all external references (*bqbiol:is*) are extracted from the original graph and used to build an Id-mapping graph containing only Intra-uris equivalences associated to the SBML. SBML graph and the associated Id-mapping graph will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to *path_to_dir_from_dumps* and *path_to_dir_intra_from_dumps*, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/import_SBML.py --config="/path/to/config.ini"
```

* Config file:

- [VIRTUOSO]
  - path_to_dumps: path to Virtuoso shared directory
  - url: the url of the Virtuoso SPARQL endpoint
  - update_file: name of the update file
- [SBML]
  - g_path: path to the SBML graph
  - path_to_dir_from_dumps: from Virtuoso shared directory, path to the directory where the SBML graph will be stored. Should be *HumanGEM/*
  - path_to_table_infos: path to *table_info.csv*
  - path_to_dir_intra_from_dumps: from Virtuoso shared directory, path to the directory where Intra-uris equivalences will be stored. Should be *Id_mapping/Intra/*)
  - version: version of the imported SBML graph. 



#### Id-mapping graph - MetaNetX: 

use import_MetaNetX_mapping.py

According to the *table_info.csv* configuration file (*URI used in MetaNetX*), the script will build an Id-mapping graph containing both Intra and Inter uris equivalences from MetaNetX RDF graph.

In MetaNetX RDF graph, equivalences between a MetaNetX uri and external identifiers are provided using *mnx:chemXref* predicated. For example:
*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *http://identifiers.org/hmdb/HMDB01487*.
Also, if a MetaNetX uri have several external identifiers, these ressources can be linked through the MetaNetX uri. For example if:

*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *http://identifiers.org/hmdb/HMDB01487*
and
*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *https://identifiers.org/CHEBI:18170*
The Inter-uri equivalence *http://identifiers.org/hmdb/HMDB01487* *skos:closeMatch* *https://identifiers.org/CHEBI:18170* can be infered.

From the set of all used identifiers, the Intra-uris equivalence graph is build. 

The Id-mapping graph for Inter and Intra uris equivalences will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/import_MetaNetX_mapping.py --config="/path/to/config.ini"
```

* Config file:

- [VIRTUOSO]
  - path_to_dumps: path to Virtuoso shared directory
  - url: the url of the Virtuoso SPARQL endpoint
  - update_file: name of the update file
- [METANETX]
  - version: version of the Id-mapping graph. 
  - g_path: path to MetaNetX graph file (.ttl)
  - path_to_dir_from_dumps: from Virtuoso shared directory, path to the directory where the Inter-uris equivalences graph will be stored. Should be *Id_mapping/MetaNetX/*
  - path_to_table_infos: path to *table_info.csv*
- [INTRA]
  - path_to_dir_from_dumps: from Virtuoso shared directory, path to the directory where the Intra-uris equivalences graph will be stored. Should be *Id_mapping/Intra/*



#### Id-mapping graph - PubChem:

use import_PubChem_mapping.py

According to the *table_info.csv* configuration file (*URI used in PubChem*), the script will build an Id-mapping graph containing both Intra and Inter uris equivalences from PubChem type RDF graph.

In the PubChem type RDF graphs, PubChem compouds CID are describe using *rdf:type* associated a ChEBI identifier. For example:

*http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID1* *rdf:type* *http://purl.obolibrary.org/obo/CHEBI_73024*

In the Id-mapping grapĥ providing using PubChem only equivalences between PubChem CID and ChEBI identfiers are provided.

The Id-mapping graph for Inter and Intra uris equivalences will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/import_PubChem_mapping.py --config="/path/to/config.ini"
```

* Config file:

- [VIRTUOSO]
  - path_to_dumps: path to Virtuoso shared directory
  - url: the url of the Virtuoso SPARQL endpoint
  - update_file: name of the update file
- [PUBCHEM]
  - version: version of the Id-mapping graph. 
  - path_to_pubchem_dir: path to PubChem compound ressource directory
  - path_to_dir_from_dumps: from Virtuoso shared directory, path to the directory where the Inter-uris equivalences graph will be stored. Should be *Id_mapping/PubChem/*
  - path_to_table_infos: path to *table_info.csv*
- [INTRA]
  - path_to_dir_from_dumps: from Virtuoso shared directory, path to the directory where the Intra-uris equivalences graph will be stored. Should be *Id_mapping/Intra/*

#### Annotation - Id mapping:

use annot_SBML.py

To compute this step, a SBML graph and at least one Id-mapping graph should be imported in the Virtuoso RDF Store, using corresponding update files.

Using imported SBML graph and Id-mapping graphs (*MAPPING_GRAPH* section), this script will extends external ressources, by creating new links using the *bqbiol:is* predicate between species and external identifiers uris.

To do so, three main SPARQL requests are sended to determine:
  - synonyms uris: From already existing external identifier uris in the SBML graph and using Intra-uris equivalences (*skos:exactMatch*), provide uris synonyms
  - Infered uris: From already existing external identifier uris in the SBML and using Inter-uris equivalences (*skos:closeMatch*) provide new external identifiers uris
  - Infered uris synonyms: For all infered uris and using Intra-uris equivalences (*skos:exactMatch*), provide infered-uris synonyms.

Three results files are then exported corresponding to the three SPARQL queries: *synonyms.ttl*, *infered_uris.ttl*, *infered_uris_synonyms.ttl*.
These resuls files are stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/annot_SBML.py --config="/path/to/config.ini"
```
* Config file:

- [VIRTUOSO]
  - url: the url of the Virtuoso SPARQL endpoint
  - path_to_dumps: path to Virtuoso shared directory
  - update_file: name of the update file
- [MAPPING_GRAPH]
  - graph_uri: a list of all graphs uris corresponding to annotation graphs that should be used in the Id mapping annotation process (ex: *http://database/ressources/ressources_id_mapping/MetaNetX/version*)
- [SBML]
  - graph_uri: the uri of the graph corresponding to the SBML to be annotated
- [ANNOTATION_TYPE]
  - path_to_dir_from_dumps: from Virtuoso shared directory, path to the directory where the Intra-uris equivalences graph will be stored. Should be *annot_graphs/*
  - version: version of the annotation graph. 

### Annotation - Inchi & SMILES:

use annot_struct_SBML.py

Using external ressources, such as MetaNetX, PubChem and ChEBI (*EXT_SOURCES*), this script allow to fill the SBML graph with Inchi and SMILES associated to species.
To provide more associations, the Id-mapping annotation graph, describe above can also be used as sources (*EXT_SOURCES*).

For one species, and using external identifiers uris provided by the *bqbiol:is* predicate a SPARQl query will try to retrieve Inchi and SMILES from differents sources.
Two results files are then exported, one containing links between SBML species and Inchi using the *voc:hasInchi* , and the second with SMILES using the *voc:hasSmiles* predicate.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.


```bash
python3 app/SBML_upgrade/annot_struct_SBML.py --config="/path/to/config.ini"
```

* Config file:

[VIRTUOSO]
  - url: the url of the Virtuoso SPARQL endpoint
  - path_to_dumps: path to Virtuoso shared directory
  - update_file: name of the update file
[EXT_SOURCES]
graph_uri: a list of graphs used as sources. It can be graphs providing links between an identifier uri and Inchi/Smiels such as MetaNetX or ChEBI, or an Id-mapping annotation graph.
[SBML]
  - graph_uri: the uri of the graph corresponding to the SBML to be annotated
[ANNOTATION_TYPE]
path_to_dir_from_dumps: from Virtuoso shared directory, path to the directory where the Intra-uris equivalences graph will be stored. Should be *Inchi_Smiles/*
version: version of the annotation graph. 

To provide a complete annotation process, the above scripts can be executed in this order:


```bash
# Import SBML
python3 app/SBML_upgrade/import_SBML.py --config="/path/to/config.ini"
# Import MetaNetX Id - mapping
python3 app/SBML_upgrade/import_MetaNetX_mapping.py --config="/path/to/config.ini"
# Import PubChem Id - mapping
python3 app/SBML_upgrade/import_PubChem_mapping.py --config="/path/to/config.ini"
```
Load all this graphs in Virtuoso using provided upload files.

```bash
# Create Id - mapping annotation graph for the associated SBML
python3 app/SBML_upgrade/annot_SBML.py --config="/path/to/config.ini"
```
Load all this graphs in Virtuoso using provided upload files.

```bash
# Create Inchi/Smiles annotation graph for the associated SBML.
python3 app/SBML_upgrade/annot_struct_SBML.py --config="/path/to/config.ini"
```