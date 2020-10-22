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

metab2mesh <- read_csv(path_metab2mesh, col_names = TRUE, cols(
  col_character(),
  col_character(),
  col_double(),
  col_double(),
  col_double(),
  col_double(),
  col_double(),
  col_double(),
  col_double(),
  col_double()
))

metab2mesh$q.value <- p.adjust(metab2mesh$p.value, method = "BH")

write.table(metab2mesh, file = path_out, sep = ",", row.names = FALSE, col.names = TRUE)
