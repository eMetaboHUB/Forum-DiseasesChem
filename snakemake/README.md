## install

### Installation via Conda/Mamba

```bash
conda install -n base -c conda-forge mamba
```

### Create env conda

```bash
conda activate base
mamba create -c conda-forge -c bioconda -n snakemake snakemake
```

## To activate this environment, use

```bash
conda activate snakemake
```

## To deactivate an active environment, use

```bash
conda deactivate
```

## testing workflow 

```bash
snakemake --dry-run 
snakemake --dry-run --verbose
```

## run
```bash
snakemake --cores 2
```