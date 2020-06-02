library(optparse)
option_list <- list(
  make_option(c("-f", "--file"), type="character", default=NULL,
              help="dataset file name", metavar="character")
);

opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser);

# Prepare files :
path_in <- opt$file
splited_path <- strsplit(path_in, "\\.")
path_out <- paste0(splited_path[[1]][1], "_results.csv")
log <- file(paste0(splited_path[[1]][1], ".log"), "w")

# Read data :
data <- read.table(path_in, header = TRUE, sep = ",", stringsAsFactors = FALSE)

# Initialyze vectors :
n <- nrow(data)
p.value <- vector(mode = "numeric", length = n)
odds_ratio <- vector(mode = "numeric", length = n)
fold_change <- vector(mode = "numeric", length = n)
chisq_stat <- vector(mode = "numeric", length = n)

# Compute test :
for( i in 1:n){
  # Prepare matrix
  a <- data[i, ]$COOC
  b <- data[i, ]$TOTAL_PMID_CID - data[i, ]$COOC
  c <- data[i, ]$TOTAL_PMID_MESH - data[i, ]$COOC
  d <- data[i, ]$TOTAL_PMID - a - b - c
  matrice <- matrix(data = c(a, b, c, d), ncol = 2, byrow = TRUE)
  # TryCatch on Fisher test :
  test <- tryCatch(
    {
      fisher.test(x = matrice, alternative = "two.sided")
    },
    error = function(e){
      writeLines(paste0(c(data[i, ]$CID, data[i, ]$MESH, e), collapse = "\t"), log)
      return(NULL)
    },
    warning = function(w){
      writeLines(paste(c(data[i, ]$CID, data[i, ]$MESH, w), collapse = "\t"), log)
      return(NULL)
    }
  )
  # TryCatch on Chisq test :
  chisq <- tryCatch({
    suppressWarnings(chisq.test(matrice)$statistic)
  },
  error = function(e){
    writeLines(paste0(c(data[i, ]$CID, data[i, ]$MESH, e), collapse = "\t"), log)
    return(NULL)
  })
  # parse and write results :
  if(!is.null(test)){
      p.value[i] <- test$p.value
      if(is.infinite(test$estimate)){
          odds_ratio[i] <- NA
      }else{
          odds_ratio[i] <- test$estimate
      }
        fold_change[i] <- (a/data[i, ]$TOTAL_PMID_CID)/(data[i, ]$TOTAL_PMID_MESH/data[i, ]$TOTAL_PMID)
  }else{
      p.value[i] <- odds_ratio[i] <- fold_change[i] <- NA
  }
  if(!is.null(chisq)){
      chisq_stat[i] <- chisq
  }else{
      chisq_stat[i] <- NA
  }
}
# Append results
data$p.value <- p.value
data$odds_ratio <- odds_ratio
data$fold_change <- fold_change
data$chisq_stat <- chisq_stat

write.table(data, path_out, sep = ',', row.names = FALSE, col.names = FALSE)
close(log)






