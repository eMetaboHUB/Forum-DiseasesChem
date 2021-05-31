library(optparse)
library(tidyverse)


# Rscript app/computation/Importance_Score.R --MeSH_context="/path/to/mesh/context" --MeSH_corpora="path/to/mesh/corpora" --cooc=COOC --Chem_name="Cpd Name" --MeSH_name="MeSH Name" --Collection_size=N --Chem_MeSH_ID="ChemID" --n_top=20 --path_out="/path/out"

option_list <- list(
  make_option(c("--MeSH_context"), type="character", default=NULL,
              help="Input MeSH context file from co_annotated_MeSH.py", metavar="character"),
  make_option(c("--MeSH_corpora"), type="character", default=NULL,
              help="Input file containing copora size associated to each MeSH descriptor (See on GitHub for the lasted release file)", metavar="character"),
  make_option(c("--cooc"), type="numeric", default=NULL,
              help="The observed co-occurence between the comôund and the MeSH ", metavar="numeric"),
  make_option(c("--Chem_name"), type="character", default=NULL,
              help="The chemical compound/class name", metavar="character"),
  make_option(c("--MeSH_name"), type="character", default=NULL,
              help="The MeSh descriptor label", metavar="character"),
  make_option(c("--Collection_size"), type="numeric", default=NULL,
              help="The total number of articles", metavar="numeric"),
  make_option(c("--Chem_MeSH_ID"), type="character", default=NA,
              help="If the compoud has also a dedicated MeSH descriptor, it is advaised to remove it from the analysis to avoid an irrelevant result.", metavar="character"),
  make_option(c("--n_top"), type="character", default=NULL,
              help="Ranked 'n.top' co-mentioned MeSH by importance score", metavar="character"),
  make_option(c("--path_out"), type="character", default=NULL,
              help="path to out dir", metavar="character")
);


compute_Importance_Score <- function(mesh_context, coocurence, N, total_pmid_mesh, mesh_chem = NA, n.top = 20){
  
  # Prepare data and compute Importance-Score
  total_pmid_mesh <- total_pmid_mesh %>% mutate(IDF = log(N/TOTAL_PMID_MESH))
  mesh_context <- mesh_context %>% mutate(TF = count/coocurence) %>% left_join(total_pmid_mesh, "MESH") %>% mutate(TF.IDF = TF * IDF)
  # If the compoud has also a dedicated MeSH descriptor, it is advaised to remove it from the analysis to avoid an irrelevant result.
  if(! is.na(mesh_chem)){
    if(mesh_chem %in% mesh_context$MESH){
      mesh_context <- mesh_context[mesh_context$MESH != mesh_chem, ]
    }
    else{
      warning("Unknow MeSH or no co-occurences for this descriptor")
    }
  }
  # Order by Importance score
  mesh_context <- mesh_context[order(mesh_context$TF.IDF, decreasing = TRUE), ]
  return(mesh_context)
}



opt_parser <- OptionParser(option_list=option_list);
opt <- parse_args(opt_parser)

# Read input data
mesh_context <- read.table(opt$MeSH_context, header = TRUE, sep = ",", stringsAsFactors = F)
total_pmid_mesh <- read.table(opt$MeSH_corpora, header = TRUE, sep = ",", stringsAsFactors = F)
cooc <- opt$cooc
Chem_name <- opt$Chem_name
MeSH_name <- opt$MeSH_name
N <- opt$Collection_size
mesh_chem <- opt$Chem_MeSH_ID
n.top <- opt$n_top
path_out <- opt$path_out

if(any(mesh_context$count > cooc)){
  print("Error: Somme values co-annotated MeSH are higher than the total co-occurence, please check the provided MeSH context and cooc.")
  quit()
}

# Cretae output dir if not exists
dir.create(path = path_out, showWarnings = FALSE, recursive = T)
fig_path <- file.path(path_out, paste0(Chem_name, '_', MeSH_name, '.png'))
table_path <- file.path(path_out, paste0("Importance_Score_", Chem_name, '_', MeSH_name, '.csv'))

IS <- compute_Importance_Score(mesh_context, cooc, N, total_pmid_mesh, mesh_chem, n.top)



# Create Figure
  ggplot(IS[1:n.top, ], aes(x = reorder(label, TF.IDF), y = TF.IDF)) +
  geom_col() +
  labs(x = NULL, y = "Importance score") + 
  coord_flip() + 
  theme_classic() + 
  # ylim(c(0,10)) + 
  ggtitle(paste("Top", n.top, "\n", Chem_name, "-", MeSH_name)) +
  theme(text = element_text(size=20), title = element_text(size=8), plot.title = element_text(lineheight = 0.8)) +
  ggsave(fig_path, device = "png")

# Create table
write.table(IS, table_path, col.names = T, row.names = F, sep = ',')








