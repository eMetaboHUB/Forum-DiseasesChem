# FORUM - Post-processes

## Step 1 - Compute statistics tests:

For each association, are computed :
- The p-value of the Fisher exact test right-tailed
- The odds-ratio
- The Fold-Change
- The Chisq statistics

Two versions of this procedure exist.
The first which need to be used on SLURM: *compute_fisher_exact_test.R* with *sarray.sh* to create the array of jobs.

And the second (**recommended**) which can be used with the FORUM's Docker.

### Parameters

- file: path to the input file (obtain with *metab2mesh_requesting_virtuoso.py*)
- chunksize: the size of chunks while reading the input file
- parallel: the number of cores that should be used

```bash
Rscript app/metab2mesh/post-processes/compute_fisher_exact_test_V2.R --file="/path/to/input" --chunksize=nchunk --parallel=ncores
```
At the end of the procedure a new file *input_file*_results.csv will be outputed in the same directory as the input file with the four added columns.


## Step 2 - Adjust p-values

After all p-value have been computed, they need to be adjusted using the BH procedure.

### Parameters

- p_metab2mesh: The path to the input file containing association and related statistics (obtained at step 1)
- Xname: The name of the first variable used in the procudre (eg. CID) as indicated on the configuration file of *metab2mesh_requesting_virtuoso.py*
- Yname: The name of the second variable used in the procudre (eg. MESH) as indicated on the configuration file of *metab2mesh_requesting_virtuoso.py*
- Yname: The name of the variable representing individuals in the procudre (eg. PMID) as indicated on the configuration file of *metab2mesh_requesting_virtuoso.py*
- p_out: The path to the output file

```bash
Rscript app/metab2mesh/post-processes/post_process_metab2mesh.R --p_metab2mesh="/path/to/file" --Xname="X_name" --Yname="Y_name" --Uname="U_name" --p_out="/path/to/out"
```

## Step 3 - Weakness testing

For all associations, compute the weakness procedure: If the association is significant at a considered threshold, try to determined at the lower boundary of the confidence interval arround the coocurence, if it is still significant. If the significance threshold can be reached in the confidence interval, additional values are also reported like the number of articles that should be remove to discredit the association.

### Parameters

- file: path to the input file (obtain with *metab2mesh_requesting_virtuoso.py*)
- threshold: the significance threshold (eg. 1e-6)
- alphaCI: the alpha related to the covidence interval (eg. 0.05 for a CI at 95%)
- chunksize: the size of the chunk while reading the input file
- parallel: the number of cores that should be used

```bash
Rscript app/metab2mesh/post-processes/compute_fisher_exact_test_V2.R --file="/path/to/input" --threshold=th --alphaCI=alpha --chunksize=nchunk --parallel=ncores
```