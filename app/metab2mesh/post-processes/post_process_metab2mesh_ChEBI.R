library(optparse)
library(tidyverse)
option_list <- list(
  make_option(c("-i", "--p_metab2mesh"), type="character", default=NULL,
              help="path to metab2mesh fisher table", metavar="character"),
  make_option(c("-o", "--p_out"), type="character", default=NULL,
              help="path to out file", metavar="character")
);

opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser);

# Prepare files :
path_metab2mesh <- opt$p_metab2mesh
path_out <- opt$p_out


# Add columns names and adjusted p.value
metab2mesh <- read.table(path_metab2mesh, sep = ",", stringsAsFactors = FALSE)
colnames(metab2mesh) <- c("CHEBI", "MESH", "COOC", "TOTAL_PMID_CHEBI", "TOTAL_PMID_MESH", "TOTAL_PMID", "p.value", "odds_ratio", "Fold_change", "Chisq_stat")
metab2mesh$p.adj <- p.adjust(metab2mesh$p.value, method = "BH")

write.table(metab2mesh, file = path_out, sep = ",", row.names = FALSE, col.names = TRUE)
