# Exemples

- Comparaison des résultats avec metab2mesh (liens simples)
  - CID - MESH test case Cyclic AMP
  - MESH - CID test cas Phenylketonurias 
- Exemple avec Propagation:
  - Résultat associations gagnées : 
    - Test case Oxyfedrine
    - Test case ChEBI + Phenylketonuria
  - Résultats associatiosn perdues :
    - Test Case Eau + Eukaryote
  - Résultat Analyse globale :
    - Imidocarb dipropionate


# Examples

Metab2MeSh [1] was a web server dedicated to the annotation of compounds with biomedical concepts defined in the MeSH Thesaurus, largely appreciated and used in the community [2-6]. Unfortunately, this tool is no longer available since 2019, impacting tools using it as a data provider or to corroborate other results and hypotheses. Metab2MeSHBis was created to fill this gap, but, using linked data, it also improve several aspects of the original tool, mainly on provided annotations, data accessibility and manipulation. In order to validate our approache, it is critical to ensure that association made by metab2mesh are also conserved in our tool. We used the same test cases as in the Metab2MeSH article: diseases related to Cyclic AMP and compouds related to Phenylketonuria by literature evidences (data were respectively retrieve from the supplementary Figures 2 and 3 of the original article).

## Diseases related to Cyclic AMP

In the original article, authors show that diseases associated to Cyclic AMP are mostly cancers, such as neuroblastoma or Glioma, but none MeSH terms representing a cancer family that would gather all these diseases is found. 
[Supp-Table X] compares results from Metab2MeSH and our tool, replicating their approache, for the Top 13 of diseases associated to Cyclic AMP. All diseases associations are conserved, with similar statistics of p-value, Fold-Change and Chisq-Stat, but as the corpus of each assoication grow each year, they relies today on more articles. 
The use of semantic relations between MeSH to propagate literature through the MeSH Thesaurus allow to reveal new associations that was not explicitely associated to the compound. Table [Supp-Table Y] compares the Top 20 enriched diseases with and without using propagation. Most of associations provided using propagation are news and involves MeSH which represent diseases family, ancestors in the MeSH tree of terms which were already associated without propagation: *Neoplasms, Neuroepithelial* is the ancestor of *Glioma* and *Neuroblastoma*. But, despite the adding of the new associations, all previously enriched MeSH are also retrieve highlly significant in the Top 40. 


## Compounds related to Phenylketonuria

The approach is reversible and allow also to retrieve compounds associated to a MeSH descriptor such as a disease. In the second test case, we compare results for compounds associated to the Phenylketonuria [Supp-Table Z], a metabolic disease induce by a defect of the phenylalanine hydroxylase, and show again how the addition of semantic level can enrich results. Some compounds (10/25) associated to this disease in Metab2MeSH results are not present in our compound list (in grey), as there are no or a few publications associated to these compounds in all our knowledge base. Differences in the approach used to link litterature to compounds and changes in the PubChem database since 2012, could explain these results. For compounds newly associated to phenylketonuria in our list, they are for the most pterin derivates. In both approaches enriched compounds like *Phenylalanine*, *Tyrosine*, *Tetrahydrobiopterins* or *Sapropterins* are knwon to be associated to Phenylketonuria [7]. The table [ZZ] describes results obtain using the ChEBI ontology to provide a semantics descriptions of molecules. This representation allow to highligh molecule families associated to the Phenylketonuria rather than simple compounds, like family of *aromatic amino acids* or *pterins* whose members are over-represented in compounds initialy linked to the disease.



L'utilisation d'une couche sémantique pour décrire les composé au travers de l'ontology ChEBI fait ressortir des familles de molécules 


la table ZZ décrits les résultats obtenus en utilisant l'ontologie ChEBI pour apporter une description sémantique des composés.
Cette représentation des molécules permet d'identifier des familles de molécules associé à la phenylketonuria comme les acides aminés aromatiques ou les pterines dont les membres sont sur-représentés parmis les composés initialement associés à la maladie. 


[Ensuite il y aurait une seconde table (j'ai fais un schéma) qui montrerait les résultats de notre outil sur le test case de l'AMP cyclic avant et après propagation (un Top25 par ex) où l'on verrait que de nouveau termes chapeau sont apparus --> Ne pas montrer directement que cesont des ancêtres ou quoi des termes enfants, ça sera plus dans la discussion ça, ici ce sont les RÉSULTATS !!] -> Ces termes nous permettent de retrouver les conclusions de l'article original.


Sans propagation ces associations sont pauvrement associés à l'AMP Cyclic et s'appuie sur un nombre très réduit d'articles.

- Pas sur que ce soit réellement utile ça car on aura pas forcément les données de compatges, juste les rangs ou jsp



## Plutôt dans la discussion 

[In fact, thoses type of MeSH (like disease families or taxons) are poorly used to index publications and represent intermediary nodes which ensures consistency in the hierarchical structure of the MeSH Tree, but because of this position, carry a lot of semantic information. Thus, propagate the litterature through the hierarchical structure of the MeSH tree allows to reveal these associations. -> Est-ce que ça ferait pas plus parti de la discussion ??]

When propaging associations to MeSH ancestors through the Thesaurus, corpus of MeSH which are not leaf can increase if some of their child terms are also associated to the compound. In Table X, corpus of *Neuroblastoma* does not change even if it has two child-terms (*Esthesioneuroblastoma* and *Ganglioneuroblastoma*), because they are never associated to Cyclic AMP in our Knowledge base. *Glioma* has 10 child-terms and his corpus size increase by more than 44% using the propagation, as his child-terms are also associated to Cyclic AMP in our Knowledge base. *Cystic Fibrosis* being a leaf in the MeSH Thesaurus, his corpus is not affected by the propagation. Significant ssociations made without propagation are conserved and new associations appears








[1] Sartor, M.A., Ade, A., Wright, Z., States, D., Omenn, G.S., Athey, B., Karnovsky, A., 2012. Metab2MeSH: annotating compounds with medical subject headings. Bioinformatics 28, 1408–1410. https://doi.org/10.1093/bioinformatics/bts156
[2] Fukushima, A., Kusano, M., 2013. Recent Progress in the Development of Metabolome Databases for Plant Systems Biology. Front. Plant Sci. 4. https://doi.org/10.3389/fpls.2013.00073
[3] Guney, E., Menche, J., Vidal, M., Barábasi, A.-L., 2016. Network-based in silico drug efficacy screening. Nat Commun 7, 10331. https://doi.org/10.1038/ncomms10331
[4] Sas, K.M., Karnovsky, A., Michailidis, G., Pennathur, S., 2015. Metabolomics and Diabetes: Analytical and Computational Approaches. Diabetes 64, 718–732. https://doi.org/10.2337/db14-0509
[5] Cavalcante, R.G., Patil, S., Weymouth, T.E., Bendinskas, K.G., Karnovsky, A., Sartor, M.A., 2016. ConceptMetab: exploring relationships among metabolite sets to identify links among biomedical concepts. Bioinformatics 32, 1536–1543. https://doi.org/10.1093/bioinformatics/btw016
[6] Duren, W., Weymouth, T., Hull, T., Omenn, G.S., Athey, B., Burant, C., Karnovsky, A., 2014. MetDisease—connecting metabolites to diseases via literature. Bioinformatics 30, 2239–2241. https://doi.org/10.1093/bioinformatics/btu179
[7] Blau, N., Shen, N., Carducci, C., 2014. Molecular genetics and diagnosis of phenylketonuria: state of the art. Expert Review of Molecular Diagnostics 14, 655–671. https://doi.org/10.1586/14737159.2014.923760
