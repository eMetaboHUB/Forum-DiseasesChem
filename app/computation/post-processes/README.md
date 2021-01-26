# FORUM - Post-processes

For all computed statistical analysis, counts and identifiers will be determined according to the column order in the result file produced by the compound2mesh analysis. For instance, for a variable $X$ representing chemical entities and a variable $Y$ representing MeSh descriptors:
Column 1: Compound identifiers (Variable $X$)
Column 2: MeSH descriptor identifiers (Variable $Y$)
Column 3: Co-occurrences
Column 4: Compounds' corpus size
Column 5: MeSH descriptors' corpus size
Column 6: Univers size

## Step 1 - Compute statistics tests:

For each association, are computed :
- The p-value of the Fisher exact test right-tailed
- The odds-ratio
- The Fold-Change
- The Chisq statistics


### Parameters

- file: The path to the input file (obtain with *requesting_virtuoso.py*)
- chunksize: Chunks size while reading the input file
- parallel: The number of cores to be used
- p_out: The path to the output file

```bash
Rscript app/computation/post-processes/compute_fisher_exact_test.R --file="/path/to/input" --chunksize=nchunk --parallel=ncores --p_out="/path/to/out"
```
According to the configuration file of the compound2mesh procedure (requesting_virtuoso.py), the resulting table contains the statistical analysis for each association between modalities of the variable $X$ and the variable $Y$.

## Step 2 - Adjust p-values

After all *p-values* have been computed, we need to estimate the False Discovery Rate using the BH procedure.

### Parameters

- p_associations: The path to the input file containing association and related statistics (obtained at step 1)
- p_out: The path to the output file

```bash
Rscript app/computation/post-processes/post_process.R --p_associations="/path/to/file" --p_out="/path/to/out"
```

## Step 3 - Weakness testing

The *fragility index* aims at determining the number $`n`$ of articles, that if removed from the corpus, would return an unsignificant *p-value* according to the set threshold (option --threshold). To determine $`n`$, we estimate several scenarios in which a growing number of articles supporting the relation between for instance, a compound (or a chemical class) $`A`$ and a MeSH descriptor $`B`$ would be removed. Nonethelesss, all scenarios can't be tested for computational reasons and we need to establish bounds in which determine scenarios. We used the Jeffrey interval for a given $`\alpha`$ (option --alphaCI) to determine a confidence interval arround the proportion of articles discussing about a MeSH descriptors $`B`$ among those discussing about the compound $`A`$, $`\frac{N_{ij}}{N_{i.}}`$ with $`N_{ij}`$ the number of article discussing about the MeSH $`j`$ and the compound $`i`$ (the co-occurrences) and $`N_{i.}`$ the total number of articles discussing about the compound $`i`$. We compute this proportion regarding to the compound corpus size, because most of them are unfortunately not well described in the literature, contrary to studied MeSH descriptors. 

In the script, the $`X`$ variable is used as reference to compute the Jeffrey's CI, according to the the co-occurrence in column 3 and corpus sizes of variable $`X`$ modalities in column 4. In the performed analysis, the variable $`X`$ therefore always correspond to chemical entities.

Using the lowest bound $`p_{min}`$ of the interval, we estimated by rounding $`N_{min}`$, the co-occurrence, corresponding to the  scenario that lead to such minimal proportion: $`N_{min} \approx p_{min} N`$.

We first test using this lowest scenario: if the test is still significant, the association is declared robust and none other test are computed, else, we compute all possible scenarios from $`N_{min}`$ to the observed co-occutrences, to determine the first scenario that fail. Using this failing scenario, we determine $`n`$, the number of articles that if removed from the corpus, makes the *p-value* over the significance threshold $`p-value \le 1e−6`$. The *q-value* being always higher or equal than the *p-value*, this also informs us about the *q-value* that could be obtains from this scenarios, and thus if this association could still be instantiated in our graph.

For more details, see the article.

### Parameters

- file: path to the input file (obtain with *requesting_virtuoso.py*)
- threshold: the significance threshold (eg. 1e-6)
- alphaCI: the alpha related to the covidence interval (eg. 0.05 for a CI at 95%)
- chunksize: the size of the chunk while reading the input file
- parallel: the number of cores that should be used
- p_out: The path to the output file

```bash
Rscript app/computation/post-processes/weakness/weakness_test.R --file="/path/to/input" --threshold=th --alphaCI=alpha --chunksize=nchunk --parallel=ncores --p_out="/path/to/out"
```