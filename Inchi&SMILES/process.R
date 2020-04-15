library(tidyverse)
# For smiles :
smiles <- read.table("all_couples_specie_specieName_SMILES_Human1.tsv", sep = '\t', header = TRUE, stringsAsFactors = FALSE)
non_unique_smiles <- smiles %>% group_by(selected_smiles) %>% mutate(n = length(unique(spe_name))) %>% distinct(selected_smiles, .keep_all=TRUE) %>% filter(n > 1)
write.table(x = smiles[smiles$selected_smiles %in% non_unique_smiles$selected_smiles, ], file = "non_unique_smiles.tsv", sep = '\t', row.names = FALSE)
# For inchi :
inchi <- read.table("all_couples_specie_specieName_inchi_Human1.tsv", sep = '\t', header = TRUE, stringsAsFactors = FALSE)
non_unique_inchi <- inchi %>% group_by(selected_inchi) %>% mutate(n = length(unique(spe_name))) %>% distinct(selected_inchi, .keep_all=TRUE) %>% filter(n > 1)
write.table(x = inchi[inchi$selected_inchi %in% non_unique_inchi$selected_inchi, ], file = "non_unique_inchi.tsv", sep = '\t', row.names = FALSE)