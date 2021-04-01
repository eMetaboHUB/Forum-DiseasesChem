## SBML Import & SBML annotation :

Methods describe below provide a way to import and annotate SBML file in the RDF store. 

There are two types of provided annotation for SBML graphs: Id mapping and Inchi/SMILES annotations.
### Id mapping: 

In the SBML graph, metabolite are represented as *SBMLrdf:Species* and links to external references (such as ChEBI, BiGG, KEGG, etc ...) are described using the *bqbiol:is* predicate, associated to an uri representing an external resource identifier, ex :

*M_m02885c a  SBMLrdf:Species ;*

*M_m02885c bqbiol:is chebi:18170.*

From initial external references present in the SBML graph, the program will try to extend this annotation using Id-mapping graphs. The extend of external uris identifiers in the SBML can be done when the SBML and some Id-mapping graphs are imported in the Virtuoso triplestore.

Id-mapping graphs are RDF graphs providing uris equivalences. There are two types of uris equivalences:

* Inter-resources equivalences:
  It defines equivalences between uris from different external resources, where identifiers correspond to the same molecule. For example, the ChEBI id 37327 is equivalent to the Pubchem CID 5372720, as it both correspond to *Isoalloxazine*. In the Id-mapping graph, this equivalence will be represented as : *http://identifiers.org/chebi/CHEBI:37327* *skos:closeMatch* *http://identifiers.org/pubchem.compound/5372720*. *skos:closeMatch* indicates that two concepts are sufficiently similar and that the two can be used interchangeably, nevertheless, this relation is not transitive, to avoid spreading equivalence errors. The *identifiers.org *namespace will be used to represent identifiers in this type of RDF triples.

* Intra-resource equivalences:
  For each identifier of an external resource, several uris can identify this entity, using different namespaces, but all refer semantically to the same individual. Unfortunately, different URIs representing the same individual can be used by different external resources, but these entities should be considered equivalents to allow an efficient use of all available resources. For example, for one ChEBI id 18170, there are 3 different uris availables: *http://purl.obolibrary.org/obo/CHEBI_18170*, *https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:18170*, *http://identifiers.org/chebi/CHEBI:18170*. In this case *http://identifiers.org/chebi/CHEBI:18170* is used by default in the SBML graph, but *http://purl.obolibrary.org/obo/CHEBI_18170* is the uri which is used in the ChEBI ontology. So, in order to propagate information from the ontology, the uri *http://purl.obolibrary.org/obo/CHEBI_18170* needs to be added into the graph. In the Id-mapping graph this equivalence will be represented as : *https://identifiers.org/CHEBI:18170* *owl:sameAs* *http://purl.obolibrary.org/obo/CHEBI_18170*. The built-in OWL property *owl:sameAs* links an individual to an individual. Such an owl:sameAs statement indicates that two URI references actually refer to the same thing: the individuals have the same "identity". While we are requesting for properties such as Inter-resources equivalences or annotations (SMILES, Inchi) all synonyms uris of an individual are implicitly taken into account. For example, even if we request for Inchi annotation from the identifier.org uri (eg. *http://identifiers.org/chebi/CHEBI:18170*), knowing that *http://purl.obolibrary.org/obo/CHEBI_18170* and *http://identifiers.org/chebi/CHEBI:18170* are both consider to be the same individual (with *owl:sameAS*), we can thus retrieve annotation explicitly indicated for *http://purl.obolibrary.org/obo/CHEBI_18170* using *http://identifiers.org/chebi/CHEBI:18170*. However, the same-As expansion is implicit in SPARQL queries, so for example, when requesting for all external resources associated to a SBML species, with the *bqbiol:is* predicate, not all synonyms will be displayed, but only the first individual. For getting the complete set of synonyms, a forward chaining approach should be used (using *owl:sameAs+* for instance). In conclusion, all uri synonyms of individuals are implicitly taken into account during SPARQL requests, but are not exported in results, to see all synonyms, it should be express explicitly in the request with forward chaining for instance. (See [Virtuoso sameAs Doc](http://docs.openlinksw.com/virtuoso/rdfsameas/) for more details.)

* String formatting: In RDF, strings can be formatted using literals with different approaches, having different behaviours, especially for String Escapes. This could be of importance for Inchi and SMILES identifiers that may contain "\" characters. In the turtle syntax "\" are escaped using "\\", while *xsd::string* accept directly "\". In order to correctly export SMILES or Inchi for further analysis, without supplementary "\", be sure to always export them using a classic format (csv, ..), as they will be escaped in turtle syntax for instance.

The set of all external resources and associated uris used in the process is indicated in the metadata file: *table_info.csv*. 
The columns are:
- resource name
- all resource available uris (comma separated)
- URI used in the SBML
- URI used in MetaNetX
- URI used in PubChem

Id-mapping graphs can be build using different sources, currently, two types of Id-mapping graphs can be build using MetaNetX and PubChem, both providing Inter and Intra-resource equivalences.

There is a single configuration file for all imports at *SBML_upgrade/config/config.ini* !

#### Import SBML:

use import_SBML.py

During the SBMl import all external references (*bqbiol:is*) are extracted from the original graph and used to build an Id-mapping graph containing only Intra-resource equivalences associated to the SBML. SBML graph and the associated Id-mapping graph will be stored in the Virtuoso shared directory, ready to be loaded.
To facilitate graph loading, the script return an update file (*SBML_upload_file.sh*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/import_SBML.py --config="/path/to/config.ini" --out="/path/to/output/dir" --sbml="/path/to/smbl/rdf/file" --version="version"
```

- config: path to the configuration file
- out: path to output directory
- sbml: path to sbml file
- version: version of the SBML RDF file

* Config file:

- [FTP]
  - ftp: The ftp server address on which created data will be stored. A valid adress is not mandatory as data will not be automatically upload to the ftp server, but this will be used to provide metadata (*void:dataDump* triples) in corresponding void.ttl files.
- [SBML]
  - format: format of the SBML rdf file, supported by the python library rdflib 5.0.0 (eg. turtle)
- [META]
  - path: path to the metadata file (should be app/SBML_upgrade/table_info.csv)

To load graph, use :

```bash
dockvirtuoso=$(docker ps | grep virtuoso | awk '{print $1}')
docker exec $dockvirtuoso isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/SBML_upload_file.sh
```




#### Id-mapping graph - MetaNetX: 

use import_MetaNetX_mapping.py

According to the *table_info.csv* configuration file (*URI used in MetaNetX*), the script will build an Id-mapping graph containing both Intra and Inter uris equivalences from MetaNetX RDF graph.

In MetaNetX RDF graph, equivalences between a MetaNetX uri and external identifiers are provided using *mnx:chemXref* predicate. For example:
*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *http://identifiers.org/hmdb/HMDB01487*.
Also, if a MetaNetX uri have several external identifiers, these resources can be linked through the MetaNetX uri. For example if:

*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *http://identifiers.org/hmdb/HMDB01487*

*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *https://identifiers.org/CHEBI:18170*

The Inter-resources equivalence *http://identifiers.org/hmdb/HMDB01487* *skos:closeMatch* *https://identifiers.org/CHEBI:18170* can be inferred.

From the set of all used identifiers, the Intra-resource equivalence graph is build. 

The Id-mapping graph for Inter and Intra uris equivalences will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/import_MetaNetX_mapping.py --config="/path/to/config.ini" --out="/path/to/out/dir" --version="version"
```
- config: path to the configuration file
- out: path to output directory
- version: version of the MetaNetX RDF resource, according to the one which was downloaded using build_rdf_store (Cf. buid_rdf_store config).

* Config file:

- [FTP]
  - ftp: The ftp server address on which created data will be stored. A valid adress is not mandatory as data will not be automatically upload to the ftp server, but this will be used to provide metadata (*void:dataDump* triples) in corresponding void.ttl files.
- [META]
  - path: path to the metadata file (should be app/SBML_upgrade/table_info.csv)

To load graph, use :

```bash
dockvirtuoso=$(docker ps | grep virtuoso | awk '{print $1}')
docker exec $dockvirtuoso isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/Id_mapping_MetaNetX_upload_file.sh
```

#### Id-mapping graph - PubChem:

use import_PubChem_mapping.py

According to the *table_info.csv* configuration file (*URI used in PubChem*), the script will build an Id-mapping graph containing both Intra and Inter uris equivalences from PubChem type RDF graph.

In the PubChem type RDF graphs, PubChem compouds CID are describe using *rdf:type* associated to a ChEBI identifier. For example:

*http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID1* *rdf:type* *http://purl.obolibrary.org/obo/CHEBI_73024*

In the Id-mapping graph created using PubChem only equivalences between PubChem CID and ChEBI identifiers are provided.

The Id-mapping graph for Inter and Intra uris equivalences will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 app/SBML_upgrade/import_PubChem_mapping.py --config="/path/to/config.ini" --out="/path/to/out/dir" --version="version"
```

- config: path to the configuration file
- out: path to output directory
- version: version of the PubChem Compound resource, according to the one which was downloaded using build_rdf_store (Cf. buid_rdf_store config). Only the *type* will be used to provide a mapping between PubChem compounds and ChEBI identifiers.

To load graph, use :

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/update_file.sh'
```

* Config file:

- [FTP]
  - ftp: The ftp server address on which created data will be stored. A valid adress is not mandatory as data will not be automatically upload to the ftp server, but this will be used to provide metadata (*void:dataDump* triples) in corresponding void.ttl files.
- [META]
  - path: path to the metadata file (should be app/SBML_upgrade/table_info.csv)

#### Annotations :


To compute this step, a SBML graph and at least one Id-mapping (MetaNetX or PubChem) graph should be imported in the Virtuoso RDF Store, using corresponding update files.
The SBML graph contains initial external identifier uris that the program will try to extend, and Id-mapping graphs contains Inter/Intra equivalences for this purpose.


Some Inter-resource equivalences are provided with uris that are not directly annotated in the SBML, but which are synonyms of annotated uris. Intra-resource equivalences being represented with the *owl:sameAs* predicate, link between synonyms is implicit in the knowledge graph. All uris synonyms of a same individual (like a ChEBI identifier) benefits of all annotations associated to each synonym, because they are semantically the same individual.

For example a specie in the SBMl can be annotated with the uris: *<https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:16424>*. None Inter-resource equivalences are explicitly provided in graphs using this uri, but, being the synonym of *<http://purl.obolibrary.org/obo/CHEBI_16424>*, which is the uri used in the MetaNetX database, all annotations associated to this uri can be linked to *<https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:16424>* and thus, extend annotations in the SBML.

To determine all new identifiers that can be inferred from the existing ones in the SBML using Intra/Inter equivalences, we can use :

```SQL
DEFINE input:inference 'schema-inference-rules'
DEFINE input:same-as "yes"
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix skos: <http://www.w3.org/2004/02/skos/core#>

select ?specie ?otherRef . 
where {
		?specie a SBMLrdf:Species ;
			bqbiol:is ?ref .
		?ref skos:closeMatch ?otherRef .
		FILTER (
			not exists { ?specie bqbiol:is ?otherRef }
		)
}
```

### Annotation - Inchi & SMILES:

Using external resources, such as MetaNetX, PubChem and ChEBI, we can extract Inchi and SMILES associated to species, according to some triples such as:
  - MetaNetX: *MetaNetX:MNXM10* *mnx:smiles/mnx:inchis* *Inchi or Smiles*

  - ChEBI: *chebi:100014* *chebi:inchi/chebi:smiles*  *Inchi or Smiles*

  - PubChem: *compound:CID1*  *sio:has-attribute* *descriptor:CID1_IUPAC_InChI/descriptor:CID1_IUPAC_Canonical_SMILES*
    *descriptor:CID1_IUPAC_InChI/descriptor:CID1_IUPAC_Canonical_SMILES*  *sio:has-value*  *Inchi or Smiles*


For all SBML species, using external identifiers provided by the *bqbiol:is* and those that we can infer from Intra/Inter equivalences using *skos:closeMatch*, in all therefore equivalent to the property path *bqbiol:is|bqbiol:is/skos:closeMatch*, we can use a SPARQL query to retrieve Inchi and SMILES annotations

* For InchI
```SQL
DEFINE input:inference 'schema-inference-rules'
DEFINE input:same-as "yes"
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
prefix mnx: <https://rdf.metanetx.org/schema/>
prefix sio: <http://semanticscience.org/resource/>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix skos: <http://www.w3.org/2004/02/skos/core#>

SELECT distinct ?specie ?selected_inchi
where {
  ?specie a SBMLrdf:Species ;
    SBMLrdf:name ?spe_name ;
    (bqbiol:is|bqbiol:is/skos:closeMatch) ?ref .

  { ?ref mnx:inchi ?inchi . }
  UNION
  { ?ref <http://purl.obolibrary.org/obo/chebi/inchi> ?inchi . }
  UNION
  { 
  ?ref sio:has-attribute ?ref_pc_desc .
  ?ref_pc_desc a sio:CHEMINF_000396 ;
    sio:has-value ?inchi
  }
BIND(str(?inchi) as ?selected_inchi)
}
```
* For SMILES

```SQL
DEFINE input:inference 'schema-inference-rules'
DEFINE input:same-as "yes"
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
prefix mnx: <https://rdf.metanetx.org/schema/>
prefix sio: <http://semanticscience.org/resource/>
prefix owl: <http://www.w3.org/2002/07/owl#>
prefix skos: <http://www.w3.org/2004/02/skos/core#>

SELECT distinct ?specie ?selected_smiles
where {
  ?specie a SBMLrdf:Species ;
    SBMLrdf:name ?spe_name ;
    (bqbiol:is|bqbiol:is/skos:closeMatch) ?ref .

  { ?ref mnx:smiles ?smiles . }
  UNION
  { ?ref <http://purl.obolibrary.org/obo/chebi/smiles> ?smiles . }
  UNION
  { 
  ?ref sio:has-attribute ?ref_pc_desc .
  ?ref_pc_desc a sio:CHEMINF_000376 ;
    sio:has-value ?smiles
  }
BIND(str(?smiles) as ?selected_smiles)
}

```


```bash
# Import SBML
python3 app/SBML_upgrade/import_SBML.py --config="/path/to/config.ini" --out="/path/to/output/dir" --sbml="/path/to/smbl/rdf/file" --version="version"
# Import MetaNetX Id - mapping
python3 app/SBML_upgrade/import_MetaNetX_mapping.py --config="/path/to/config.ini" --out="/path/to/out/dir" --version="version"
# Import PubChem Id - mapping
python3 app/SBML_upgrade/import_PubChem_mapping.py --config="/path/to/config.ini" --out="/path/to/out/dir" --version="version"
```
Load all this graphs in Virtuoso using provided upload files and then we can requests for identifiers, smiles, inchi, etc ...

**All this workflow can be achieved using: workflow/w_upload_metabolic_network**