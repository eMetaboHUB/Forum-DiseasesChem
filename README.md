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