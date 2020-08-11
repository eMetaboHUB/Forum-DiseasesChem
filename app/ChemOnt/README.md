# ChemOnt

In order to provide a MeSH enrichment from ChemOnt classes, the goal of this procedure is to retrieve ChemOnt classes associated to PubChem compounds, using only compounds for which a literature is available.

ChemOnt classes associated to a PubChem compound are accessible through their InchiKey at the URL http://classyfire.wishartlab.com/entities/INCHIKEY.json

For a molecule, ChemOnt classes are organised in 2 main catergories: 
- A *Direct-parent* class: representing the most dominant structural feature of the chemical compounds
- Some *Alternative parents* classes: Chemical features that also describe the molecule but do not have an ancestor–descendant relationship with each other or with the *Direct Parent* class. 

*Djoumbou Feunang, Y., Eisner, Wishart, D.S., 2016. ClassyFire: automated chemical classification with a comprehensive, computable taxonomy. J Cheminform 8, 61. https://doi.org/10.1186/s13321-016-0174-y*


These both types of classes are stored separately in two different graphs.
### Config file
- [PROCESSES]
  - n_processes: The number of molecule that will be treated in parralel. The input table will be divided in *n_processes* sub-tables, which will be treated independtly in parralel.
  - version: A version
- [OUT]
  - path: path to output directory (eg. /workdir/share-virtuoso)
- [INPUT]
- path: path to input file


How to run:
```python
python3 app/ChemOnt/fetch_ChemOnt.py --config="path/to/config.ini"
```