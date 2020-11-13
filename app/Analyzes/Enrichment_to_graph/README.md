# Enrichment analysis to RDF graph

### Processes

The goal of this analysis is to convert significant associations from enrichment analysis in RDF triples.

The main source is an enrichment result table, created from the knowledge graph.

Several graphs can be created from the same enrichment table using differents parameters.

Each created graph is linked to the configuration file used to create it, indicating source files and parameters, always placed in the description attribute of the associated void.ttl

### Config files

All used configuration files are stored in the *config* directory.

- [METADATA]
  - ressource: The name of the association ressource (eg. EnrichmentAnalysis/CID_MESH) 
  - targets = URIs of graphs targeted by this analysis (eg. PubChem and MESH graph URIs)
- [PARSER] 
  - chunk_size: The chunk size used to read the enrichment result file (eg. 1000000)
  - padj_threshold: The adjusted p-value threshold (eg. 0.000001)
  - column: column name of the data.frame used for filtering
- [NAMESPACE]
  - ns: A list of URI namespaces (eg. *http://rdf.ncbi.nlm.nih.gov/pubchem/compound/*)
  - name = A list of prefix associated to namespaces, in the same order as in *ns* (eg. *compound*)
- [SUBJECTS]
  - name: The column name in the enrichment result file corresponding to desired triple subjects (eg. CID)
  - namespace = The namespace prefix of subjects, see NAMESPACE section (eg. compound)
  - prefix = A prefix which can be added before the content of the subject column (eg. CID)
- [PREDICATES]
  - name = The predicate (eg. related)
  - namespace = The namespace prefix of the predicate, see NAMESPACE section (eg. skos)
- [OBJECTS]
  - name = The column name in the enrichment result file corresponding to desired triple objects (eg. MESH)
  - namespace = The namespace prefix of subjects, see NAMESPACE section
  - prefix = A prefix which can be added before the content of the subject column.
- [OUT]
  - file_prefix = Output file names

### Run

```bash
python3 app/Analyzes/Enrichment_to_graph/convert_association_table_to_triples.py --config="path/to/config.ini" --input="path/to/input" --uri="ftp://path/to/input" --version="version" --out="path/to/out"
```
Two configuraton files are required in this process. The first (config) correspond to the confugaration file describe above, used for the convertion process. The second is the configuration file that was used during the computation process (metab2mesh_requesting_virtuoso). This configuration file is also needed to describe all the data that was used to create these triples.

- config: path to the configuration file for the conversion process
- c2mconfig: path to the configuration used in the computation analysis (metab2mesh_requesting_virtuoso)
- c2mname: name of the converted ressource (eg. CID_MESH)
- input: path to the input result table
- uri: url of the input table on the ftp server, same as used to upload it 
- version: the analysis version

**/!\ WARNING:** the path to the configuration file **MUST** be the relative path from the repository root, such as *app/Analyzes/.../.../config.ini* to correspond to the path of the file on the GitLab repo.

All triples will be exported in the Docker Virtuoso share directory. A file named *upload_Enrichment_SUBJECT_OBJECT.sh* can then be used to load triples into Virtuoso.

Several metadata are created to fully describe the created triples. The created graph is defined to be a void:Linkset and its location on the ftp server is indicated using the *void:dataDump* predicate. The result table that have been filtered to produce these triples is also indicated with the *dcterm:source* predicate. For this resource table, its location on the ftp server is also indicated using the *dcat:downloadURL* predicate and all graphs that that have been used as resource in the computation process (metab2mesh_requesting_virtuoso), to produce this table, are also indicated using the predicate *dcterm:source*.