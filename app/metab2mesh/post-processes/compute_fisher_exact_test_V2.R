library(optparse)
library(bigstatsr)
library(parallel)
library(foreach)

option_list <- list(
  make_option(c("-f", "--file"), type="character", default=NULL,
              help="dataset file name", metavar="character"),
  make_option(c("-c", "--chunksize"), type="numeric", default=NULL,
              help="chunk size while reading", metavar="numeric"),
  make_option(c("-p", "--parallel"), type="numeric", default=NULL,
              help="Number of cores allowed for parallelisation", metavar="numeric")
);


opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser)

# Functions


# Compute test :
parallel_on_chunck <- function(dataChunk, n_cores){
  
  # Function
  compute_tests <- function(X, Y, COOC, T_X, T_Y, TT){
    # Prepare matrix
    a <- COOC
    b <- T_X - COOC
    c <- T_Y - COOC
    d <- TT - a - b - c
    matrice <- matrix(data = c(a, b, c, d), ncol = 2, byrow = TRUE)
    # TryCatch on Fisher test :
    test <- tryCatch(
      {
        fisher.test(x = matrice, alternative = "greater")
      },
      error = function(e){
        print(paste(c(X, Y, e), collapse = " "))
        return(NULL)
      },
      warning = function(w){
        print(paste(c(X, Y, w), collapse = " "))
        return(NULL)
      }
    )
    # TryCatch on Chisq test :
    chisq <- tryCatch({
      suppressWarnings(chisq.test(matrice)$statistic)
    },
    error = function(e){
      print(paste(c(X, Y, e), collapse = " "))
      return(NULL)
    })
    # parse and write results :
    if(!is.null(test)){
      p.value <- test$p.value
      if(is.infinite(test$estimate)){
        odds_ratio <- NA
      }else{
        odds_ratio <- test$estimate
      }
      fold_change <- (a/T_X)/(T_Y/TT)
    }else{
      p.value <- odds_ratio <- fold_change <- NA
    }
    if(!is.null(chisq)){
      chisq_stat <- chisq
    }else{
      chisq_stat <- NA
    }
    return(c(p.value, odds_ratio, fold_change, chisq_stat))
  }
  
  n <- nrow(dataChunk)
  cl <- parallel::makeCluster(n_cores, outfile = "")
  doParallel::registerDoParallel(cl)
  results <- FBM(n, 4)
  print("Computing ....")
  tmp <- foreach(i = 1:n, .combine = 'c') %dopar% {
    # On calcule les stats. Attention, maintenant les log suront print, il faudrait donc rediriger la sortie vers un fichier .log au moment du lancement
    results[i, ] <- compute_tests(dataChunk[i, 1], dataChunk[i, 2], dataChunk[i, 3], dataChunk[i, 4], dataChunk[i, 5], dataChunk[i, 6])
  }
  # On stoppe les processus en parallèle
  parallel::stopCluster(cl)
  return(results[])
}



# Get parralel parameteres
n_cores <- opt$parallel
chunksize <- opt$chunksize

# Prepare files :
path_in <- opt$file
splited_path <- strsplit(path_in, "\\.")
path_out <- paste0(splited_path[[1]][1], "_results.csv")

# Get total number of lines. Remove 1 for header:
nlines <- R.utils::countLines(path_in)[1] - 1
print(paste("There are", nlines, "associations to compute"))
print(paste("Use parallelisation with", n_cores, "cores"))

# Prepare conn
con <- file(description=path_in, open="r")
reached_chunck <- 0
print(paste("Treating chunk", reached_chunck))

# First time is read here to extract reader: 
dataChunk <- read.table(con, nrows = chunksize, skip = 0, header = TRUE, fill = TRUE, sep = ",")

# Computation
results <- parallel_on_chunck(dataChunk, n_cores)

# On cbind par rapport au chunk
dataChunk <- cbind(dataChunk, results)

# On écrit une première fois les headers
colnames(dataChunk)[seq.int(to = length(colnames(dataChunk)), length.out = 4)] <- c("p.value", "odds_ratio", "fold_change", "chisq_stat")

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

  # Computation
  results <- parallel_on_chunck(dataChunk, n_cores)
  dataChunk <- cbind(dataChunk, results)
  out <- file(description=path_out, open="a")
  write.table(dataChunk, out, sep = ',', row.names = FALSE, col.names = FALSE, append = TRUE)
  close(out)
  # On incrémente le chunk
  reached_chunck <- reached_chunck + chunksize
  
}
close(con)
print("End !")

