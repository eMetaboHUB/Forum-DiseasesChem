library(optparse)
library(bigstatsr)
library(parallel)
library(foreach)


option_list <- list(
  make_option(c("-f", "--file"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-t", "--threshold"), type="numeric", default=NULL,
              help="p-value threshold", metavar="numeric"),
  make_option(c("-a", "--alphaCI"), type="numeric", default=NULL,
              help="alpha for Confidence interval", metavar="numeric"),
  make_option(c("-c", "--chunksize"), type="numeric", default=NULL,
              help="chunk size while reading", metavar="numeric"),
  make_option(c("-p", "--parallel"), type="numeric", default=NULL,
              help="Number of cores allowed for parallelisation", metavar="numeric")
);

parallel_on_chunck <- function(dataChunk, n_cores, pv_th, alpha_CI){

  
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
    # On détermine si le seuil a été atteint dans l'intervalle. Sachant qu'on passe le seuil de p-value, on a juste a testé la borne supérieure de l'IC: 
    th_reached <- (res$p_value[1] > pv_th)
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
      Entropy <- ifelse(p_from_closest_point == 1, yes = 0, no = -(p_from_closest_point*log2(p_from_closest_point)) - ((1 - p_from_closest_point) * log2((1 - p_from_closest_point))))
      return(c(TRUE, point_closest_to_th, (COOC - (point_closest_to_th - 1)) , p_from_closest_point, Entropy))
    }
  }
  
  n <- nrow(dataChunk)
  cl <- parallel::makeCluster(n_cores, outfile = "")
  doParallel::registerDoParallel(cl)
  results <- FBM(n, 5)
  print("Computing ....")
  tmp <- foreach(i = 1:n, .combine = 'c') %dopar% {
    if(dataChunk[i, ]$p.adj > pv_th){
      print(paste("At line ", i, " association was not initially significant, impossible to determine weakness features !"))
      results[i, ] <- c(FALSE, NA, NA, NA, NA)
    }
    else{
      results[i, ] <- compute_weakness_features(dataChunk[i, 3], dataChunk[i, 4], dataChunk[i, 5], dataChunk[i, 6], pv_th, alpha_CI)
    }
  }
  # On stoppe les processus en parallèle
  parallel::stopCluster(cl)
  return(results[])
}
    
opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser);

print("Starting computing weakness")

# Prepare files :
path_in <- opt$file
pv_th <- opt$threshold
alpha_CI <- opt$alphaCI
n_cores <- opt$parallel
chunksize <- opt$chunksize

splited_path <- strsplit(path_in, "\\.")
path_out <- paste0(splited_path[[1]][1], "_weakness.csv")

# Get total number of lines. Remove 1 for header:
nlines <- R.utils::countLines(path_in)[1] - 1
print(paste("There are", nlines, "associations to compute"))
print(paste("Use parallelisation with", n_cores, "cores"))


con <- file(description=path_in, open="r")
reached_chunck <- 0
print(paste("Treating chunk", reached_chunck))

# First time is read here to extract reader: 
dataChunk <- read.table(con, nrows = chunksize, skip = 0, header = TRUE, fill = TRUE, sep = ",")
# On récupère le hearder pour les prochaines itérations car no aura besoinn de récupérer l'attribut p.adj
headers <- colnames(dataChunk)

# Computation
results <- parallel_on_chunck(dataChunk, n_cores, pv_th, alpha_CI)

# On cbind par rapport au chunk
dataChunk <- cbind(dataChunk, results)
colnames(dataChunk)[seq.int(to = length(colnames(dataChunk)), length.out = 5)] <- c("Is_Threshold_reached", "COOC_closest_to_threshold", "Nb_articles_to_removed_assos", "proba_of_sucess", "Entropy")

# On écrit avec les headers
out <- file(description=path_out, open="w")
write.table(dataChunk, out, sep = ',', row.names = FALSE, col.names = TRUE, append = FALSE)
close(out)

# On incrémente le chunk
reached_chunck <- reached_chunck + chunksize

# Do in loop
while(reached_chunck < nlines){
  print(paste("Treating chunk", reached_chunck))
  # read chunk
  dataChunk <- read.table(con, nrows = chunksize, skip = 0, header = FALSE, fill = TRUE, sep = ",")
  # On réinjecte les headers pour pouvoir mappé la colonnes p.adj
  colnames(dataChunk) <- headers
  # Computation
  results <- parallel_on_chunck(dataChunk, n_cores, pv_th, alpha_CI)
  dataChunk <- cbind(dataChunk, results)
  out <- file(description=path_out, open="a")
  # On écrit en append SANS les headers
  write.table(dataChunk, out, sep = ',', row.names = FALSE, col.names = FALSE, append = TRUE)
  close(out)
  # On incrémente le chunk
  reached_chunck <- reached_chunck + chunksize
  
}
close(con)
print("End !")