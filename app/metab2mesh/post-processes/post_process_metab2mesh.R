library(optparse)
library(tidyverse)
option_list <- list(
  make_option(c("-i", "--p_metab2mesh"), type="character", default=NULL,
              help="path to metab2mesh fisher table", metavar="character"),
  make_option(c("-x", "--Xname"), type="character", default=NULL,
              help="Name of the first variable used in the metab2mesh (ex: CID)", metavar="character"),
  make_option(c("-y", "--Yname"), type="character", default=NULL,
              help="Name of the second variable used in the metab2mesh (ex: MESH)", metavar="character"),
  make_option(c("-u", "--Uname"), type="character", default=NULL,
              help="Name of the individual variable used in the metab2mesh (ex: PMID)", metavar="character"),
  make_option(c("-o", "--p_out"), type="character", default=NULL,
              help="path to out file", metavar="character")
);


opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser);

# Prepare files :
path_metab2mesh <- opt$p_metab2mesh
X_name <- opt$Xname
Y_name <- opt$Yname
U_name <- opt$Uname
path_out <- opt$p_out

# Add columns names and adjusted p.value
metab2mesh <- read.table(path_metab2mesh, sep = ",", stringsAsFactors = FALSE, header = TRUE) #  J'ai rajouté Header = True, car avec la nouvelle version du calcul en parallèle, on a direct le header
colnames(metab2mesh) <- c(X_name, Y_name, "COOC", paste0("TOTAL_", U_name, "_", X_name), paste0("TOTAL_", U_name, "_", Y_name), paste0("TOTAL_", U_name), "p.value", "odds_ratio", "Fold_change", "Chisq_stat")
metab2mesh$p.adj <- p.adjust(metab2mesh$p.value, method = "BH")


write.table(metab2mesh, file = path_out, sep = ",", row.names = FALSE, col.names = TRUE)
