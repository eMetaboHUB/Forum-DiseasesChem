library(optparse)
library(readr)

option_list <- list(
  make_option(c("-i", "--p_associations"), type="character", default=NULL,
              help="path to association fisher table", metavar="character"),
  make_option(c("-o", "--p_out"), type="character", default=NULL,
              help="path to out file", metavar="character")
);


opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser);

# Prepare files :
path_associations <- opt$p_associations
path_out <- opt$p_out

associations <- read_csv(path_associations, col_names = TRUE, cols(
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

associations$q.value <- p.adjust(associations$p.value, method = "BH")

write.table(associations, file = path_out, sep = ",", row.names = FALSE, col.names = TRUE)
