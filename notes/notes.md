## Notes du développement de la base

* 10/02/2020 : 
  Inspiration de Metab2MeSH (**Metab2MeSH: annotating compounds with medical subject headings** doi:10.1093/bioinformatics/bts156) de 2012.
  Dans leur papier, la méthodo utilisée pour faire le lien entre métabolites et termes MeSH passe par un matching des substances. A partir de PubChem, pour chaque composé, ils extraient la liste des synonymes assoociés à ce composé, qu'ils matchent ensuite par rapport à la liste des PubMed subtances. La liste Pubmed substances est construite en extrayant l'index "substances" associée à chaque abstract des article PubMed présent de la base NLM PubMed. Ils disposent donc d'une liste de substances PubMed pour lesquelles ils sont un ensemble d'article associés 
  En matchant les synonymes, ils créent ainsi des liens entre les PubChem Compound et les PubMed Substances. Ainsi, chaque PubMed Substances ayant une liste de publications associées, ils ont pour chaque composées pubmed, en fonction du matching des synonymes associées par rapport aux substances PubMed un liste d'article. A partir des articles ils extraient les meSH associés aux catégories : Diseases, Anatomy, Chemicals and Drugs, Phenomena and Processes, Organisms, Psychiatry and Psychology, Anthropology, Education, Sociology and Social Phenomena, Technology, Industry, and Agriculture. ensuite, ils font des tests d'enrichissement pour tester la signficativité de chaque associées PubChem Compounds -> MeSH term.

  Mais en 2016 est sorti un article de la base PubChem (**Literature information in PubChem: associations between PubChem records and scientific articles** DOI 10.1186/s13321-016-0142-6) :

  Dans cet article ils explique que désormais la base PubChem fournit des associaions PubChem compounds - litterature. En gros, il y a 4 types de sources d'association PuchChem CID - PMID : 
  	- **Depositor-provided corss-references :**
	  Ex:  IBM Almaden Research Center, CTD, ChemDB, etc ...
	  Ce sont des providers externes qui fournissent des associations CID - PMID, à partir d'algo de Text-Mining par e'xemple des papieres qui metionnent la molécule (IBM), ou de la base CTD par exemple qui fournit des anntotations curées et inférées. Ainsi, certaines des références sont issues de curations manuelles et d'autres d'algo de text-mining, certains ce focalise par exemple sur des domaines particuliers (ex: IEDB spécialisé en Immunologie epitope ) ce qui explique la disproportion des cross-reference fournies par les différents providers. Voila ce que j'ai pu trouver sur les annotation fournit par IBM - Almaden : "The IBM BAO strategic IP insight platform (SIIP) aggregates patent and scientific literature data and offers powerful search and analytics capabilities to comb intellectual property for new insights. It uses a computer-driven method for curating and analyzing massive amounts of patents, scientific content and molecular data, automatically extracting chemical entities from textual content as well as from images and symbols."

	- **Bioactivity data extracted from scientific articles :**
	  Certaines autres base de données telles que *ChemBL*, fournisse des informations sur des expériences dans lesquelles est impliquée la molécule. Ainsi, à cette molécule est associée un ensemble de papiers décrivant des expérieences (assay) avec donc des informations sur les méthodes de détections utilisés, les protocoles expérimentaux, les maladies associées, etc ...Il s'agit donc d'article parlant d'expérience dans lesquelles serait impliqué la molécule. *ChemBL* permet également d'enrichir la table BioAssay de pubChem. *IUPHAR* et *BPS* fournissent des références bibliographique sur l'activité des ligand sur des cibles thérapeutique. *PDBBind* litterature associées aux interaction Proteine (ou complexe Proteiques) - Ligand. *BindingDB* fournit des références sur l'affinité des liaisons entre des ligand et des proteines considérés comme des cibles thérapeutiques. *GLIDA* founie des informations sur les intéraction entre ligand et GPCR (récepteurs couplés à des protéines G). Enfin, certaines associations sont diretectment rensignés par les auteurs en indiquant leur publication dans la catégorie BioAssay de PubChem.       
	- **Chemical information provided by journal publishers :** 
	  Plusieurs publishers fournissent également des associations PubChem-PubMed, lorsque l'article est publié certains journaux (ex; Nature Chemical Biology) certains journaux lie directement leur article aux molécules PubChem identifiées dans l'étude.
	- **Automated annotations of PubChem records with PubMed articles via MeSH** :
	  C'est en gros ce que faisait Metab2MeSH. Mais tout les noms (synonymes) associés à un PubChem compound ne sont pas utilsé, les noms chimiques sont filtrés par rapport à la cohérence des associations chemical_name/structures des synonymes, par exemple en regroupant sous un même termes différentes formes de la molécule à différents états de charge par exemple. Ainsi, pour chaque PubChem compound, on obtient une liste de "filtered synonyms"   Les PubChem chemical Names sont matchés contre les concepts MeSH, par le biais des synonymes, permettant de créer l'association PubChem - MeSH qui permettent de liers les PMID associés au MeSH au composé Pubmed. On a ainsi : CID -> Name -> MeSH -> PMID).

Ces infos peuvent être trouvées à plusieurs endroits sur le DocSums, quand on fait une recherche sur le NCBI PubChem compounds, on peut sélectionner des compounds associées à jotre recherche et ensuite, Find l'onglet "Find Related Data", on peut trouver les papiers associées, en filtrant si on le souhaite par sources: providers, MeSH annot ou Publisher.
On a aussi ces infos dans l'onglet litterature de la page pubChem associée au composé, ou pareil, on a par sources *Depositor Provided Citations* pour les références Depositor-provided, *NLM Curated PubMed Citations* pour les associations faîtes par le biais de l'annotation MeSH, et enfin *xxx References* pour celles fournies par les Publishers.
Pour les stats un peu plus descriptives, regarder la partie *Discussion* de l'article. Ainsi : 
	- Très peu d'association sont fournies par les Publishers visiblement.
	- La plupart des PubChem Compound n'ont pas plus de 10 PMIDS associées (95% depositors provided et 70% MeSH auto-annotation).
	- Ils s'interressent ensuite à l'overlap que l'on peut trouver entre les associations CID-PMID fournies par les *Depositor-provided* et celle de *MeSH-annotation*. Ainsi, sur les 39.2 Millions d'association 4% sont communes entre les deux sources -> annotation *orthogonales*, vraiment des points de vue différentes -> complémentarité !
	- Dans cet ensemble des 4% de paires CID-PMID les CID impliqués représente 10% et les PMID 19% de tout ceux qui sont trouvés des les paires CID-PMID
   	- Il y a beaucoup moins de liens CID - PMID issues des *Depositor-provided* que ceux issus des annot meSH, **MAIS**, il y a beaucoup de CID annotés avec une association vers un PMID à partir des *Depositor-provided* Cela s'explique par le fait seul des composés assez connus et étudiés sont annotés dans les MeSH. En effet, les associations générés par les MeSH peuvent ignorer la spécificité, l'identité, du produit chimique pour annoter des termes MeSh qui représentent plutôt des "familles chimiques", à moins que le terme MeSH soit suffisament connu pour être une feuille a par entière du thésaurus MeSH. Ainsi des associations *Depositor-provided* ne souffre pas de ce problème et peuvent permettre d'annoter beaucoup plus de molécules.	  
	- Par contre les faut indiquer que PubChem ne fournie aucun contrôle supplémentaire sur les association fournies par les providers et que la qualité de ces annotations dépend uniquement des contrôles fait par les providers.	       
  
* * *

Alors, on sait que l'on peut récupérer les associations CID - SID - PMID - MeSH à partir du RDF de PubChem. Je pense qu'une première étape pour faciliter le travail ultérieur serait de créer directement dans le RDF les associations CID - PMID, par le même pricnipe que les associations au SID, Compound:CIDxxx cito:isDiscussedBy reference:PIMDyyy

Mais comme on a pu le constater, les associations avec la litterature que l'on peut récupérer avec le RDF sont celle qui sont *Depositor provided* c a d à partir de IBM, la CTD etc ... E
En fait, les associations sont initialement inidiqué à l'échelle des substances et pour le composé l'ensemble des références bibliogrpahiques sont mergées. Le seul inconvénient c'est que ces associations ne constituent pas toutes les associations à la litterature possible. Dans certains cas on observera beaucoup plus d'association *Depositor provided* que NLM Curated, ex de l'acteone avec respectivement 14580 items 7642. Mais des fois c'est l'inverse, par exemple pour le Galactose ou autre où on a beaucoup plus d'associations avec LNM curated. 

Ce que fait PubChem en fait lorsqu'il fait les NLM Curated, c'est donc qui cherche les publications pour lesquelles un MeSH correspondant à la molécule a été annoté, c'est en gros le principe de metabToMeSH. En fait, il renvoie vers une requête PubMed en utilisant comme query "meSh term"[type de MeSH]. Par exemple pour "Kdo2-lipid A" la requête va être "Kdo2-lipid A"[NM], qui est l'abbréviation de Suypplementary concept et pour le Galactose, on a "Galactose"[Mesh Terms:noexp] où c'est un 'Mesh Terms' et on demmande de ne pas étendre la requête a ces termes enfant (:noexp)

Ainsi ce qu'il nous faiut c'est le nom du terme meSh et le type de terme MeSH pour pouvoir lancé la requête avec l'outil E-utils E-search qui me renvoie direct une liste de PMID.
Je sais que : depuis le REST PubChem VIEW, on peut récupérer une vue en JSON de la page associé à un compound et dans la catégorie "Names and Identifiers" -> "Synonyms" -> "MeSH Entry Terms" en suivant la référence on peut retrouver l'identifiant UID du MeSH associé (ex : 68005690). L'identifié UID c'est l'identifiant unique dans la base de données NCBI pour représenter les MeSH. Mais pour pouvoir correctement aire des recherche autour du terme MeSH j'ai l'impression qu'il me faut le MeSH unique id (ex: C004521). Grâce a ce MeSH unique ID, on peut récupérer toutes les infos dont on a besoin sur le MeSH dans le RDF associé, son nom, son type etc ... Et ainsi on pourra construire efficacement la requête.
Donc de sur :
	- Il me faut le RDF MeSH pour avoir les noms et les types associées.
	- Il me faut le meSH unique ID. A savoir si en télécharger le bulk de PubChem, cet identifiant ne serait pas direct annoté, ou au moins le uid car par requête ça risque d'être trèèès long... Donc peut être aussi enviager de télécharger tout MeSH pour faire facilement les liens uid - MeSH unique ID. 



il y a d'autre moyens de chercher à regarder les associations entre molécule et PMID en utilisant les autres, en utilsant d'autres méthodes E-utils mais elles ne sont pas très efficace... J'ai testé : 
ELink (https://dataguide.nlm.nih.gov/eutilities/utilities.html#einfo). D'après la doc c'est : 
ELink (elink.fcgi) est un utilitaire très flexible et puissant qui prend une liste d'identifiants uniques (UID) d'une base de données et renvoie, pour chacun des UID listés :

    une liste d'UID pour des enregistrements similaires, liés ou autrement connectés dans la même base de données,
    une liste d'UID pour les enregistrements liés dans une autre base de données Entrez, ou
    une liste d'URL et d'attributs LinkOut pour les ressources connexes non-Entrez.

En raison de la puissance et de la souplesse de cet utilitaire, et parce qu'il implique des liens entre bases de données (et entre bases de données et ressources externes), il peut être difficile d'utiliser certaines de ses fonctionnalités les plus avancées. Il est conseillé aux nouveaux utilisateurs de faire preuve de patience.
A partir d'un uid on peut donc lancer une requête Elink, en paramétrant les base de données *From* et *To*, on eput faire : 
https://eutils.ncbi.nlm.nih.gov/entrez/query/static/entrezlinks.html
	- *pccompound_pubmed*: PubChem Compound to PubMed -> Très peu de résultats
	- *pccompound_pubmed_mesh* : Related PubMed via MeSH -> Peu de résultats aussi
Le mieux semble être 
	- mesh to pubmed avec *mesh_pubmed_major* : mais les résultats s'arrêtes aux publi de 2010 ... on loupe 10 ans de publi LOL MDR !

Dans tout les cas je pense que le mieux et le plus robuste est de faire exactement ce que fait PubChem !:) En reconstruisant la bonne requêe avec le nom du terme MeSH et son type

**Ce que je me dis :**
Si on a récupérer le RDF de meSH pour faire ce travail, il sera interressant de le raccorder direct au RDf de pubChem.
Si dans une étape ultérieure, on a crée des liens CID - PMID (Compound:CIDxxx cito:isDiscussedBy reference:PIMDyyy), je pense qu'il serait très utile pour que les **nouveaux** liens que l'on a pu créer avec les requêtes PubMed à la manière *NLM Curated*, de construire également des triplets pour enrichir notre RDF Compound:CIDxxx cito:isDiscussedBy reference:NewPMIDFromQueryPubMed
Et encore plus : de créer des éléments correspondant à ces PMID dans le RDF store référence c'est a dire que comme pour ce qui a été fait avec les *Depositor provided*. Donc on créer les incomming et les outgoing links, avec les prdicat *date*, *bibliographicCitation*, *http://purl.org/spar/fabio/hasSubjectTerm*, enfin exactement comme pour les PMID déjà ref (ex: https://pubchem.ncbi.nlm.nih.gov/rest/rdf/reference/PMID10395478.html)

Et on aurait un super RDF !! :)

Alors au niveau des résultats, si on prend l'exemple du Galactose (CID:6036) on a 16963 PMID associés en utilisant notre requetage via E-utils et 16961 élément si on prend les infos de la page PubChem.
Sur l'ensemble de ces éléments 16876 sont communs, ce qui fait > 99% donc c'est bon ! Les éléments qui manque ou diffère sont des publication très récentes ou bien pour beaucoup des associations qui sont *Publisher-provided* car je pense que les liens sont plus difficile à établir pour la requeêtes :/

* * * 
J'ai regardé je pense qu'on pourra direct liée le RDF MeSh au RDF de PubChem

Pour les éléments MeSH si on regarde comme dans l'es exemple de https://hhs.github.io/meshrdf/sparql-and-uri-requests, on peut direct accder a la classe du MeSh 
car exemple on a http://id.nlm.nih.gov/mesh/C506188> a http://id.nlm.nih.gov/mesh/vocab#SCR_Chemical> ;
        ou encore avec un terme MeSh simple : 
        http://id.nlm.nih.gov/mesh/D000900> a http://id.nlm.nih.gov/mesh/vocab#TopicalDescriptor> ;


### PubChem RDF References: Comment sont organisé les éléments, comment une publication PubMed est représenté dans le RDF ?

Exemple : 
![alt text](ExamplesReferencesRDF.png "Exemple de représentation d'une publication PubMed dans le RDF de PubChem")

Donc en gros, les parties principales, il y a : 

- un PMID:  l'identifiant de la publication dans PubMed.
- Citation Bibliographique : Auteur + Journal + date de parution dans le journal.
- Date: date de publication de l'article.
- Titre: Le titre de la publication
- Les Concepts MeSH (Supplementary MeSH) ('http://purl.org/spar/cito/discusses') qui commencent par des identifiants M000. Attention ce sont des concepts MeSH, pas des descripteurs! En fait il sont annotés tels des concepts MeSH mais si l'on regarde quels termes ils représentent par rapport à la publication, ils s'agit **toujours** des Supplementary MeSH que sont *Substances*, *Diseases* et *Protocols*. Au lieu d'annoter le MeSH descriptor associé à cet élément, ils annote le Concept MeSH associé. Je rappelle que dans les Supplementary MeSH tels que *Substances*, etc ... ne se trouve pas que des *Supplementary Chemical Records (SCRs)*, c'est a dire des termes trop précis ou trop rare pour être un Descriptor MeSH, mais on y trouve aussi des MeSH Descriptor tout à fait classique. Donc il s'agit bien des Supplementary MeSH

- Les Majors Topics MeSH termes ('http://purl.org/spar/fabio/hasPrimarySubjectTerm) : Les termes **Desciptors** indiqués comme major-topics de l'article
- Les autres termes MeSH ('http://purl.org/spar/fabio/hasSubjectTerm') : Les termes MeSH **Desciptors** qui décrivent la publication
- Type: le type de publication, ex "http://purl.org/spar/fabio/JournalArticle"

Par rapport aux *Supplementary MeSH*, je pense que c'est une ressource essentielle qui faut absolument conservée. En revanche, je pense qu'il serait plus utile de les décrire avec leur Descriptor MeSH associé plutôt que le Concept, car ce sera plus facile de faire des traitement ensuite si tout est standardisé avec les Descriptors. Je pense donc que dans le cas où le terme est un SCR, il faudrait récupérer à l'aide du RDF MeSH sont *Descriptor MeSH* associé. Ça doit se faire !:)


#### Donc comment retrouver ces informations dans le XML PubMed: 

- Chaque élément *PubmedArticle* du XML est essentiellement représenté par le sous Élement Descripteur *MedlineCitation*. L'élément en lui même contient des infos sur qui a jouté la publi, son statu ("reviwed", etc ...) **MAIS en fait c'est pas suffisant !!** Car la date est dans *PubmedData* donc il faut prendre l'xmlElement *PubmedArticle* et ensuite la majorité des infos sont dans le sous-élément *MedlineCitation* amsi la date sera dans
A partir de cet élément XML *MedlineCitation=* on peut accéder à l'élément PMID: *MedlineCitation PMID* qui indique le PMID associé à la publication avec la version qui y est associé. En effet, même si c'est très rare, une publi, peut avoir plusieurs PMID annoté. Ainsi, si il existe un PMID annoté avec une version > 1, cela indique qu'il existe deux versions de la publi, une version antérieure et une version actuelle. En fait, je crois qu'il y a toujours qu'un seul pmid annoté à l'élément pubmed_citation de toute façon... juste la version nous dit si c'est l'original ou quoi .. 

Attention, les attributs *DateCreated*, *DateRevised* et *DateCompleted* ne sont pas les dates associées directement à la publication du papier, mais celle où on a entré la publi dans la base, on a commencé a annotés et enfin ou on a finis d'annotés les termes MeSH pour l'indexer etc ..; 

- Ensuite on a l'élément *Journal* : décrit les éléments relatifs au Journal et à la publication de l'article dans ce Journal, c'est ici que se trouve une partie des infos recherchées pour la "Citation Bibliographique" car on aura le nom, le Volum et la date de Parution dans le Journal. Ainsi par exemple pour une Publication  annoté du style : Biochem Med. 1975 Jun;13(2):117-26., il s'agit en fonction des attribut de *Journal* de : 
*ISOAbbreviation*. *PubDate Year* *PubDate Month*; *JournalIssue Volume*(*JournalIssue Issue*)*Pagination MedlinePgn* 
Attention *Pagination MedlinePgn* , ne sont plus des enfant de *Journal*, mais sont les éléments qui suivent.
La liste des auteurs pour compléter le "Citation Bibliographique" se trouve dans les éléments *AuthorList Author*

- Pour la Date: Pour la Date je pense qu'on peut prendre le *PubDate Year* *PubDate Month*, et rajouter *PubDate Day* comme dans la Citation.

- Pour le titre: Il est dans l'Élément XMl *ArticleTitle*

- Les Supplementary MeSH: Les supplémentary MeSH sont stockés dans des Élément XML différents selon s'il s'agit de *Substances* ou de *Diseases* et *Protocols*. Ainsi, pour les *Substances* c'est dans *ChemicalList Chemical* chaque Élément XMl présente alors le MeSH unique ID assoicé : un *MeSH Descriptor* comme par D; ou un *MeSH SCR Chemical* (les Suppl records) qui comment par C. On a un parfait exemple ici :   https://www.nlm.nih.gov/bsd/licensee/elements_descriptions.html#supplmesh. Pour les autres (*Diseases* et *Protocoles*) c'est *SupplMeshList SupplMeshName*. Pareil ici se seront souvent des *MeSH SCR Diseases et Protocoles* qui commencent aussi par C.
- il faut donc impérativement mettre une routine en place pour convertir si besoin un *MeSH SCR* vers un *Descriptor MeSH* en s'appuyant sur le RDF MeSH. **Ou alors peut être qu'en branchant directement le RDF MeSH à notre RDF, on aurait pas besoin ... il suffirait de construire les bonnes requpetes jsp ...**

- Les Majors Topics MeSH: Dans le noeud *MeshHeadingList* chaque Élément XML *MeshHeading* représente un **Desciptor** MeSH avec son **Qualifier** MeSH si il y en a un. A partir de là, grâce aux attributs *UI*, on a le MeSH Unique Identidier et l'attribut *MajorTopicYN* (associé au Descripteur OU au qualifier dans le cas de couples *Descriptor/Qualifier*)  = "Y" ou "N" suivant s'il s'agit ou non d'un Major Topic

- Les autres termes MeSH : Ce sont tout les éléments *MeshHeading* qui ne sont pas major :) 

- le Type : *PublicationTypeList PublicationType*


* * *
Je pense que c'est pas une bonne idée de compléter les objets PMIDs avec les propriétés des MeSH annttéd dans PubMed, car un même PMID peut être retrouvé chez beaucoup de pcc et aussi ça ferai beaucoup trop grossir la taille du fichier ...
Vue que je peut avoir l'union de **tout** les PMID associés à tout les éléments Pccompound de mon Ensemble_pccompound, je pense travailler à partir de cette liste.
On crée un object Ensemble Citation qui est associé à **1** fichier de PubMed et pour lequel on aura récupérer que les citations qui correspondent à des PMID qui appartiennent à notre Union.
Dès que l'on a lu tout les fichier ou que la liste est vide ou s'arrete.
Le meix je pense serait de DL TOUT les fichier, mais surtout pas de les décomprésser, mais dès que l'on crée un nouvel Objet Ensemble_ci, on décompresse le fichier à la volé puis on le recompresse.


Pour HMDB: je pense que ce n'est pas le moment de l'intégrer, car en fait les liens Métabolite - Diseases sont ici fait à partir des MeSH associés associées ux publications parlant de ces maladies. mais dans le cas de HMDb, même si une publication est associé à cette association, rien ne dit que le MeSH de la maladie et du métabolite sera annoté. Donc ce n'est pas le même type de relation mise en jeux:
	- **From meSH**: MeSH met. et MeSH disease annoté dans la publication
	- **From HMDB**: le métabolite est annoté en concentration anormale dans cette maladie, et il y une référence de la publication. Il peut y avoir plusieurs abnormal concentration qui sont annotés entre ce métabolite et la maladie. 
	- 
  En gros je ne pense pas qu'il soit judicieux de prendre les PMID associés aux concentrations anormales annotées entre un métabolites et une maladies dans HMSB pour chercher à récupérer des MeSH ou quoi ... car l'association n'est pas faite avec des MeSH à la base mais "manuellement"

  Peut être que quand on aura les liens direct Metabolites - PMID - Maladies, si HMSB apporte de nouveaux PMID impliqué dans l'association de ce métabolite avec cette maladie, alors là on pourra prendre l'union des PMID entre notre annotation et HMDB 


  Bon bah je m'arrete là car il semble que PubChem est déjà fait tout mon travail finalement ...
  Enfait certes les associations publications - CID ne sont référencé que par les depositors Provided mais même des publications associée par le biais des MeSH sont indéxées dans le RDF de PubCHEM Reference, seulement elles n(ont pas de outgoing links ...
  Donc je stoppe là, je vais dl tout le ref de PubChem

  Au pire on completera le code pour récupérer les éléments manquant

  * * *
  
  Bon pour faire notre OWL: 
  - Pour le type de mes élément reference:PMID:
    - D'après le fichier reference_type de PubChem, il y a 
    - 12216202 fabio:JournalArticle .
    - 1186795 fabio:ReviewArticle .
      - Qui sont tous les deux des sous-classes de http://purl.org/spar/fabio/Article

Donc en important le Vocabulaire de Fabio: On peut récupérer tout les article avec le Type Article:
PREFIX cito:	<http://purl.org/spar/cito/>
PREFIX compound:	<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
PREFIX reference:	<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/>
PREFIX fabio:	<http://purl.org/spar/fabio/>

select ?x ?y where {
  ?x a fabio:Article
  ?x a ?y
}


  - Pour le type de mes élément compound:CID... ils n'ont pas vraiment de type particulier ...
  - Ils sont rattacher au type associé de leur ChEBI, donc chaque molécule à un type différent en vrai. Mais du coup, si toute l'ontologie ChEBI est importer, on peut montrer qu'il sont tous de type "CHEBI:23367 molecular entity" qui est définit comme "Any constitutionally or isotopically distinct atom, molecule, ion, ion pair, radical, radical ion, complex, conformer etc., identifiable as a separately distinguishable entity."

Donc j'ai fait un parseur adapté a tout type de fichier turtle, maitenant on peut parser les fichiers PubChem_compound où on peut par exemple avoir le type et DONC le ChEBI associée. Ce parseur permet donc de récupérer les lignes pour lesquelles il s'agit d'un des cids que j'ai sélectionner depuis la liste totale. Ainsi, en incorporant également l'ontologie owl de ChEBI, on peut avoir avoir : 

PREFIX cito:	<http://purl.org/spar/cito/>
PREFIX compound:	<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
PREFIX reference:	<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/>
PREFIX fabio:	<http://purl.org/spar/fabio/>
PREFIX obo:	<http://purl.obolibrary.org/obo/>

select distinct ?x where {
  ?x a CHEBI_23367
  ?x cito:isDiscussedBy ?p
}

Pour rappel, **obo c'est ChEBI**

la liste de toutes les molecules. Et ainsi maintnenant les éléments sont bien typé !

Après il semble qu'il est a aussi l'ontologue BioPax, où chaque composé est également du type bp:SmallMolecule


Peut être que le miexu c'est de créer la propriété chainé et ensuite avec le SPARQL on fera les restriction sur les types pedant que l'on requetera les éléments !


Dans les fichiers référence PubChem  pc_reference2chemical_disease_00000x j'ai remplacé l'attribution de *cito:discusses* par *fabio:hasSubjectTerm* car *fabio:hasSubjectTerm* est fait pour mettre en référence des MeSH, contrairement à *cito:discusses* qui n'est pas très adapté ici. Et en plus étant la propriété inverse de*cito:isDiscussedBy*, cela crée des mauvaise inférence lorsque je veux créer des liens entre Compound et MeSH term.

J'ai pensé à intégrer la disease Ontologie pour détermin er plus efficacement les termes désignant des maladies et les autres, mais le problème c'est qu'ils n'ont pas fait l'effort de mettre des URI pour les cross-ref ... genre pour le MeSHJ c'est un String su coup ...

Comment marche un peu le owl: Le tout est simplement de dire que voc:HasUndirectDescriptor est une propriété chainé sur fabio:hasSubjectTerm -> meshv:hasDescriptor et que en fait la désigne comme la même chose que fabio:hasSubjectTerm. Ainsi tout ce que est pointé par voc:HasUndirectDescriptor est par inférence aussi pointé par fabio:hasSubjectTerm. Ainsi les objects des triplets de fabio:hasSubjectTerm contiennent **tout** les TopicalDescriptors, qu'ils soient seuls ou qu'ils étaient en paires.



Bon la owl est ok ! Maintenant ça fonctionne pour récupérer notre matrice (### QUERY SPARQL POUR FAIRE NOTRE MATRICE) le seul truc c'est que dans le rdf Store de PubChem, il n'y pas d'information de HasPrimarySubjectTerm... Elle est dispo sur la page mais pas dans les données que l'on peut télécharger .. J'ai envoyé un mail aà PubCheml pour savoir ce qu'il en était

* * *
Les gens de PubChem m'ont répondu : 
" Dear Maxime,

Thanks for your comment! It is a known issue from our side, which we consider to correct it in our future plan. For now, I would suggest that you use our rest service to retrieve the data you want.  Detailed information is available in https://pubchemdocs.ncbi.nlm.nih.gov/rdf

Thanks,
Leon "
En gros cette partie là du Service est indisponible sur le ftp de PubChem. En revanche ils suggèrent d'utiliser le PubChemRDF REST. Avec de REST, on peut faire des query qui permettent de récupérer certains couples Subjects-Predicate-Object en spécifiant les paramètres “graph” (or “domain”) and “predicate” (or “pred”). Il faut également gérer les offset. En effet, seulement 10000 résultats peuvent être renvoyé de manière simultanée, et pour obtenir les 10000 résultats suivant (soit e 10001 à 20000 par ex) il faut spécififier l'attribut offset. La doc est présent à https://pubchemdocs.ncbi.nlm.nih.gov/rdf$_5-2 **Query RESTful Interface**


Il va falloir créer une fonction pour récupérer tout cela.

Donc un petit résumé de comment fonctionne mon fichier OWL:
 -La première problématique a traité et le fait de toujours pouvoir référer à un terme MeSH de type TopicalDescriptor, car c'est cette classe de Termes qui présente un "héritage" dans le structure du thésaurus MeSH. Cet héritage de concept est formalisé par la propriété broaderDescriptor qui indique des termes plus généraux pour décrire ce concept. Cependant, tout les meSH annotés ne sont pas des des TopicalDescriptor, on a aussi des Supplementary Concepts Records et des DescriptorQualifierPairs. Pour les Supplementary Concepts Records, étyant des concepts, on ne peux malheureusement pas les lier à des Topical Descriptor? En revanche pour les DescriptorQualifierPairs, grâce à leur propriété hasDescriptor, on peut déterminer le TopicalDescriptor associé à la partie Descriptor de la paire. Ainsi en déclarant :

voc:HasUndirectDescriptor owl:propertyChainAxiom ( fabio:hasSubjectTerm meshv:hasDescriptor ) .
voc:HasUndirectDescriptor owl:equivalentProperty fabio:hasSubjectTerm .

On crée une propriété HasUndirectDescriptor qui est une chaine sur hasSubjectTerm et hasDescriptor permettant donc de lier un pmid a un descriptor dans le cas d'un DescriptorQualifierPairs. Ensuite on indique que cette propriété est la même chose que fabio:hasSubjectTerm de tel sorte qu'en recherchant les triplets avec cete propriété on récupère par inférence directe ceux qui ont HasUndirectDescriptor.

Pour la suite on commence par rendre la propriété broaderDescriptor transitive 
meshv:broaderDescriptor a owl:TransitiveProperty .

Ensuite on crée la classe DiseaseMesh avec :
voc:DiseaseMeSH a owl:Class ;
    owl:oneOf
        (mesh:D007239 mesh:D009369 mesh:D009140 mesh:D004066 mesh:D009057 mesh:D012140 mesh:D010038 mesh:D009422 mesh:D005128 mesh:D052801 mesh:D005261 mesh:D002318 mesh:D006425 mesh:D009358 mesh:D017437 mesh:D009750 mesh:D004700 mesh:D007154 mesh:D007280 mesh:D000820 mesh:D013568 mesh:D009784 mesh:D064419 mesh:D014947 ) .

On la crée en déclarant tout les memebres de la classes qui représente les termes MeSH racine de la partie Disease de l'arbre meSH à savoir: Infections [C01], Neoplasms [C04], Musculoskeletal Diseases [C05], etc ... 

Ensuite, on crée la classe DiseaseLinkedMesH en déclarant qu'il s'agit des termes MeSH pour lesquels au moins l'un des broderDescriptor (devenu transitif) est un des termes racine de la partie Disease de l'arbre MeSH et qui appartient donc à la classe DiseaseMeSH
voc:DiseaseLinkedMesH rdf:type owl:Class ;
        owl:equivalentClass [ rdf:type owl:Restriction ;
            owl:onProperty meshv:broaderDescriptor ;
            owl:someValuesFrom voc:DiseaseMeSH
        ] .


Le fait que des termes soient annotés avec hasPrimarySubjectTerm ne pose pas de problème car  étant une sous-propriété de hasSubjectTerm lorsque que l'on appelle hasSubjectTerm on récupère donc aussi ceux annotés avec hasPrimarySubjectTerm.

Pour montrer que àa marche bien on a cette publcation où le seule terme MeSH maladie est un primary MeSH et DescriptorQualifierPair où ce descripteur est unique à cette paire, et en utilisant la requête suivante on arrive bien a retrouver le terme Descriptor de la paire qui le porte dans les PrimaryMeSH


select ?pmid ?mesh where {
	reference:PMID13147725 fabio:hasSubjectTerm ?mesh
	?mesh a voc:DiseaseLinkedMesH
}

Olivier a suggérer que pour mieux gérer le versionning de nos RDF et aussipour correctement garder une trace de ce qui a été Importer/Modifier ou créée depuis le RDF de PubChem

Donc finalement vue que le reasoner de Virtuoso n'est pas capable de faire les inférences OWL demandés, finalement on est obligé de le faire en SPARQL. Néanmoins cela semble plus performant et Olivier était également de cet avis.
je copie colle quand même l'intoogie que l'on avait fait au cas où ça serve un jour.

@prefix cito:	<http://purl.org/spar/cito/> .
@prefix compound:	<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/> .
@prefix reference:	<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> .
@prefix endpoint:	<http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/> .
@prefix obo:	<http://purl.obolibrary.org/obo/> .
@prefix dcterms:	<http://purl.org/dc/terms/> .
@prefix mesh:	<http://id.nlm.nih.gov/mesh/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix meshv: <http://id.nlm.nih.gov/mesh/vocab#> .
@prefix fabio:	<http://purl.org/spar/fabio/> .
@prefix xsd:	<http://www.w3.org/2001/XMLSchema#> .
@prefix rdf:	<http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix voc: <http://myorg.com/voc/doc#> .
<http://myorg.com/voc/doc#> a owl:Ontology ;
    dcterms:contributor "Delmas Maxime"^^xsd:string,
        "Clément Frainay"^^xsd:string ,
        "Olivier Filangi"^^xsd:string ;
    dcterms:creator "Delmas Maxime"^^xsd:string ;
    dcterms:date "2020-03-14"^^xsd:date ;
    owl:versionInfo "1.0.0"^^xsd:string .

voc:HasUndirectDescriptor owl:propertyChainAxiom ( fabio:hasSubjectTerm meshv:hasDescriptor ) .
voc:HasUndirectDescriptor owl:equivalentProperty fabio:hasSubjectTerm .

meshv:broaderDescriptor a owl:TransitiveProperty .

voc:DiseaseMeSH a owl:Class ;
    owl:oneOf
        (mesh:D007239 mesh:D009369 mesh:D009140 mesh:D004066 mesh:D009057 mesh:D012140 mesh:D010038 mesh:D009422 mesh:D005128 mesh:D052801 mesh:D005261 mesh:D002318 mesh:D006425 mesh:D009358 mesh:D017437 mesh:D009750 mesh:D004700 mesh:D007154 mesh:D007280 mesh:D000820 mesh:D013568 mesh:D009784 mesh:D064419 mesh:D014947 ) .

voc:DiseaseLinkedMesH rdf:type owl:Class ;
        owl:equivalentClass [ rdf:type owl:Restriction ;
            owl:onProperty meshv:broaderDescriptor ;
            owl:someValuesFrom voc:DiseaseMeSH
        ] .



Les DBidentifiers.org du modèle pose je pense un petit problème, car les URI ne sont pas celle pointés dans les ontology:
Dans le chebi.owl, on a par exemple les URIs : 
http://purl.obolibrary.org/obo/CHEBI_16424

De la même manière dans les fichier de PubChem on a 
@prefix obo:	<http://purl.obolibrary.org/obo/> .
http://purl.obolibrary.org/obo/ obo:CHEBI_16424


Mais dans le fichier de Human RDF, on a :
 http://identifiers.org/chebi/CHEBI:16424

 où celui pointe en fait vers :	https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:{$id}
 ce qui n'est pas l'URI de la ressource dans l'ontology de ChEBI ...

 Solution ? convertir toutes les URI du modèle en URI "correcte" comme dans l'ontology ?


 Pour l'ensemble des propriétés PubChem compounds and descriptors.
 Il y a beaucoup de propriété et certainement que la majorité ne nous interressent pas, genre "_Rotatable_Bond_Count" est-ce-qu'il serait pas préférable de les supprimer dces graph obtenus. Il faudrait les supprimer de la partie compound2descriptor et de la partie descriptor car ce sont en quelques sortes des blankNodes. On pourrait le faire en utilisant un set de type de propriété ChemINF que l'on voudrait conservé car chacun de ces blanknodes est annoté avec un type ChemINF. Donc a voir si ça vaut le coup...

 * * *
 * Après avoir parsé l'ensemble des PubChem Descriptor, il semble qu'il manque l'attribut *Compound_Identifier*. Ce n'est pas très grace car par exemple pour le CID6036 et bien la valeur c'est 6036, peut être donc qu'il s'emmerdent pas à la mettre et qu'elle est déterminer à la volée. Donc je peux l'enlever des features à recherchées !


The query which may be used to get all the cid - MeSH diseases assocaition with the number of associated pmid is :  

```
DEFINE input:inference 'schema-inference-rules'
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
PREFIX voc: <http://myorg.com/voc/doc#>
prefix cito: <http://purl.org/spar/cito/>
prefix fabio:	<http://purl.org/spar/fabio/> 
prefix owl: <http://www.w3.org/2002/07/owl#> 
prefix void: <http://rdfs.org/ns/void#>

select ?cid ?mesh ?name ?countdist where {
	
	?mesh rdfs:label ?name .	
	{
		select ?mesh ?cid (count(distinct ?pmid) as ?countdist) where {
		?cid cito:isDiscussedBy ?pmid .
		?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
		?mesh a meshv:TopicalDescriptor .
		
		?mesh meshv:treeNumber ?tn .
		FILTER(REGEX(?tn,"C"))
		}
		group by ?mesh ?cid
		
	}
}ORDER BY DESC(?countdist)


Sparql query pour récupérer tout les smiles associés à mes species en passant par chebi : 
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>

select ?specie ?ref ?smile where {
  ?specie a SBMLrdf:Species .
  ?specie bqbiol:is ?ref .
  FILTER(STRSTARTS(STR(?ref), "http://purl.obolibrary.org/obo/CHEBI_"))
  ?ref <http://purl.obolibrary.org/obo/chebi/smiles> ?smile
}

Pour accéder à MeSh Sparql depuis notre vituoso on peut faire comme ça :
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
PREFIX mesh2020: <http://id.nlm.nih.gov/mesh/2020/>
PREFIX mesh2019: <http://id.nlm.nih.gov/mesh/2019/>
PREFIX mesh2018: <http://id.nlm.nih.gov/mesh/2018/>

select * where {
    service <http://id.nlm.nih.gov/mesh/sparql> {
        SELECT DISTINCT ?class
        FROM <http://id.nlm.nih.gov/mesh>
        WHERE { [] a ?class . }
        ORDER BY ?class
    }
}

Ha et aussi autre raison de bien vérifier nos ids: je me rends compte que des fois mon script n'a pas pu trouver d'information pour un PubChem CID dans le RDF, étrange puique je pars de toute la base. Il se trouve en fait que des fois, dans le SBML des éléments annotés CID sont en fait des SID chez PubChem, ils ont un CID, mais c'est pas celui indiqué dans le SBML. Bon après c'est seulement le cas pour 36 sur 1381 et c'est genre des gros lipides ou des trucs pas très bien annotés donc c'est pas très grace au pire. Mais peut être qu'avec UniChem on pourrait corriger ce genre de chose 

### Pour ChemBL : 
Je pense pas que ChemBL soit si important dans un premier temps car finalement j'ai pu importer ces identifiants qu'à partir de ce que je connaissait déjà, dès lors cela ne m'apportera aucune nouvelles information pour les SMILES ou les Inchi par exemple.
Pour les InchiKey et les autres, je pense qu'il faudra aussi créer des triples avec un contruct.


# Requête pour trouver le nombre de species qui présente une référence dont l'URI appartient à tel pattern : 
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
select count(distinct(?specie)) where {
 	?specie a SBMLrdf:Species ;
		bqbiol:is ?ref .
  	FILTER ( STRSTARTS(STR(?ref), "http://identifiers.org/metanetx.chemical/"))
}

## Pour compter le nombre de species pour lesquelles on ne dispose **pas** d'indentifiants metanetX, mais pour lesquelles on disposerait d'autres identifiants qui nous permettrait de retrouver des infos sur les InCHi, SMILES, etc ...

DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>

select count(distinct(?specie)) where {
 	?specie a SBMLrdf:Species ;
	bqbiol:is ?ref .
	FILTER ( STRSTARTS(STR(?ref), "http://identifiers.org/chebi/CHEBI:") || STRSTARTS(STR(?ref), "http://identifiers.org/pubchem.compound/") || STRSTARTS(STR(?ref), "http://identifiers.org/lipidmaps/"))
 	MINUS
 	{
 	 	?specie a SBMLrdf:Species ;
	 			bqbiol:is ?ref_metanetX .
		FILTER ( STRSTARTS(STR(?ref_metanetX), "http://identifiers.org/metanetx.chemical/"))
 	}
}


Pour le test sur les inchi et smiles pour savoir s'ils sont uniques à la molécule, dans un premier temps je fais avec Specie name, mais lorsque l'on aura définit l'entity biologique supérieure il y aura juste a changer ça. Pour récupérer tout ceux qui ne sont pas unique il suffit de mettre 	having(count(distinct(?spe_name)) > 1)

La requête pour aller chercher tout les couples spe_name Smiles qui lesquels le smiles est associé à x spe_name est : 
```SQL

DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
prefix mnx: <https://rdf.metanetx.org/schema/>
prefix sio: <http://semanticscience.org/resource/>

select distinct ?spe_name ?str_smiles where {

{
	select str(?smiles) as ?str_smiles where {
		?specie a SBMLrdf:Species ;
			SBMLrdf:name ?spe_name .
		OPTIONAL { ?specie bqbiol:is ?ref_metaNetX . FILTER ( STRSTARTS(STR(?ref_metaNetX), "https://rdf.metanetx.org/chem/")) }
		OPTIONAL { ?specie bqbiol:is ?ref_chebi . FILTER ( STRSTARTS(STR(?ref_chebi), "http://purl.obolibrary.org/obo/CHEBI_")) }
		OPTIONAL { ?specie bqbiol:is ?ref_pc . FILTER ( STRSTARTS(STR(?ref_pc), "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID")) }            
		{ ?ref_metaNetX mnx:smiles ?smiles . }
		UNION
		{ ?ref_chebi <http://purl.obolibrary.org/obo/chebi/smiles> ?smiles . }
		UNION
		{ 
		?ref_pc sio:has-attribute ?ref_pc_desc .
		?ref_pc_desc a sio:CHEMINF_000376 ;
			sio:has-value ?smiles
		}
		                
		}
	group by str(?smiles)
	having(count(distinct(?spe_name)) = 1)
}

	?specie a SBMLrdf:Species ;
		SBMLrdf:name ?spe_name .
	OPTIONAL { ?specie bqbiol:is ?ref_metaNetX . FILTER ( STRSTARTS(STR(?ref_metaNetX), "https://rdf.metanetx.org/chem/")) }
	OPTIONAL { ?specie bqbiol:is ?ref_chebi . FILTER ( STRSTARTS(STR(?ref_chebi), "http://purl.obolibrary.org/obo/CHEBI_")) }
	OPTIONAL { ?specie bqbiol:is ?ref_pc . FILTER ( STRSTARTS(STR(?ref_pc), "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID")) }            
	{ ?ref_metaNetX mnx:smiles ?smiles . }
	UNION
	{ ?ref_chebi <http://purl.obolibrary.org/obo/chebi/smiles> ?smiles . }
	UNION
	{ 
	?ref_pc sio:has-attribute ?ref_pc_desc .
	?ref_pc_desc a sio:CHEMINF_000376 ;
		sio:has-value ?smiles
	}
FILTER(str(?smiles) in (?str_smiles))

}

```


## CONFIG VIRTUOSO:
* For Buffers:
SYS.RAM	NumberOfBuffers	MaxDirtyBuffers
2 GB 	170000 			130000
4 GB 	340000 			250000
8 GB 	680000 			500000
16 GB 	1360000 		1000000
32 GB 	2720000 		2000000
48 GB 	4000000 		3000000
64 GB 	5450000 		4000000 

* MaxCheckpointRemap:  1/4th of the database size is recommended

* For other important parameters like ThreadsPerQuery, AsyncQueueMaxthreads, ... see http://docs.openlinksw.com/virtuoso/vexqrparlconfp/


**Initials URIs in the SMBL graph MUST be identifiers.org URIS !**
This request may be separated in 3 main parts :
And **version** must be fill in the Graph URI. 
#### part 1 : Get synonyms of existing uris : 
As indicated in the Graph URI, this file should be named *synonyms.trig*
```SQL
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
construct {
	 GRAPH <http://database/ressources/annotation_graph/version> { ?specie bqbiol:is ?ref_syn . }
}where {
	?specie a SBMLrdf:Species ;
		bqbiol:is ?ref .
	?ref skos:exactMatch ?ref_syn option(t_distinct) .

}
```
For a specie, we extract all the current uris associated to the predicate bqbiol:is, and for those elements we extract uris which are in skos:exactMatch with them, so their intra-ressources URI synonyms

#### part 2  : Extraction of infered equivalent uris :
As indicated in the Graph URI, this file should be named *infered_uris.trig*
```SQL

DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
construct {
	GRAPH <http://database/ressources/annotation_graph/version> { ?specie bqbiol:is ?otherRef . }
}where {
		?specie a SBMLrdf:Species ;
			bqbiol:is ?ref .
		?ref skos:closeMatch ?otherRef .
		FILTER (
			not exists { ?specie bqbiol:is ?otherRef }
			&&
			not exists {?ref skos:exactMatch ?otherRef option(t_distinct)}
		)

}
```
For a specie, we extract all the current uris associated to the predicate bqbiol:is, and for those elements we extract uris which are associated to the element with a skos:closeMath predicate, corresponding to equivalent URIs from identfiers equivalence provided by UniChem. **BUT**, we specifie that the extracted URI **must** not ne already known in the current graph *not exists { ?specie bqbiol:is ?otherRef }* **AND** that the extracted URI are not a synonym of the current annotate URIs (*not exists {?ref skos:exactMatch ?otherRef option(t_distinct)}*), because of *skos:exactMatch* is a sub-property of *skos:closeMatch*, by searching equivalent URIs using skos:closeMatch, we may extract synonyms of the already annotated URIs, but this is already done by the first request.

#### part 3 : Extraction of synonymes of infered equivalent uris :
As indicated in the Graph URI, this file should be named *infered_uris_synonyms.trig*
```SQL

DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
construct {
	GRAPH <http://database/ressources/annotation_graph/version> { ?specie bqbiol:is ?otherRef_syn . }
}where {
	?otherRef skos:exactMatch ?otherRef_syn option(t_distinct) .
	FILTER (
		not exists { ?specie bqbiol:is ?otherRef_syn }
		&&
		not exists { ?ref skos:exactMatch ?otherRef_syn option(t_distinct) }
	)
	{
		select ?specie ?otherRef ?ref where {
		?specie a SBMLrdf:Species ;
			bqbiol:is ?ref .
		?ref skos:closeMatch ?otherRef .
		FILTER (
			not exists {?specie bqbiol:is ?otherRef }
      &&
    		not exists { ?ref skos:exactMatch ?otherRef option(t_distinct) }
		)

		}
	}
}
```
For a specie, we extract all the current uris associated to the predicate bqbiol:is, and for those elements we extract uris which are associated to the element with a skos:closeMath predicate, corresponding to equivalent URIs from identfiers equivalence provided by UniChem. **BUT**, we check that this URIs are not already known in the current annotation **AND** that the *?otherRef* is not a synonym of ?ref (becacuse *skos:exactMatch* is a sub-property of *skos:closeMatch*). And, for those URIs, we extract all their direct synonyms using *skos:exactMatch* and we check that this synonyms are not already present in the annotation (*not exists { ?specie bqbiol:is ?otherRef_syn }*) **and**, that this synonyms are not synonyms of already known annotation (*not exists { ?ref skos:exactMatch ?otherRef_syn option(t_distinct) }*), like those we were added with the query !

Finally it's really more computionnaly efficient to separate this work in three diffenret queries.


### To count the number of added URIs from a specific pattern
#### (#Part 1 ) 
```SQL

DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
select count(distinct(?ref_syn)) where {
	?specie a SBMLrdf:Species ;
		bqbiol:is ?ref .
	?ref skos:exactMatch ?ref_syn option(t_distinct) .
  	FILTER ( STRSTARTS(STR(?ref_syn), "/pattern/"))
}

```

#### (#Part 2) 
```SQL
DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
select count(distinct(?otherRef)) where {
		?specie a SBMLrdf:Species ;
			bqbiol:is ?ref .
		?ref skos:closeMatch ?otherRef .
		FILTER (
			not exists { ?specie bqbiol:is ?otherRef }
			&&
			not exists {?ref skos:exactMatch ?otherRef option(t_distinct)}
      &&
      STRSTARTS(STR(?otherRef), "/pattern/")
		)

}
```

#### (#Part 3)

```SQL

DEFINE input:inference 'schema-inference-rules'
prefix SBMLrdf: <http://identifiers.org/biomodels.vocabulary#>
prefix bqbiol: <http://biomodels.net/biology-qualifiers#>
prefix mnxCHEM: <https://rdf.metanetx.org/chem/>
prefix chebi: <http://purl.obolibrary.org/obo/CHEBI_>
prefix model: <http:doi.org/10.1126/scisignal.aaz1482#>
prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>

select count(distinct(?otherRef_syn)) where {
	?otherRef skos:exactMatch ?otherRef_syn option(t_distinct) .
	FILTER (
		not exists { ?specie bqbiol:is ?otherRef_syn }
		&&
		not exists { ?ref skos:exactMatch ?otherRef_syn option(t_distinct) }
    &&
    STRSTARTS(STR(?otherRef_syn), "/pattern/")
	)
	{
		select ?specie ?otherRef ?ref where {
		?specie a SBMLrdf:Species ;
			bqbiol:is ?ref .
		?ref skos:closeMatch ?otherRef .
		FILTER (
      		not exists {?specie bqbiol:is ?otherRef }
      		&&
      		not exists { ?ref skos:exactMatch ?otherRef option(t_distinct) }
		)
		}
	}
}
```



Au niveau de la mise à jour de 2020-05-29 sur le le RDF Store:
- Maj du store Reference avec les Primary MeSh directement inclus
- Maj des associations
Pour les associations:
	-  il y a : 664104 associations présentes uniquement dans le store de 05-29 et pas présente dans la précédente release, qui ont été *ajouté*
	- il y a 743343 associations présentes uniquement dans le store de 04-18 et qui ne sont plus présente en 05-29, et qui ont donc été supprimé, avec la différences des 2, on retrouve 79239 ce qui correspond a la différence du nombre de triplets observé avec void.ttl
	Donc on en a supprimé plus que l'on en a ajouté.
Il y a eu des correction Ex de la Cyclosomatostatin (CID: 4195535) qui était associé a des publis parlant de somatostatin par erreur (Ex: PMID 2569533)
La requête utilisée:

```
select *
where {
GRAPH <http://database/ressources/PMID_CID/2020-04-18> {?s ?p ?o}

FILTER( not exists{ GRAPH <http://database/ressources/PMID_CID/2020-05-29> {?s ?p ?o} })
}
limit 1000
```


## Pour les corrections apportés aux requête de metab2mesh à cause des liens PMID cito:discusses SCR MeSh :
Dans plusieurs cas j'ai utilisé le graph endpoint à la place du graph classique PMID_CID.

Dans le cas des requête groupé par MeSH ou pour les comptes totaux de pmids, j'ai remplacé ?cid cito:isDiscussedBy ?pmid par :

?endp obo:IAO_0000136 ?pmid .

Car si la publication (?pmid) présente un liens de type obo:IAO_0000136 avec un élément de endpoint c'est qu'elle est forcément lié à un composé puique que ces entité sont créés pour toutes les associations PMID - CID.


Pour récupérer les MeSH Tree number, j'ai utilisé la requête suivante :
```
DEFINE input:inference "schema-inference-rules"
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
PREFIX voc: <http://myorg.com/voc/doc#>
PREFIX cito: <http://purl.org/spar/cito/>
PREFIX fabio:	<http://purl.org/spar/fabio/> 
PREFIX owl: <http://www.w3.org/2002/07/owl#> 
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
PREFIX sio: <http://semanticscience.org/resource/>
PREFIX obo: <http://purl.obolibrary.org/obo/>

select distinct (strafter(str(?mesh), "http://id.nlm.nih.gov/mesh/") as ?MESH) (strafter(str(?tn), "http://id.nlm.nih.gov/mesh/") as ?TREE_NUMBER)
where
{
?mesh a meshv:TopicalDescriptor .
?mesh meshv:treeNumber ?tn .
}
```


# ChEBI by MeSH

Pour les Chebi, on a au total : 93409 CID qui ont un ChEBI associé. 
Si on ne considère que les classes ChEBI pour lesquelles elles représentent au maximum 10% de ma librairie totale de molécule, soit 9340, on peut mettre à 10000 pour être large

Dans le cas où l'on cherche à déterminer le nombre pmid associé à un Chebi: on a besoin d'utiliser l'ontologie ChEBI est disant ?cid a+ ?chebi car l'on veut récuprer à la fois les cid associé au Chebi mais également les cid associés à tout les ChEBI fils du ChEBI cible.

En revanche, lorsque l'on cherche à déterminer déterminer le nombrede pmid associé à chaque MESH en utilisant comme unvisers l'ensemble des ?pmid mentionnant également un CID qui présente un MeSH qui nous intéresse. Pour les rappel les MESH sélectionnés sont ceux pour lesquels on a moins de 10.000 cid associés.
Pouir déterminer cet univers, on a pas besoin d'utiliser l'ontologie ChEBI directement car on peut simplement sélectionner tout ?cid qui a un ChEBI qui appartient à l'ensemble ?CHEBI sélectionner, mais pas besoin de tester que vérifier que celui-ci est également de la classe des ChEBI enfant

Peu importel les éléments sélectionner dans les requête, l'Univers est troujours lensembl des cid pour lesquels on dispose d'un Chebi.

Ainsi faire:
select (count(distinct ?cid) as ?count) 
{
                            ?chebi rdfs:subClassOf+ chebi:24431 .
                            ?cid a+ ?chebi
}      
revient au même que de faire :
select (count(distinct ?cid) as ?count) 
{
                            ?cid a chebi:24431
}  
Seulement que pour les autres requêtes, on a pas vraiemnt bveosin de connaitre tout les  cid présents dans chaque classue ChEBI, on a juste besoin de connaitre tout ceux qui ont une classe ChEBI


### Metab2MeSH with Species :

Initialement avec les graph d'annotations : MetaNetX 3.0 et PubChem type 2020-04-24, nous avons 4759 spcies avec un identifiant CID associé par bqbiol:is.
Parmis ces 4759 species il y en a 3861 qui ont un CID pour lequel on dispose de litterature soit 38%

Pour voir l'effet de notre graph d'annotation j'ai également réalisé les comtages sans loader le graph d'annotations des uris inférés et des uris synonymes inférés, on obtient alors 3275 species pour lesquelles on peut alors lier de la littérature. 

Dans le papaier Mind The Gap, il y avait 869 species pour lesquelles on a de la littérature dans le réseau de Recon2.04. **MAIS ATTENTION** il s'agit de species uniques, sans compartiement !!!!! Nous si on veut faire ~ la même chose en utilsant notre Human1, on va chercher à faire la même requête mais on va compter le nombre de *name* différents cat il sera le même pour la molécule, peut importe le compartiment, alors on obtiens 1196 species uniques avec de la littérature associé, donc c'est pas mal, mais c'est pas fifou non plus !

Donc on a effectivement one amélioration intéressante sur le nombre de species pour lesquelles on peut lier de la littérature en utilisant le graph d'annotation

Au sujet de ma problématique sur "est-ce que je dois considérer seulement les articles qui parlent de maladies lorsque je vais faire mon metab2mesh avec les species pour ensuite propager" en fait on se rend compte que suivant si on considère tout les catégorie MeSH ou seulement la catégorie MeSH Disease en fait on répond pas à la même question.
Si on considère toutes les catégories on répond à : "Parmis tout les sujets (topic) qui sont associés à ma molécule, est-ce que la fait de parler d'Alzeimer est vraiment significatif ?"
En revanche, si on considère seuelement la catégorie MeSH Diseases, on répond à la question : "Sachant que je parle seulement de maladie, est-ce que ma molécule est significativement associé à cette maladie" Au sens, plus que les autres maladies dont je parle. Genre, parmis toutes les maladies auxquel ma molécule est  associés, qu'elles sont celles qui sont significativement associés.

Le truc c'est que choisir seulement les terme maladie, va grandement me faire diminuer le nombre de publis associés à ma molécule et donc sachant que moins l'on a de publi plus les probabilité associés sont biaisé c'est peut être pas une bonne idée, Genre si j'ai seuelement 3 publi associé à des maladies genre Alzeimer parmis en tout 10000 publis si je considère tout les topics et que je choisis de ne m'intéressés qu'aux maladies vont test va dire est que que en tirant 3 publis c'est significatifs de tirer 3 publis associés à Alzeimer, il va surement me dire oui alors qu'en vrai bof ....


" Pour faire mes vues de Sub-Network, j'ai :
(1) Sélectinner fait un fitlre sur les métabolites de ma signature (p-value <= 0.0001)
(2) J'ai sélectionner tout les réactions dans lesquels ils étaient impliqué et j'ai ré-initialiser le filtre la dessus
(3) J'ai uniquement sélectionner les métabolites du Cytosol
(4) J'ai remove les side-compounds
(5) J'ai remove des réactions de transports ou de Biomass

* * * 

J'ai aussi lu la publi sur Annotation Enrichment Analysis: *An Alternative method for Evaluating the Functional Properties of Gene Sets* qui parle des biais que l'on peut trouver dans les analyses de types Go-Enrichments (donc un peu similaire à notre metab2mesh) en utilisant le test de Fisher. Ils montrent qu'il y a un biais dans la significativité des résultats due au fait que la distribution du nombre d'annotation GO-termes au niveau des gènes est très inégale et non-homogène, voir proche d'une power-law. En effet, certains  gènes vont être très bien annotés et auront ainsi énormément de termes Go annotés. En revanche, certains gène, peu annotés auront peu de termes GO annotés. On peut également voir la même chose, moins importante certes, sur les termes ou la distribution de gènes associés à un terme GO varie énormément. Pour des GO-termes qui sont proches des racinces c'est normal car ils comptabilise l'ensemble des annotations de leur enfants, en revanche, le nombre d'enfant variant énormément, certains termes Go ont néanmoins beaucoup plus de gènes associés que les autres.
Il en retourne par exemple que les tests qui sont réalisés à partir de set de gènes qui présente beaucoup plus d'annotations que les autres sont souvent facilement significatifs. En effet, cedrtains gènes étant annotés avec énormément de termes GO, il vont avoir tendance à augmenter de manière non-spécifique finalement toutes les co-occurences et donc augmenter la significitvité des tests
Dans notre cas cela reviendrai a dire que les publications qui ont beaucoup de termes MeSH annotés ont tendance à rendre les test plus facilement significatifs. Dans notre cas ce biais n'est pas présent puisque contrairement au gènes globalement toutes les publi on en moyenne une dizaine de publication, aucune publi n'a par exemple 300 MeSh associés.

Pour solutionner ce problème leur solution est non pas de compter l'overlap de gènes entre le set et le termes Go, mais de compter le nombre d'annotations communes entre le set de gènes et le le terme GO et ensuite en rendomisant de voir si ceci est significatif. Donc:
	- Le set d'annotations associé au set de gène c'est l'union de tout les termes GO associés au set.
	- Le set d'annotations associé au terme c'est l'ensemble de tout les termes GO enfant associé à ce terme, ils parlent de la branche associé au terme
  Ainsi on compte les annotations communes entre notre set et le terme GO
  Ensuite, on va shuffle à la fois gènes et les termes GO, pour obtenir:
	- Un set de gènes qui contient ~ le même nombre d'annotation que le set d'orgine
	- Un set de termes MeSH qui à ~ le même nombre d'annotation que la branche d'origine

Ensuite pour chaque des shuffeling crée on va compter le nombre de cooc d'annotation et ensuite c'est donc du monte-Carlo, on compte combien de fois de manière aléatoire on a obtenu un score de co-occurence plus élevé
La chose à retenir est que le Test Exact de Fisher est basé sur la loi hypergéométrique. Ainsi pour tester la significativité d'une association il cherche à calculer la probabilité de tirer au hazard un set de gène équivalent à celui observé, c a d qui présente k gènes appartenant au GO-terme X connaissant le nombre de gènes associé au GO-terme X. Ainsi, lorsqu'il fait son tirage, il considère que la probabilité de tirer au hazard chaque gène est equiprobable, or dans ce cas là c'est faux !!!! En effet, certains gènes étant annotés avec beaucoup plus de termes GO que les autres, il est beaucoup plus probable quand j'étudie un GO-terme de tirer un gène qui est très fortement annotés (annotés dans beaucoup de GO-termes), qu'un gène très mal annotés qui a par exemple seulement 2 GO-termes annotés.
Y'a un peu une srote d'effet lampadaire dans la construction des bases par rapport aux gènes souvent étudiés (ex: cancer, etc ...)
Ainsi en comptant les annotation communes et en randomisant pour estimer la pvalue on s'absous de ça :)

Et dans notre cas cela reviendrait à considérer que l'on a une grosse différence dans les nombre de MeSH associés à nos publications et que donc certaines publication serait plus probable d'être tirer de manière aléatorie car elles ont beaucpoup de MeSH annotés, or ce n'est pas le cas globalement toutes les publications ont en ~ un dizaine de MeSH

que les gènes associés aux sets comparés (ceux de la signature et ceux associé au termes MeSH) sont 



# ON A CHANGE LA MANIERE DE FAIRE LA PROPAGATION :  GROS FIX

On a modifier la manière dont on faisait la propagation dans la hiérarchie qui était en fait erronée. Pour la nouvelle manièe de faire on s'est appuyer sur l'article *Transforming the Medical Subject Headings into Linked Data: Creating the Authorized Version of MeSH in RDF* et sur la page *https://hhs.github.io/meshrdf/tree-numbers*. 
On passe désormais par les treeNumber/parentTreeNumber+ pour récuprer les ancêtres car en fait dans la documentation du MeSH RDF il s'avère que broaderDescriptor n'est **pas** une relation transitives et que donc on utilisait des mauvais chemins dans la propagation, ils sont notamment l'exemple parlant de Eye Brown (les sourcils) qui peut être considéré comme un organe des sens si on utilise brodaerDescriptor due à la mauvaise utilisation de la transitité. Or la propriété parentTreeNumber est bien fait pour être transitive.
Aussi cela permet de simplifier les requêtes puisque l'on a plus besoin de propager dans les ancêtre pour les CID ou pour compter les individus. En effet, en utilisant broaderDescriptor on pouvait parfois obtenir des ancêtres qui n'était pas dans l'arbre d'origine du terme et donc initialement on pouvait avoir des publications pour lesquelles les termes MeSh n'appartenait pas aux branches considérés, mais, en propageant aux ancêtres, certains pouvait appartenir aux arbres, toujours due à la mauvaise propagation. Maintenant avec le tree Number on a plus ce problème . En effet, tout les ancêtres d'un termes seront sur les même branche que celles définis par les TreeNumber du termes MeSH (Cf. ex EyeBrown) et donc seulement avec le(s) treeNumber(s) su terme, on peut direct savoir si il appartient lui et ces ancêtres à nos branches ou non.


## Pour les termes Obsolètes.
Il semblerait que certains termes soit devenu obsolete et que donc leur position dans la hierarchie MeSH ne doit plus être pris en compte. Il ne faut donc plus prendre en comptes les termes MeSh obsolètes car il ne sont plus utilisé et ce sont des termes que l'on ne peut pas retrouver sur le MeSH browser, en fait, il existe encore uniquemnt dans le MeSH RDF où ils sont annotés comme obsolètes.
MAIS, il faut faire très attention aux publications qui ont directement un terme obsolète annoté car en propageant certains de ces anciens ancêtres sont toujours actifs, or il n'est plus juste de propager depuis ces éléments car leur position dans la hierarchie a été discrédité. Il faut donc vérifier si les termes initiaux sont actifs, avant de propager dans la hiérarchie, et en propageant dans la hierarchie, ne propager qu'a des éléments encore actifs.
En effet on pourrait imager le cas où une publi serait annoté avec uniquement un terme MeSH obsolete, on ne prendrait pas en compte donc dans le corpus de la molécule, en revanche en utilisant la propagation aux ancêtres si certains sont actifs, on la prendrait en coocurences et on retournerait aux même problème qu'avant l'utilisation des tree-number où le corpus des molécules pourrait être plus petit que certaines coocurences.

Ainsi: 
- avant de propager on sélectionne uniquement les MeSH actifs !
- en propage, on ne propage qu'aux termes actifs

ATTENTION: même si le tree-number possède une propriété obsolete, le terme peut être obsolete et le tree-Number non car il aura été remplacé !!!

## Pour le refactoring de SBML upgrade :

J'ai donc changé les associations *skos:exactMatch* en *owl:sameAs* car avec la nouvelle release de MetaNetX, j'ai vue que finalement ce que j'avais mis en place n'était pas super au point :/
En fait je pouvais aller chercher les synonymes d'uris inférés MAIS on ne pouvais pas aller chercher des uris inférés à partir de synonymes de ce que l'on avait annoté dans la base. Or on pourrait très bien imaginer une ressource qui présente des associations en utilisant des uris synonymes de celles annotés dans le SBML ce qui fait que l'on aurait pas pu faire directement le lien et inférés de nouvelles uris par cette ressource.
Là où ça devenait problématique c'est que maintenant les uris identifiers.org dans MetaNetX ne sont plus les même que celle dans le SBML, alors même si on les écrivait ensuite dans les fichiers en utilisant les uris identifiers.org du SBML, ce n'était pas opti :/ 

Pour être précis: ça fonctionne car lorsque je crée les graph d'équivalence skos:closeMatch, j'utilise comme uri pattern la première uri de la propriété ressources_uris de ma table table_info qui est toujours l'uri de identifier.org et il s'agit donc de l'uri qui est utilisé dans le SMBL ! Mais en utilsant owl:sameAs, maintenant :
- On gère aussi les identifiants inférés depuis des synonymes de ceux annotés dans le SBML
- Tout les synonymes sont implicites pas besoin de les instancier ! :D
Donc c'est mieux ! :)

J'ai donc opter pour un changementet j'ai choisit de remplacer *skos:exactMatch* par *owl:sameAs*
Le super avantage de owl:sameAs c'est que Virtuoso le maitrise en activant la règle: *DEFINE input:same-as "yes"* Alors, **toutes** les uris qui sont liés par le prédicats sameAs sont considéré comme identiques dans les requêtes. Ainsi, si tout les synonymes sont considéré comme le "même individu*, toutes les associations les annotations sont partagés entre les synonymes. Ainsi, le liens entre ces synonymes devient implicite dans le graph de connaissance. Deplus, si il est implicite, il n'y a pas besoin de le rajouter et l'on peut supprimer les graph synonymes et infered_uris_synonyms ! On a donc seulement à exporter les équivalences inter-uris que l'on peut faire, et le tour est joué ! :)

Pareil pour les annotations structurelle, plus besoin de chercher à vérifier l'uris utilisé pour que ce soit la bonne, vue que les synonymes partagent les annotations, cela marche également pour les inchi et les SMILES !


## Pour ClassyFire et la récupération des classes associés aux identifiants :
On avait en tout 373765 identifiants PubChem avec de la litterature pour lesquels on disposai d'une InchiKey, soit quasiment tous !

Parmi eux, on a pu récupérer 316.087 CID pour lesquels on a eu direc-parent dans la classification ChemOnt et 315.336 pour lesquels on a également pu trouver un alternative-parent ! Cela représente en gros plus de 84%

## Pour faire l'enrichissment à partir de l'ontology ChemOnt: 
 - On va utiliser l'entité racine comme source: Chemical entities (CHEMONTID:9999999)
 - D'arpès mes premiers test, on utilisant seulement les classes Chebi avec plus de 1 CID associés **ET** moins de 1000, on va pouvoir étudié 271 classes chemont