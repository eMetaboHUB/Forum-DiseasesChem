library(optparse)
library(dplyr)

option_list <- list(
  make_option(c("-f", "--file"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-t", "--threshold"), type="numeric", default=NULL,
              help="p-value threshold", metavar="numeric"),
  make_option(c("-a", "--alphaCI"), type="numeric", default=NULL,
              help="alpha for Confidence interval", metavar="numeric")
);


compute_weakness_features <- function(COOC, TOTAL_PMID_CID, TOTAL_PMID_MESH, TOTAL_PMID, pv_th, alpha_CI){
  # On calcule l'intervalle de Jeffreys en utilisant une Beta avec un prio non-informatif, comme dans la doc
  CI <- c(qbeta(p = alpha_CI/2, shape1 = COOC + 0.5, shape2 = (TOTAL_PMID_CID - COOC) + 0.5), qbeta(p = 1 - (alpha_CI/2), shape1 = COOC + 0.5, shape2 = (TOTAL_PMID_CID - COOC) + 0.5))
  min <- round(CI[1] * TOTAL_PMID_CID)
  max <- round(CI[2] * TOTAL_PMID_CID)
  predicted_proba <- vector(mode = "numeric", length = (max - min + 1))
  # On calcule toute les valeurs dand l'intervalle
  for(i in 1:(length(predicted_proba))){
    predicted_proba[i] <- phyper(q = min + i - 2, m = TOTAL_PMID_MESH - (COOC - (min + i - 1)), n = (TOTAL_PMID - TOTAL_PMID_MESH), k = TOTAL_PMID_CID - (COOC - (min + i - 1)), lower.tail = FALSE)
  }
  res <- data.frame(coocurence = seq(min, max), p_value = predicted_proba)
  # On détermine si le seuil a été atteint dans l'intervalle: 
  th_reached <- (res$p_value[1] > pv_th) & (pv_th > last(res$p_value))
  if(! th_reached){
    # Le seuil n'a pas été atteint, pas besoin de chercher le point le plus proche
    return(c(FALSE, NA, NA, NA, NA))
  }
  else{
    # On cherche le point le plus proche du seuil mais qui reste significatif, nous donnant l'effectif limite pour inférer une association au seuil imposés
    test_closest <- res[res$p_value <= pv_th, ]
    point_closest_to_th <- test_closest[1, ]$coocurence
    # On détermine la proba minimale associé à cet effectif en prenant en compte l'approximation
    approx <- (point_closest_to_th + (point_closest_to_th - 1))/2
    p_from_closest_point <- pbeta(approx/TOTAL_PMID_CID, shape1 = COOC + 0.5, shape2 = (TOTAL_PMID_CID - COOC) + 0.5, lower.tail = FALSE)
    # Suivant l'intervalle choisit l'approximation peut renvoyer 1 (On cherche P(p > plim))
    Entropy <- if_else(p_from_closest_point == 1, true = 0, false = -(p_from_closest_point*log2(p_from_closest_point)) - ((1 - p_from_closest_point) * log2((1 - p_from_closest_point))))
    return(c(as.logical(TRUE), point_closest_to_th, (COOC - (point_closest_to_th - 1)) , p_from_closest_point, Entropy))
  }
}


opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser);

# Prepare files :
path_in <- opt$file
pv_th <- opt$threshold
alpha_CI <- opt$alphaCI


splited_path <- strsplit(path_in, "\\.")
path_out <- paste0(splited_path[[1]][1], "_weakness.csv")
log <- file(paste0(splited_path[[1]][1], ".log"), "w")

# Read data :
data <- read.table(path_in, header = TRUE, sep = ",", stringsAsFactors = FALSE)
# intial columns must be in this order: CID MESH  COOC  TOTAL_PMID_CID  TOTAL_PMID_MESH TOTAL_PMID
n <- nrow(data)
results <- as.data.frame(matrix(numeric(0), ncol = 5, nrow = n, dimnames = list(NULL, c("th_reached", "nb_lim", "nb_removed", "proba", "entropy"))))

for(i in 1:n){
  # Si l'association n'est pas intialement signifcative on passe car on ne s'interresse qu'au faux positifs :
  if(data[i, ]$p.adj <= pv_th){
    writeLines(paste("At line ", i, " association was not initially significant, impossible to determine weakness features !"), log)
    results[i, ] <- c(FALSE, NA, NA, NA, NA)
  }
  else{
    results[i, ] <- compute_weakness_features(data[i, 3], data[i, 4], data[i, 5], data[i, 6], pv_th, alpha_CI)
  }
}
close(log)
data <- cbind(data, results)
write.table(data, path_out, sep = ',', row.names = FALSE, col.names = FALSE)