## SBML Import & SBML annotation :

Methods describe below provide a way to import and annotate SBML file in the RDF store. 

There are two types of provided annotation for SBML graphs: Id mapping and Inchi/SMILES annotations.
### Id mapping: 

In the SBML graph, metabolite are represented as *SBMLrdf:Species* and links to external references (such as ChEBI, BiGG, KEGG, etc ...) are described using the *bqbiol:is* predicate, associated to an uri representing an external ressource identifier, ex :

*M_m02885c a  SBMLrdf:Species ;*

*M_m02885c bqbiol:is chebi:18170.*

From intial external references present in the SBML graph, the program will try to extend this annotation using Id-mapping graphs. The extend of external uris identifiers in the SBML can be done when the SBML and some Id-mapping graphs are imported in the Virtuoso RDF Store.

Id-mapping graphs are RDF graphs providing uris equivalences. There are two type of uris equivalences:

* Inter-uris equivalences:
  It defines equivalences between uris from different external ressources, where identifiers correspond to the same molecule. For example, the ChEBI id 37327 is equivalent to Pubchem CID 5372720, in the Id-mapping graph, this equivalence will be represented as : *http://identifiers.org/chebi/CHEBI:37327* *skos:closeMatch* *http://identifiers.org/pubchem.compound/5372720*. *skos:closeMatch* indicates that two concepts are sufficiently similar and that the two can be used interchangeably, nevertheless, this  is not transitive, to avoid spreading  equivalence errors.

* Intra-uris equivalences:
  For each identifiers of an external ressource, several uris can identify this entity, using different namespaces. So, Intra-uris equivalences defines equivalences between uris associated to this same external ressource entity. For exemple, for one ChEBI id 18170, 3 different uris are availables: *http://purl.obolibrary.org/obo/CHEBI_18170*, *https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:18170*, *http://identifiers.org/chebi/CHEBI:18170*. In this case *http://identifiers.org/chebi/CHEBI:18170* is used by default in the SBML graph, but *http://purl.obolibrary.org/obo/CHEBI_18170* is the uri which is used in the ChEBI ontology. So, in order to propagate information from the ontology, the uri *http://purl.obolibrary.org/obo/CHEBI_18170* needs to be added into the graph. In the Id-mapping graph this equivalence will be represented as : *https://identifiers.org/CHEBI:18170* *skos:exactMatch* *http://purl.obolibrary.org/obo/CHEBI_18170*. *skos:exactMatch* indicating that the both concepts have exactly the same meaning, so we can pass from one to each other directly without errors, it's a transitive property.

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
To load graph, use :

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/update_file.sh'
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

*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *https://identifiers.org/CHEBI:18170*

The Inter-uri equivalence *http://identifiers.org/hmdb/HMDB01487* *skos:closeMatch* *https://identifiers.org/CHEBI:18170* can be infered.

From the set of all used identifiers, the Intra-uris equivalence graph is build. 

The Id-mapping graph for Inter and Intra uris equivalences will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/import_MetaNetX_mapping.py --config="/path/to/config.ini"
```
To load graph, use :

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/update_file.sh'
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

In the PubChem type RDF graphs, PubChem compouds CID are describe using *rdf:type* associated to a ChEBI identifier. For example:

*http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID1* *rdf:type* *http://purl.obolibrary.org/obo/CHEBI_73024*

In the Id-mapping grapĥ created using PubChem only equivalences between PubChem CID and ChEBI identfiers are provided.

The Id-mapping graph for Inter and Intra uris equivalences will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/import_PubChem_mapping.py --config="/path/to/config.ini"
```
To load graph, use :

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/update_file.sh'
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
The SBML graph contains initial external identifier uris that the program will try to extends, and Id-mapping graphs contains Inter/Intra ressources equivalences to compute this process. Used Id-mapping graphs and SBML graph will be mentionned as sources in the *void.ttl* file associated to the annotation graph.

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
To load graph, use :

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/update_file.sh'
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

Using external ressources, such as MetaNetX, PubChem and ChEBI (*EXT_SOURCES*), this script allow to fill the SBML graph with Inchi and SMILES associated to species. For example: 
  - MetaNetX: *MetaNetX:MNXM10* *mnx:smiles/mnx:inchis* *Inchi or Smiles*

  - ChEBI: *chebi:100014* *chebi:inchi/chebi:smiles*  *Inchi or Smiles*

  - PubChem: *compound:CID1*  *sio:has-attribute* *descriptor:CID1_IUPAC_InChI/descriptor:CID1_IUPAC_Canonical_SMILES*

    *descriptor:CID1_IUPAC_InChI/descriptor:CID1_IUPAC_Canonical_SMILES*  *sio:has-value*  *Inchi or Smiles*


To provide more associations, the Id-mapping annotation graph, describe above can also be also used as sources (*EXT_SOURCES*) to provide more available external identifier uris.

For one species, and using external identifiers uris provided by the *bqbiol:is* predicate a SPARQl query will try to retrieve Inchi and SMILES from differents sources.
Two results files are then exported, one containing links between SBML species and Inchi using the *voc:hasInchi* predicate, and the second with SMILES using the *voc:hasSmiles* predicate.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.


```bash
python3 app/SBML_upgrade/annot_struct_SBML.py --config="/path/to/config.ini"
```
To load graph, use :

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/update_file.sh'
```

* Config file:

- [VIRTUOSO]
  - url: the url of the Virtuoso SPARQL endpoint
  - path_to_dumps: path to Virtuoso shared directory
  - update_file: name of the update file
- [EXT_SOURCES]
  - graph_uri: a list of graphs used as sources. It can be graphs providing links between an identifier uri and Inchi/Smiels such as MetaNetX or ChEBI, or an Id-mapping annotation graph.
- [SBML]
  - graph_uri: the uri of the graph corresponding to the SBML to be annotated
- [ANNOTATION_TYPE]
  - path_to_dir_from_dumps: from Virtuoso shared directory, path to the directory where the Intra-uris equivalences graph will be stored. Should be *Inchi_Smiles/*
  - version: version of the annotation graph. 

* * *

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