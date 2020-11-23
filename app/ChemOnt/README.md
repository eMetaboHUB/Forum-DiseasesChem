# ChemOnt

In order to provide a MeSH enrichment from ChemOnt classes, the goal of this procedure is to retrieve ChemOnt classes associated to PubChem compounds, using only thoose for which a literature is available. The literature information is extracted from PMID - CID graphs, while the InchiKey annotation from PubChem InchiKey graphs.

ChemOnt classes associated to a PubChem compound are accessible through their InchiKey at the URL http://classyfire.wishartlab.com/entities/INCHIKEY.json

For a molecule, ChemOnt classes are organised in 2 main catergories: 
- A *Direct-parent* class: representing the most dominant structural feature of the chemical compounds
- Some *Alternative parents* classes: Chemical features that also describe the molecule but do not have an ancestor–descendant relationship with each other or with the *Direct Parent* class. 

*Djoumbou Feunang, Y., Eisner, Wishart, D.S., 2016. ClassyFire: automated chemical classification with a comprehensive, computable taxonomy. J Cheminform 8, 61. https://doi.org/10.1186/s13321-016-0174-y*


These both types of classes are stored separately in two different graphs.
### Config file
- [PROCESSES]
  - n_processes: The number of molecule that will be treated in parralel. The input table will be divided in *n_processes* sub-tables, which will be treated independtly in parralel.
- [FTP]
  - ftp: The ftp server address on which created data will be stored. A valid adress is not mandatory as data will not be automatically upload to the ftp server, but this will be used to provide metadata (*void:dataDump* triples) in corresponding void.ttl files.


How to run:
```python
python3 app/ChemOnt/fetch_ChemOnt.py --config="path/to/config.ini" --out="/path/to/out/dir" --log="path/to/log/dir" --version="version"
```

- config: path to the configuration file
- out: path to output directory, should be the docker-virtuoso shared directory
- log: path to the log directory
- version: The version of the builded ressource. If nothing is indicated, date will be used

At the end of the process, a *upload_ClassyFire.sh* file is also build in the output directory. This file contains all the *ISQL* commands that should be execute by Virtuoso to properly load all graphs and metadata.

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/upload_ClassyFire.sh'
```