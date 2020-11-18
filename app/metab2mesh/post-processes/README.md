# FORUM - Post-processes

## Step 1 - Compute statistics tests:

For each association, are computed :
- The p-value of the Fisher exact test right-tailed
- The odds-ratio
- The Fold-Change
- The Chisq statistics


### Parameters

- file: The path to the input file (obtain with *metab2mesh_requesting_virtuoso.py*)
- chunksize: Chunks size while reading the input file
- parallel: The number of cores to be used
- p_out: The path to the output file

```bash
Rscript app/metab2mesh/post-processes/compute_fisher_exact_test.R --file="/path/to/input" --chunksize=nchunk --parallel=ncores --p_out="/path/to/out"
```
According to the configuration file of the compound2mesh procedure (metab2mesh_requesting_virtuoso.py), the resulting table contains the statistical analysis for each association between modalities of the variable $X$ (identifiers in the column 1 and corpus size in the column 4) and the variable $Y$ (identifiers in the column 2 and corpus size in the column 5), with their co-occurence in column 3.

For the next step, computation will be performed according to this column order !

## Step 2 - Adjust p-values

After all p-value have been computed, they need to be adjusted using the BH procedure.

### Parameters

- p_metab2mesh: The path to the input file containing association and related statistics (obtained at step 1)
- p_out: The path to the output file

```bash
Rscript app/metab2mesh/post-processes/post_process_metab2mesh.R --p_metab2mesh="/path/to/file" --p_out="/path/to/out"
```

## Step 3 - Weakness testing

The \textit{fragility index} aims at determining the number $n$ of articles, that if removed from the corpus, would return an unsignificant \textit{p-value}. To determine $n$, we estimate several scenarios in which a growing number of articles supporting the relation between for instance, a compound (or a chemical class) $A$ and a MeSH descriptor $B$ would be removed. Nonethelesss, all scenarios can't be tested for computational reasons and we need to establish bounds in which determine scenarios. We used the Jeffrey interval (at 95\%) to determine a confidence interval arround the proportion of articles discussing about a MeSH descriptors $B$ among those discussing about the compound $A$, $\frac{N_{ij}}{N_{i.}}$ with $N_{ij}$ the number of article discussing about the MeSH $j$ and the compound $i$ (the co-occurrences) and $N_{i.}$ the total number of articles discussing about the compound $i$. We compute this proportion regarding to the compound corpus size, because most of them are unfortunately not well described in the literature, contrary to studied MeSH descriptors. 

In the script, the $X$ variable is used as reference to compute the Jeffrey's CI, according to the the co-occurence in column 3 and corpus sizes of variable $X$ modalities in column 4. In the performed analysis, the variable $X$ therefore always correspond to chemical entities.

Using the lowest bound $p_{min}$ of the interval, we estimated by rounding $N_{min}$, the co-occurrence, corresponding to the  scenario that lead to such minimal proportion: $N_{min} \approx p_{min} N$.

We first test using this lowest scenario: if the test is still significant, the association is declared robust and none other test are computed, else, we compute all possible scenarios from $N_{min}$ to the observed co-occurences, to determine the first scenario that fail. Using this failing scenario, we determine $n$, the number of articles that if removed from the corpus, makes the \textit{p-value} over the significance threshold $p-value \le 1e−6$. The \textit{q-value} being always higher or equal than the \textit{p-value}, this also informs us about the \textit{q-value} that could be obtains from this scenarios, and thus if this association could still be instantiated in our graph.

### Parameters

- file: path to the input file (obtain with *metab2mesh_requesting_virtuoso.py*)
- threshold: the significance threshold (eg. 1e-6)
- alphaCI: the alpha related to the covidence interval (eg. 0.05 for a CI at 95%)
- chunksize: the size of the chunk while reading the input file
- parallel: the number of cores that should be used
- p_out: The path to the output file

```bash
Rscript app/metab2mesh/post-processes/weakness/weakness_test.R --file="/path/to/input" --threshold=th --alphaCI=alpha --chunksize=nchunk --parallel=ncores --p_out="/path/to/out"
```