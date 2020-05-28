## Metabolite - Diseases Graph Database

This repository contains some usefull methods to provides links between PubChem compound identifiers, litteratures (PMIDs) and MeSH

## Install

### Install Docker:

Follow instructions at https://docs.docker.com/engine/install/ubuntu/

### Install Docker Virtuoso :

- Pull tenforce/Virtuoso image: 
```bash
docker pull tenforce/virtuoso
```
Documentation at https://hub.docker.com/r/tenforce/virtuoso

### Run Docker Virtuoso :

In the docker-virtuoso directory:
- Create a share directory:
```bash
mkdir share
```
In the *share* directory, create two sub-directories *MetaNetX* and *vocabulary*

```bash
mkdir MetaNetX
mkdir vocabulary
```
The vocabulary directory contains files associated to the schema of used ontology, they can be download using the docker ressource directory or at:

- MeSH: ftp://ftp.nlm.nih.gov/online/mesh/rdf/vocabulary_1.0.0.ttl
- ChEBI: ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.owl
- cito: http://purl.org/spar/cito.ttl
- fabio: http://purl.org/spar/fabio.ttl
- Dublin Core: https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.nt
- Cheminf: http://www.ontobee.org/ontology/CHEMINF
- skos: https://www.w3.org/2009/08/skos-reference/skos.rdf

Download data from docker-ressources and place a copy of *metanetx.ttl* in the MetaNetX directory and place all vocabulary files in the vocabulary directory.

Be sure that these paths are the same as those indicated in the workflow.sh file

To launch the Virtuoso docker, in the same directory as *docker-compose.yml*, use:
```bash
./workflow.sh
```

### Build metdisease Docker :

At the root of the repository, run:

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
Where *network="host"* allow the metdisease docker to communicate with the SPARQL endpoint of Virtuoso created by the Virtuoso docker at localhost.
Also:
- *path/to/docker-ressource*: To create the MetaNetX Id-mapping graph (Cf. *SBML Import & SBML annotation*), the script will need access to the MetaNetX .ttl file
-  *path/to/config/dir*: path to a directory containing configuration files (*optional*)
-  */path/to/virtuoso-share/dir*: All graphs created or downloaded by the provided scripts **must** be writed in the Virtuoso shared directory to be loaded (Cf. volume *share* in the docker-compose.yml).
- */path/to/out/dir*: path to an output directory, where addtional files (Cf. *build RDF Store*) and metab2mesh results files should be writed.


## Build RDF Store:

Go in the app/build_RDF_store directory to consult documentation.

## Metab2mesh :

Go in the app/metab2mesh directory to consult documentation.

## SBML Import & SBML annotation :

Go in the app/SBML_upgrade directory to consult documentation.

## Versionning :

Created data-graphs are named graphs for which the associated uri identify the graph and triples it contains in the RDF store. By this specific uri, each data-graph is associated to a version of a specific ressource. There are several main ressources such as: *MeSH*, *PubChem references*, *PubChem Descriptor*, *PubChem compounds*, *PMID_CID*, etc ... 

When a new graph is created, a new version of the associated ressource is created. For example, if a new version of PubChem compounds is build using *build_RDF_store* script, a new graph with the uri *http://database/ressources/PubChem/compound/version_X* is created as a version of the ressource *http://database/ressources/PubChem/compound*.

Several other types of metadata are associated to the created graph. All these metadata information are indicated in a metadata-graph, named *void.ttl*, which is automatically created with the data-graph in the same directory. An example of a *void.ttl* associated to a PubChem reference ressource is describe bellow:
```
<http://database/ressources/PubChem/reference> dcterms:hasVersion <http://database/ressources/PubChem/reference/version_X> .

<http://database/ressources/PubChem/reference/version_X> a void:Dataset ;
    dcterms:created "creation date of the data-graph"^^xsd:date ;
    dcterms:description "The reference subset contains RDF triples for the type and basic metadata of a given PMID."@en ;
    dcterms:subject <http://dbpedia.org/page/Reference> ;
    dcterms:title "PubChemRDF reference subset"@en ;
    void:dataDump a list of all files associated to the graph, ex: 
        <ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference/pc_reference2chemical_disease_000001.ttl.gz>,
        <ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/reference/pc_reference2chemical_disease_000002.ttl.gz>,
        ... ;
    void:distinctSubjects number of distincts subkects in the graph^^xsd:long ;
    void:exampleResource <http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID10395478> ;
    void:triples "total number of triples in the graph "^^xsd:long ;
    void:uriLookupEndpoint <http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> ;
    void:uriSpace "http://rdf.ncbi.nlm.nih.gov/pubchem/reference/"^^xsd:string .
```