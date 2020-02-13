
library(XML)
library(tidyverse)
fromEutils <- xmlParse(file = "data/test_data_Galactose/From_Eutils/galactose_test.xml")


from_Eutils_link_list <- list()

for(sub in getNodeSet(fromEutils, "/eLinkResult/LinkSet/LinkSetDb")){
  print(unlist(xmlValue(getNodeSet(sub, "./LinkName"))))
  print(length(unlist(xmlValue(getNodeSet(sub, "./Link/Id")))))
  from_Eutils_link_list[[unlist(xmlValue(getNodeSet(sub, "./LinkName")))]] <- unlist(xmlValue(getNodeSet(sub, "./Link/Id")))
}

union_from_E_utils <- Reduce(union, from_Eutils_link_list)


fromPubChemMeSH <- read.table("data/test_data_Galactose/FromPubChem/pubmed_result.txt", header = FALSE)$V1 %>% as.character()
fromPubChemPublisher <- read.csv("data/test_data_Galactose/FromPubChem/CID_6036_springernature.csv", header = TRUE, sep = ',', stringsAsFactors = FALSE) 
fromPubChemPublisher <- fromPubChemPublisher$pmid[!is.na(fromPubChemPublisher$pmid)] %>% as.character()

fromPubChemDepositor <- read.csv("data/test_data_Galactose/FromPubChem/CID_6036_depositor_provided.csv", header = TRUE, sep = ',', stringsAsFactors = FALSE) 
fromPubChemDepositor <- fromPubChemDepositor$pmid[!is.na(fromPubChemDepositor$pmid)] %>% as.character()

union_from_PubChem <- Reduce(union, list(fromPubChemMeSH, fromPubChemPublisher, fromPubChemDepositor))
