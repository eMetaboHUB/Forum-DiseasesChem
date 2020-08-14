# Biblio
### Rebholz-Schuhmann, D., Oellrich, A., Hoehndorf, R., 2012. Text-mining solutions for biomedical research: enabling integrative biology. Nat Rev Genet 13, 829–839. https://doi.org/10.1038/nrg3337

- Notre approche rentre dans une ddes catégories qu'ils décrivent: Information extraction
The process of automatically assessing documents, data or knowledge bases to extract statements that are likely to be true given the available information. Information extraction can be based on defined patterns, machine-learning techniques, statistical analyses or automated reasoning. 
- Il présentent les étapes fondamentale d'une solution text - mining:
- 1) Retrieving relevant documents:
    - Dans l'article ils présentent ça comme retrouver par exemple retrouver tout les articles qui mentionnent une maladie. Il présentait par exemple les search engine de Pubmed ou GoPubMed qui se basait sur les Go-terms, les MeSH pour retrouver les publications associés
    - Nous à la maière de GoPubMed, on a que grâce à l'annotation sémantique des publication par les MeSH, on peut rerouver les publis associé à une maladie par exemple et d'un point de vue sémantique, même à un groupe de maladie. L'approche est entièrement réalisable avec les gènes ou les protéines grâce à Elink
- 2) Entity recognition & normalization: C'est plutôt pour du text mining car c'est vrai que nous grâce à l'annotation en MeSH on a pas ce problème car nos données sont déjà labélisé. Pour les approches de text mining comme PolySearch ou autre, les étapes d'entity recongnition & normalization sont complexes ! Pour un mot, il fait identifier s'il s'ait par exempe dèn gène, de quel gène il s'agit et ensuite de le relier en une entité normalisé dans une base de données type NCBI-Gene ou Unirpot par exemple. Mais dû aux problématique de tokenisation (si il y a des caractère spéciaux, ou si le nom du gène est par exemple en 2 mots), de synonymes et des ambiguités (entity desambiguation, ex: Mice = l'organisme et MicE = nom d'une proteine) cet étape est une grosse source d'erreur. Ex: le mot "has" peut à la fois être interpréter comme le verbe, mais aussi comme le nom de la protéine "hyaluronan synthase" ou de son gène. Aussi, les MeSH étant annotés manuellement par des curateurs, cela diminue les ambiguité sur les annotations des articles
- 3) Identificatin of relations between entities:
    - Méthode la plus simple: cooc dans les phrases
    - En utilisant des réseau d'intéraction
    - Extraction de statements particuliers -  pattern based approaches or machine learning
- 4) Hypothesis generation: 
    - C'est pas le but de notre base
- 5) Driving integrative research (**Ce paragrapge du papier décrit complètement notre problématique et on y a répondu !!**): 
    - Contruire une base de données intégratives:
    - Openly accessible
    - Interoperabilité des données
    - Lier la litterature à des ressources sémantiques liée à d'autres base de données (**Technologies du Web Semantic** -> information in a computer-readable format)
    - Extraire et intégrer des liens ("assertions") entre des concepts extrait de la littérature
    - Les implications que ça peut avoir::
        - La distinction entre ressource extraite de la litteratures (les liens que l'on aura inféré) et ceux décrits dans des bases de données sera plus flou
- 6) Exploiting formal knowledge with reasoning techniques:
    - Les résultats ou données sont représenté de manière formalisé par des concepts décrits dans des ontologies
    - Extension des analysesn raisonnement automatique (pas encore)
    - Un outil pour formuler de nouvelles hypothèse


### PubMed and beyond: a survey of web tools for searching biomedical literature

Dasn cet artciles ils présentent tout les alternatives à PubMed comme search-engine pour la literature scientifique
Ils définissent plusieurs classes d'outils dont 2 qui colle pas mal avec ce que l'on a nous grâce aux MeSH: *Clustering results into topics* et *Enriching results with semantics and visualization*
- *Clustering results into topics*: plusieurs outils ont permis d'offrir une clusterisation des résultats d'une requête PubMed en fonction des MeSH, des termes ULMS, de Go-termes, etc ... qui sont annotés à ces publications. Ils peuvent également utilisé la date de publication, le nom des auteurs, le journal, etc ...
On peut citer; McSyBu, Anne O-Tate, GoPubMed, ClusterMed et XplorMed
- *Enriching results with semantics and visualization*: Offre la possibilité de faire des requêtes sémantiques de tel sorte que les articles retournés en résultat soit associés sémantiquement aux termes de la requête. In peut citer MedEvi, MEDIE, CiteXplore ...
Malheureusement, tout ces outils sont aujourd'hui indisponible ....
Deplus le moteur de recherche de PubMed est aujourd'hui suffisament performant grâce à tout ces module de recherche avancé avec les MeSH etc ...


### The role of ontologies in biological and biomedical research: a functional perspective
Les quatres propriété principales des ontologies :
- **provision of standard identifiers for classes and relations that represent the phenomena within a domain:**
    The use of standard identifiers for classes and relations in ontologies is what enables data integration across
multiple databases because the same identifiers can be used across multiple, disconnected databases, files, or
web sites.

- **provision of a vocabulary for a domain:**
    Through labels associated with classes and relations, ontologies provide a domain vocabulary that can be exploited for applications ranging from natural language processing, creation of user interfaces, etc.

- **provision of metadata that describes the intended meaning of the classes and relations in ontologies:**
    Textual definitions, descriptions, examples and further metadata associated with classes in ontologies are what enable domain experts to understand the precise meaning of class in the ontology. The definitions and related metadata should allow consistent understanding of the meaning of classes in ontologies.

- **provision of machine-readable axioms and definitions that enable computational access to some aspects of the meaning of classes and relations:**
    Formal definitions and axioms enable automated and computational access to (some parts of) the meaning of a class or relation

Pourquoi les utiliser :
 - Intégration de données en utilisant des classes ou des concepts définit dans des ontologies permet de les rendre interopérables, car le même id pourra lier à plusieurs database + apporte de l'info sur les entités (métadata, syonymes, exemples, etc ..;)
Comme ils le montre, une des approches les plus utilisé des ontologie est par exemplele Gene Set Enrichment Analysis avec les GO-termsqui ombine la structure de l'ontologie (axions relationnels etdéfinitions) avec de l'intégration de données afin  de fournir une interprétation statistique de la différence entre 2 conditions par exemples dans un contexte de connaissance décrites par l'ontologie
-> C'est exactement ce que nous faisons avec MeSH, Chebi et tout !



    ### Thesaurus, Txanonomy and Ontology :
    Summarization: A thesaurus is expressive enough to improve most enterprise applications significantly, but it is not too complex to create and maintain it in a sustainable way. All three are types of controlled vocabularies, which contain terms with their synonyms and alternative spellings combined to form concepts. A taxonomy is the simplest variant as it contains only terms that are organized into a hierarchical structure. A thesaurus adds non-hierarchical relationships between concepts and other properties to each concept. Ontologies are on the heavy end of the spectrum. Ontologies can express axioms and restrictions. This maximum in expressivity has the drawback that ontologies are hard to create, maintain and handle. We believe thesauri hit the sweet spot between expressive semantics and ease of handling, and designed PoolParty to be a tool that makes creating and maintaining them straightforward.

    Une différence majeure entre Thesaurus et ntology est surtout le type d'assertions que l'on va pouvoir en faire. Dans le as des Thesarus, on va ête limiter à des raisonnemenbt relativement simples et type: *broader term* ou *narrower term* par exemple qui représente un raisonnement de généralisation ou de spécialisation. Chose qui nous ai suffisante pour faire nos analyses. 
    Avec les ontologies on peut difinir des raisonnement plus poussé: Par exemple On peut définir les personnel hospitaliers comme une personnage qui a un travail et dont ce travail est soit médecin, infirmier, aide soignant, etc .. 
    Aussi si je définis que tout les genes qui travailles dans des hopitaux sont soit médecin, infirmier, aide soignant, alors je peux inférer que tout les gens qui travailles dans des hopitaux sont du personnel hospitalier, c'est plus poussé !