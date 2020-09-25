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
  - version: A version. If nothing is indicated, date will be used
  - path: path to the Virtuoso shared directory (eg. /workdir/share-virtuoso/)
  - out: path to the out directory, for logs and additional files /workdir/out/
- [INCHIKEYS]
  - version: the version associated to a specific PubChem inchikey graph, like in Virtuoso shared directory. **Or** if nothing, the most recent one will be choosed. *Set version at nothing is recommended for the workflow*
- [PMID_CID]
  - version: the version associated to a specific PMID - CID graph, like in Virtuoso shared directory. **Or** if nothing, the most recent one will be choosed. *Set version at nothing is recommended for the workflow*


How to run:
```python
python3 app/ChemOnt/fetch_ChemOnt.py --config="path/to/config.ini"
```

At the end of the process, a *upload_ClassyFire.sh* file is also build in the output directory. This file contains all the *ISQL* commands that should be execute by Virtuoso to properly load all graphs and metadata.

```bash
dockvirtuoso=$(docker-compose ps | grep virtuoso | awk '{print $1}')
docker exec -t $dockvirtuoso bash -c '/usr/local/virtuoso-opensource/bin/isql-v 1111 dba "FORUM-Met-Disease-DB" ./dumps/upload_ClassyFire.sh'
```