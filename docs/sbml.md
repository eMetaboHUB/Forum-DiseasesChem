## SBML Import & SBML annotation :

Methods describe below provide a way to import and annotate SBML file in the RDF store. 

### Id mapping: 

In the SBML graph, metabolite are represented as *SBMLrdf:Species* and links to external references (such as ChEBI, BiGG, KEGG, etc ...) are described using the *bqbiol:is* predicate, associated to an URI representing an external resource identifier, ex :

*M_m02885c a  SBMLrdf:Species ;*

*M_m02885c bqbiol:is chebi:18170.*

From initial external references present in the SBML graph, the program will try to extend this annotation using Id-mapping graphs. The extend of external URIs identifiers in the SBML can be done when the SBML and some Id-mapping graphs are imported in the Virtuoso triplestore.

Id-mapping graphs are RDF graphs providing URIs equivalences. There are two types of URIs equivalences:

* Inter-resources equivalences:
  It defines equivalences between URIs from different external resources, where identifiers correspond to the same molecule. For example, the ChEBI id 37327 is equivalent to the Pubchem CID 5372720, as both correspond to *Isoalloxazine*. In the Id-mapping graph, this equivalence will be represented as : *http://identifiers.org/chebi/CHEBI:37327* *skos:closeMatch* *http://identifiers.org/pubchem.compound/5372720*. *skos:closeMatch* indicates that two concepts are sufficiently similar and that the two can be used interchangeably, nevertheless, this relation is not transitive, to avoid spreading equivalence errors. The *identifiers.org *namespace will be used to represent identifiers in this type of RDF triples.

* Intra-resource equivalences:
  For each identifier of an external resource, several URIs can identify this entity, using different namespaces, but all refer semantically to the same individual. Unfortunately, different URIs representing the same individual can be used by different external resources, but these entities should be considered equivalently to allow an efficient use of all available resources. For example, for one ChEBI id 18170, there are 3 different URIs availables: *http://purl.obolibrary.org/obo/CHEBI_18170*, *https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:18170*, *http://identifiers.org/chebi/CHEBI:18170*. In this case *http://identifiers.org/chebi/CHEBI:18170* is used by default in the SBML graph, but *http://purl.obolibrary.org/obo/CHEBI_18170* is the uri which is used in the ChEBI ontology. So, in order to propagate information from the ontology, the uri *http://purl.obolibrary.org/obo/CHEBI_18170* needs to be added into the graph. In the Id-mapping graph this equivalence will be represented as : *https://identifiers.org/CHEBI:18170* *owl:sameAs* *http://purl.obolibrary.org/obo/CHEBI_18170*. The built-in OWL property *owl:sameAs* links an individual to an other individual. Such an owl:sameAs statement indicates that two URIs actually refer to the same thing: the individuals have the same "identity". While we are requesting for properties such as Inter-resources equivalences or annotations (SMILES, Inchi) all synonyms URIs of an individual are implicitly taken into account. For example, even if we request for Inchi annotation from the identifier.org uri (eg. *http://identifiers.org/chebi/CHEBI:18170*), knowing that *http://purl.obolibrary.org/obo/CHEBI_18170* and *http://identifiers.org/chebi/CHEBI:18170* are both consider to be the same individual (with *owl:sameAS*), we can thus retrieve annotation explicitly provided for *http://purl.obolibrary.org/obo/CHEBI_18170* using *http://identifiers.org/chebi/CHEBI:18170*. However, the *owl:sameAs* expansion is implicit in SPARQL queries, so for example, when requesting for all external resources associated to a SBML species, with the *bqbiol:is* predicate, not all synonyms will be displayed, but only the first individual. For getting the complete set of synonyms, a forward chaining approach should be used (using *owl:sameAs+* for instance). In conclusion, all uri synonyms of individuals are implicitly taken into account during SPARQL requests, but are not exported in results, to see all synonyms, it should be express explicitly in the request with forward chaining for instance. (See [Virtuoso sameAs Doc](http://docs.openlinksw.com/virtuoso/rdfsameas/) for more details.)

* String formatting: In RDF, strings can be formatted using literals with different approaches, having different behaviours, especially for String Escapes. This could be of importance for Inchi and SMILES identifiers that may contain "\" characters. In the turtle syntax "\" are escaped using "\\", while *xsd::string* accept directly "\". In order to correctly export SMILES or Inchi for further analysis, without supplementary "\", be sure to always export them using a classic format (csv, ..), as they will be escaped in turtle syntax for instance.


- **The resource configuration table**: app/build/data/table_info_2021.csv
- 
The set of all external resources and associated URIs used in the process is indicated in the metadata file: *table_info.csv*. 
The columns are:
- resource name
- all resource available URIs (comma separated)
- URI used in the SBML
- URI used in MetaNetX
- URI used in PubChem

Id-mapping graphs can be build using different sources, currently, two types of Id-mapping graphs can be build using MetaNetX and PubChem, both providing Inter and Intra-resource equivalences.

#### Import SBML:

use app/build/import_SBML.py

From an SBML file in XML, the script first converts it into RDF (turtle format) using SBML2RDF (see https://services.pfem.clermont.inrae.fr/gitlab/forum/sbml2rdf)

During the SBMl import all external references (*bqbiol:is*) are extracted from the original graph and used to build an Id-mapping graph containing only Intra-resource equivalences associated to the SBML. SBML graph and the associated Id-mapping graph will be stored in the Virtuoso shared directory, ready to be loaded.

```bash
python3 -u app/build/import_SBML.py --config="config/release-2021/config_Human1_1.7.ini" --out="/workdir/share-virtuoso"
```

##### Config

- [SBML]
  - path = path to the original sbml file in xml
  - version = the version. If this version already exists (a valid void.ttl file found at *share/PMID_CID/{version}/void.ttl), the computation will be skiped and only the upload file will be produced.
- [DEFAULT]
  - upload_file = the name of the upload file
- [RDF]
  - path = output path for the convertion step
- [META]
  - path = path to the resource configuration table
- [VOID]
  - description = a description for the void file of the SBML graph
  - title = a title for the void file of the SBML graph
  - source = a dcterms:source for the void file of the SBML graph (eg. a link to the Git repo)
  - seeAlso = a dcterms:seeAlso for the void file of the SBML graph (eg. the DOI of the pubication)


#### Id-mapping graph - MetaNetX: 

use import_MetaNetX_mapping.py

According to the *resource configuration table*, the script will build an Id-mapping graph containing both Intra and Inter URIs equivalences from the MetaNetX RDF graph.

In MetaNetX RDF graph, equivalences between a MetaNetX uri and external identifiers are provided using *mnx:chemXref* predicate. For example:
*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *http://identifiers.org/hmdb/HMDB01487*.
Also, if a MetaNetX uri have several external identifiers, these resources can be linked through the MetaNetX uri. For example if:

*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *http://identifiers.org/hmdb/HMDB01487*

*http://identifiers.org/metanetx.chemical/MNXM10* *mnx:chemXref*  *https://identifiers.org/CHEBI:18170*

The Inter-resources equivalence *http://identifiers.org/hmdb/HMDB01487* *skos:closeMatch* *https://identifiers.org/CHEBI:18170* can be inferred.

From the set of all used identifiers, the Intra-resource equivalence graph is build. 

The Id-mapping graph for Inter and Intra URIs equivalences will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 -u app/build/import_MetaNetX_mapping.py --config="/workdir/config/release-2021/import_MetaNetX_mapping.ini" --out="/workdir/share-virtuoso"
```

##### Config

- [DEFAULT]
  - upload_file = the name of the upload file
- [METANETX]
  - version = the version. If this version already exists (a valid void.ttl file found at *share/PMID_CID/{version}/void.ttl), the computation will be skiped and only the upload file will be produced.
  - file_name = the name of the MetaNetX file (usually metanetx.ttl.gz)
- [META]
  - path = path to the resource configuration table


#### Id-mapping graph - PubChem:

use app/build/import_PubChem_mapping.py

According to the *resource configuration table* configuration file, the script will build an Id-mapping graph containing both Intra and Inter URIs equivalences from PubChem type RDF graph.

In the PubChem type RDF graphs, PubChem compouds CID are describe using *rdf:type* associated to a ChEBI identifier. For example:

*http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID1* *rdf:type* *http://purl.obolibrary.org/obo/CHEBI_73024*

In the Id-mapping graph created using PubChem only equivalences between PubChem CID and ChEBI identifiers are provided.

The Id-mapping graph for Inter and Intra URIs equivalences will be stored in the Virtuoso shared directory (at *path_to_dumps*) according to the  *path_to_dir_intra_from_dumps* specify in the corresponding section, ready to be loaded.
To facilitate graph loading, the script return an update file (*update_file*) in the Virtuoso shared directory, containing all ISQL commands needed to properly load graphs, that have to be executed by Virtuoso.

```bash
python3 -u app/build/import_PubChem_mapping.py --config="/workdir/config/release-2021/import_PubChem_mapping.ini" --out="/workdir/share-virtuoso"
```

##### Config

- [DEFAULT]
  - upload_file = the name of the upload file
- [PUBCHEM]
  - version = the version. If this version already exists (a valid void.ttl file found at *share/PMID_CID/{version}/void.ttl), the computation will be skiped and only the upload file will be produced.
  - path_to_dir = path to the PubChem compound directory from *share*
  - mask = the mask of the PubChem compound files containing the ChEBI rdf:type annotations (usually *_type*.ttl.gz)
- [META]
  - path = path to the resource configuration table

#### Annotations :


To compute this step, a SBML graph and at least one Id-mapping (MetaNetX or PubChem) graph should be imported in the Virtuoso RDF Store, using corresponding update files.
The SBML graph contains initial external identifier URIs that the KG will try to extend, and Id-mapping graphs contains Inter/Intra equivalences for this purpose.

Some Inter-resource equivalences are provided with URIs that are not directly annotated in the SBML, but which are synonyms of annotated URIs. Intra-resource equivalences being represented with the *owl:sameAs* predicate, link between synonyms is implicit in the knowledge graph. All URIs synonyms of a same individual (like a ChEBI identifier) benefits of all annotations associated to each synonym, because they are semantically the same individual.

For example a specie in the SBMl can be annotated with the URIs: *<https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:16424>*. None Inter-resource equivalences are explicitly provided in graphs using this uri, but, being the synonym of *<http://purl.obolibrary.org/obo/CHEBI_16424>*, which is the uri used in the MetaNetX database, all annotations associated to this uri can be linked to *<https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:16424>* and thus, extend annotations in the SBML.

To have access to all the identifiers, use: 
```SQL
DEFINE input:inference 'schema-inference-rules'
DEFINE input:same-as "yes"

select distinct ?specie ?ext_ref 
where {
		?specie a SBMLrdf:Species ;
			(bqbiol:is|bqbiol:is/skos:closeMatch) ?ext_ref .
}
```

To determine just the new identifiers that can be inferred from the existing ones in the SBML using Intra/Inter equivalences, we can use :

```SQL
DEFINE input:inference 'schema-inference-rules'
DEFINE input:same-as "yes"


select distinct ?specie ?otherRef 
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
  *Warning:* These annotations from PubChem's Compound and Descriptor graphs can consume a lot of resources to load as the graphs are huges, with several billions of triples. But for metabolic network annotation, PubChem's data could be very redundant with ChEBI and MetaNetX information, which are also more generally used in SBML annotation. We advise to only use MetaNetX and ChEBI annotation in a first time and then, if annotations are not sufficients, try to add PubChem's Compound and Descriptor graphs. 

For all SBML species, using external identifiers provided by the *bqbiol:is* and those that we can infer from Intra/Inter equivalences using *skos:closeMatch*, in all therefore equivalent to the property path *bqbiol:is|bqbiol:is/skos:closeMatch*, we can use a SPARQL query to retrieve Inchi and SMILES annotations

Replace "[model_URI]" with the actual namespace of the model (eg. https://forum.semantic-metabolomics.org/SBML/Human1/1.7#)

* For InchI
```SQL
DEFINE input:inference 'schema-inference-rules'
DEFINE input:same-as "yes"

SELECT distinct (strafter(STR(?specie), "[model_URI]") as ?SPECIE) ?selected_inchi
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

SELECT distinct (strafter(STR(?specie), "[model_URI]") as ?SPECIE) ?selected_smiles
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