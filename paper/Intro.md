I
Field domain
     
    metabo: last layer before phenotype (From genomics to phenytipe)-> mais couverture plus limité (10.3390/metabo9040076)
        -> cce qui en fait un outil puissant pour comparer les phénotype !
    
    Prédiction de BM, drug design
    Liens avec la bioinfo
    

What field Know
    Pred de biomarker à partir de exp metabo, caracterisé un c
        targeted and untergeted metabo (ref: 10.1038/nrm.2016.25 ) - pour découvrir des biomarker il faut mieux faire des approches untargeted
        

Remaining Gap: 
    Understand mechanism -> Go Beyond biomarkers
    Variabilité inter-Individus: metabo-Type -> Fragilité des signtures très contexte dependants


Need to federates data
Represent knowledge, concepts
Extrcat relevant information to provide hypotheses



La litterature scientifique contient la connaissance
    Le text mining couplé à des analyses stats peut permetttre de l'extraire à grende échelle
    -> Mais nous on utilise l'indexation

-> les ontologies permette de représenter les concepts associé
Construire des knwoledge networks


Aussi, en plus des approches de 

Pour un autre exemple de l'utilité: Gene Ontology Enrichment Improves Performances of Functional Similarity of Genes


KG:
Structure de données machine readable
Represent data woith complex relation



On a un KG avec des infos sur les molécules des liens vers la litteature et les topics annotés
-> Il fat extraire la sur-représentation (over-representation)

molecules to biomedical concepts

Some tools have already been developed to extract and propose gene or drugs candidates related to pathological phenotypes based on literature evidences and databases [KnetMiner, Sosa et al., Malas et al.; Kanza and Frey]. Literature evidences are often extracted from sentenses in PubMed articles using text-mining approches, but these articles are also manualy indexed from their main topics, by the \textit{National Library of Medecine} with MeSH descriptors (Medical Subject Headings), a controled thesaurus of biomedical concepts. A thesaurus is similar to an ontology, it is a structured vocabulary, but have a lower power of reasoning than an ontology [Kim et Beck]. PubMed articles can be linked to PubChem chemical compounds using the \textit{NBCI E-utilities} E-link function by findind related records through the both databases. Pubchem, the world largest free chemistry database, also provide knowledge graphs to semantically represent all available data associated to chemical compounds[Fu et al PubChem RDF]. All these resources can be fererate to build a FAIR knowledge graph that host the information required to proced knowledge discovery analysis in metabolomics.
