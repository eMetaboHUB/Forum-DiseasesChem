a <- elink(uid="6036", dbFrom ="pccompound", dbTo ="mesh")
xmlParse(a$content)

# Savoir que dans a, on ne retrouve même pas le term MeSh galactose de numéri 68005690, donc ce elink est byzarre
# Premier test
elink(uid="68005690", dbFrom ="mesh", dbTo ="pubmed")

new_ids <- c("67040642",
             "68003287",
             "68011134",
             "68002241",
             "68064907",
             "68020313",
             "68020228",
             "68020164",
             "68003287")

# Second test 

elink(uid=new_ids, dbFrom ="mesh", dbTo ="pubmed")

# Ce qui marche le mieux c'est ça !:)

a <- esearch(term = "Galactose[Mesh Terms]", db = "pubmed", retmax = 25000)
a

# Comment on pourrait faire ?
# Ex : 
# On récupère le nom du meSH term, toujours le premier fils de DS_MeshTerms, ici : Galactose
esummary(uid = "68005690", db = "mesh")
# On le paste à coté de [MeSh term] et c'est bon : 
esearch(term = "Galactose[Mesh Terms]", db = "pubmed", retmax = 25000)
# Le problème c'est que tous ne sont pas des Mesh termes ...y'a des sub concept et tout...
# Car par exemple si on met le Kdo2 -lipid A suivit le [Mesh], rien ne sort car c'est un supplementary concept et non un descripteur. Et si sont parent qui le représente, c'est Lipopolysachariide et là on a plus de 80000 PMID ...#
# Donc il faut vraiemenbt que la requête soit spé du type de MeSH. comme lorsque l'on lance avec "Add to search builder"

# Mais avec le uid et la requête MeSH, on peut récupérer le  DS_MeSHUI qui est le MeSH Unique ID.
# Et avec ce MeSH unique ID, on peut petre être faire plus et au moins savoir je pense s'il d'agit d'un supplementary concept ou non
# En effet, Grâce au MeSH unique ID, en mapppant sur le RDF MeSH pour savoir su'il est du type MeSH SupplementaryConceptRecord et de la on pourra certaienement construire la requête


