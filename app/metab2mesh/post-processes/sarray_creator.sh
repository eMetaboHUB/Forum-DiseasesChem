#!/bin/bash

for f in `ls ~/work/metab2mesh/data/*`
do
echo "module load system/R-3.6.2; Rscript compute_fisher_exact_test.R -f \"$f\""
done

mkdir out
mkdir err
# launch: bash sarray_creator.sh > commands_metab2mesh.sh
# sarray command: sarray -J metab2mesh -o out/%j.out -e err/%j.err -t 24:00:00 --mem=2G -c 1 --mail-type=BEGIN,END,FAIL commands_metab2mesh.sh