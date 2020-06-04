library(optparse)
library(tidyverse)
option_list <- list(
  make_option(c("-i", "--p_metab2mesh"), type="character", default=NULL,
              help="path to metab2mesh fisher table", metavar="character"),
  make_option(c("-c", "--p_CID_labels"), type="character", default=NULL,
              help="path to CID labels table", metavar="character"),
  make_option(c("-m", "--p_MESH_labels"), type="character", default=NULL,
              help="path to MESH labels table", metavar="character"),
  make_option(c("-u", "--p_CID_InchI"), type="character", default=NULL,
              help="path to CID InchI table", metavar="character"),
  make_option(c("-o", "--p_out"), type="character", default=NULL,
              help="path to out file", metavar="character")
);

opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser);

# Prepare files :
path_metab2mesh <- opt$p_metab2mesh
path_CID_labels <- opt$p_CID_labels
path_MESH_label <- opt$p_MESH_labels
path_CID_InchI <- opt$p_CID_InchI
path_out <- opt$p_out

# path_metab2mesh = "~/Documents/Thèse/building_database/FORUM/metdiseasedatabase/data/metab2mesh/metab2mesh_fisher/metab2mesh_fisher.csv"
# path_CID_labels = "~/Documents/Thèse/building_database/FORUM/metdiseasedatabase/data/metab2mesh/CID_LABEL/res_full.txt"
# path_MESH_label = "~/Documents/Thèse/building_database/FORUM/metdiseasedatabase/data/metab2mesh/MESH_LABEL/res_full.csv"
# path_CID_InchI = "~/Documents/Thèse/building_database/FORUM/metdiseasedatabase/data/metab2mesh/CID_INCHI/res_full.txt"

# Add columns names and adjusted p.value
metab2mesh <- read.table(path_metab2mesh, sep = ",", stringsAsFactors = FALSE)
colnames(metab2mesh) <- c("CID", "MESH", "COOC", "TOTAL_PMID_CID", "TOTAL_PMID_MESH", "TOTAL_PMID", "p.value", "odds_ratio", "Fold_change", "Chisq_stat")
metab2mesh$p.adj <- p.adjust(metab2mesh$p.value, method = "BH")

# Parse CID labels
cid_labels <- read.table(path_CID_labels, sep = "\t", stringsAsFactors = FALSE, quote = '')
colnames(cid_labels) <- c("CID", "CID_LABEL")

# Parse MeSH labels
mesh_labels <- read.table(path_MESH_label, sep = ",", stringsAsFactors = FALSE)
colnames(mesh_labels) <- c("MESH", "MESH_LABEL")

# Parse CID InchI
cid_inchi <- read.table(path_CID_InchI, sep = "\t", stringsAsFactors = FALSE, quote = '')
colnames(cid_inchi) <- c("CID", "CID_INCHI")

# Add CID labels to metab2mesh :
metab2mesh <- metab2mesh %>% left_join(cid_labels, by = "CID")
metab2mesh <- metab2mesh %>% left_join(mesh_labels, by = "MESH")
metab2mesh <- metab2mesh %>% left_join(cid_inchi, by = "CID")

write.table(metab2mesh, file = path_out, sep = ",", row.names = FALSE, col.names = TRUE)
