## Requierements:

- Check that the docker virtuoso image is installted :
If not 
  - Pull tenforce/Virtuoso image: 
  ```bash
  docker pull tenforce/virtuoso
  ``` 

You can use the docker-image provided containing all needed packages and librairies. It's not mandatory, each script can be executed without if all R packages and python libraries are installed.

if you want to use the docker image, first install it :
```bash
docker build -t forum/processes .
```
Then, launch it:

```bash
docker run --name forum_scripts --rm -it --network="host" \
-v /path/docker-virtuoso/share:/workdir/share-virtuoso \
-v /path/to/data/dir:/workdir/out \
forum/processes bash
```




### Compute chemical entities to MeSH assoctions

#### Init Virtoso
```bash
./workflow/w_virtuoso.sh -d /media/mxdelmas/Elements/TEST/docker-virtuoso -s share start
```

#### Set configuration files: 
For each analysis, there are two main configuration files: 
- The first refer of paramters required during the 



#### Compute PubChem compounds - MeSH associations


#### Compute ChEBI - MeSH associations
Run inside the docker forum_scripts (forum/processes) or in your environment :

```bash
./workflow/w_compound2mesh.sh -v *version* -m */path/to/config/ChEBI2MeSH* -t *path/to/config/triplesConverter/ChEBI2MeSH* -u CHEBI_MESH -d */path/to/data/dir* -s */path/to/virtuoso/share/dir*
```