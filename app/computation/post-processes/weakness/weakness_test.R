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
              help="Number of cores allowed for parallelisation", metavar="numeric"),
  make_option(c("-o", "--p_out"), type="character", default=NULL,
              help="path to out file", metavar="character")
);

parallel_on_chunck <- function(dataChunk, n_cores, pv_th, alpha_CI){

  
  compute_weakness_features <- function(COOC, TOTAL_PMID_CID, TOTAL_PMID_MESH, TOTAL_PMID, pv_th, alpha_CI){
    # On calcule l'intervalle de Jeffreys en utilisant une Beta avec un prio non-informatif, comme dans la doc
    CI <- c(qbeta(p = alpha_CI/2, shape1 = COOC + 0.5, shape2 = (TOTAL_PMID_CID - COOC) + 0.5), qbeta(p = 1 - (alpha_CI/2), shape1 = COOC + 0.5, shape2 = (TOTAL_PMID_CID - COOC) + 0.5))
    min <- round(CI[1] * TOTAL_PMID_CID)
    max <- round(CI[2] * TOTAL_PMID_CID)
    # On test si le seuil est franchi à la borne minimale
    min_p <- phyper(q = min - 1, m = TOTAL_PMID_MESH - (COOC - min), n = (TOTAL_PMID - TOTAL_PMID_MESH), k = TOTAL_PMID_CID - (COOC - min), lower.tail = FALSE)
    # Si la p-value à la borne est toujours significative, alors on ne cherche pas à calculer car cela veut dire que le test passe pour tous les scénarios
    if(min_p <= pv_th){
        return(NA)
    }
    # Sinon on fait le test
    predicted_proba <- vector(mode = "numeric", length = (COOC - min + 1))
    # On calcule entre la borne minimale et la coocurence observée. L'expression n'est pas très explicite, mais le but est d'exprimé en fonction de i pour remplir le vecteur.
    for(i in 1:(length(predicted_proba))){
      predicted_proba[i] <- phyper(q = min + i - 2, m = TOTAL_PMID_MESH - (COOC - (min + i - 1)), n = (TOTAL_PMID - TOTAL_PMID_MESH), k = TOTAL_PMID_CID - (COOC - (min + i - 1)), lower.tail = FALSE)
    }
    res <- data.frame(coocurence = seq(min, COOC), p_value = predicted_proba)
    test_closest <- res[res$p_value <= pv_th, ]
    point_closest_to_th <- test_closest[1, ]$coocurence
    return(COOC - point_closest_to_th + 1)
  }
    
  n <- nrow(dataChunk)
  cl <- parallel::makeCluster(n_cores, outfile = "")
  doParallel::registerDoParallel(cl)
  results <- FBM(n, 1)
  print("Computing ....")
  tmp <- foreach(i = 1:n, .combine = 'c') %dopar% {
    if(dataChunk[i, ]$q.value > pv_th){
      results[i, ] <- c(NA)
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

path_out <- opt$p_out

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
colnames(dataChunk)[length(names(dataChunk))] <- c("n_weak")

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