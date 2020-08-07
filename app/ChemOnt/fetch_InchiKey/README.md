## Fetch CID - InchiKey annotations

- Download PubChem_InchiKey directory using function download_PubChem in build_RDF_store. Now, it's included in the build_RDF_store.py script with all others PubChem directories.

- Load data in Virtuoso using upload_get_info_for_ClassyFire.sh

- Get all available InchiKey annotation for CID which have linked literatures using request.rq

### results

We obtains 373765 CID - InchiKey annotations. But there are 373835 CID with annotated litterature, so there are 70 CID for which we don't get the associated inchiKey from PubChem.
