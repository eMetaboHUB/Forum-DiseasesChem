## Introduction 


- **Big problem in science: Exploiter la litterature scientifique**

	- La litterature scientifique est aujourd'hui la plus grande source de connaissance dans le domaine biomedical avec plus de 30 Million d'articles scientifiques et le nombre d'articles publié par an est en constante augmentation
	- De nombreux outils ont été développé pour extraire la litterature scientifique assoicié à des gènes, des transcrits ou des protéines et en extraire des informations tels que des maladies asociés ou autre (e.g LGscore, Beegle)
	- Il existe néanmoins peu d'outils pour lier des molécules chimiques à leur litterature scientifique


- **Narrower problem: Fédérer et exploiter la connaissance issus de la litterature scientifique associée aux molécules**

	- Les thématiques dominantes retrouvées dans le corpus de publications associé une molécule peuvent ainsi permettre de la caractérisé précisément, d'identifiers des pathologies associés, etc .
	- Ces liens entre molécules et littératures ou concepts représentent également une nouvelle donnée permettant de réaliser d'autres analyses beaucoup plus profondes
	- Plusieurs approches ont déjà été développé comme PolySearch qui utilise une approche de TextMining et metab2mesh (down), dont l'application présenté est inspiré.
	- Pour lier des molécules à leur litératures, les approches de text-mining présentent certaines limites au vue des caractéristiques particlières des articles scientifiques: seul l'abstract présent, les noms de molécules, des synonymes, etc ... 
	- Les approches de text-mining sont efficace pour découvrir de nouvelles relations entre des molécules et des concepts biomédicaux en utilisant par exemple des approches de Topics modeling. Néanmoins, ces relations peuvent se baser sur seulement quelques phrases dans un corpus réduits d'articles, remettant parfois en cause la solifité d'une association. Le noms de certaines molécules ou l'emploi de synonymes pour désigner une même maladie dans la literature scientifiques peut aussi biaiser ces relations, faux positifs etc ...
	- Néanmoins, les pulications scientifiques étant indéxées manuellement avec des termes MeSH par des curateurs, on a une annotation manuelle utilisant un vocabulaire hiérarchisé pour décrire les concepts biomédicaux associés aux publications
	- Contrairement on text-mining, on ne fait pas de Knowledge discovery car on utilise des données labélisées, mais grâce aux tailles grandes tailles de corpus dont on dispose pour représentés nos molécules et nos termes MeSH, on va pouvoir identifiers les concepts biomédicaux les plus associés à une molécule, et inversement dans la littérature scientifique.


- **Yet narrower paper Gap: Lier les molécules à des concepts biomédicaux en utilisant une approche de linked data**
	

	- Comme metab2mesh, le but est d'établir des liens entre des composés chimiques représentés par des entités PubChem et des concepts biomédicaux représenter par des termes MeSh
	- Considéré les relations entre les concepts MeSH ou entre les molécules peut permettre d'enrichir considérablement les associations, ex: des familles de molécules, des catégories de maladies, ...
	- Les outils classique fournissent seulement un "moteur de recherche", il est important d'améliorer accéssibilité et la manipulation des données 
	- Ces deux problématiques vont pouvoir être prise en compte grâce à l'ulilisation des Linked Data 


- **Notre approche:**
	- Qu'est ce que les Linked Data ?
	- Développement d'une base de connaissance des associations molécules - concepts biomédicaux en se basant sur la litterature
	- Utilisation de vocabulaires hiérarchisé (ontologies) pour décrire sémantiques les molécules et les concepts MeSH ainsi que leurs relations
		- Les Ontologies sont un vocabulaires hierarchisé, pas de problèmes de synonymes 
	- Enrichir les associations en propageant les relations de concepts précis vers des concepts plus généraux grâce aux relations décrites dans les ontologies.
	- Faciliter l'accessibilité et la manipulation des données grâce au SPARQL endpoint



## Methods

### Squelette de la Knowledge base:

	- Le graph des Composés (short example)
	- Le graph des Descripteurs (short example) ?? Ajout du graph InchiKeys ??
	- Le graph des Références
	- Les liens entre composés et publications par Elink
	- Exemple de Schéma RDF général

### Les Ontologies

	- MeSH pour définir les concepts biomédicaux
	- CheBI, ClassyFire pour les molécules

### Liens entre molécules et concepts MeSH
	* Déterminer les coocurences entre molécules et Descripteur MeSH :
		-  ?? liens simples ??	
		- Propagation dans l'ontologie MeSh
		- Propagation dans l'ontologie des molécules
	* Test Statistiques
		- ?? *Weakness* des associations ??
		- Analyse des Hot topics ?
	* Implémentation des triplets représentants les associations significatives dans la base
	* Le SPARQL endpoint et le FTP pour manipuler les données
		- Montrer l'interface du endpoint avec requête pré-construites
	* Exemple de l'interface
		- Montrer l'interface de la table de résultat pour une requête particulière
		

## Discussion

- Bilan de la knwoledge base:
	- Combien de composés, MeSh, associations, etc ...

- Discussion sur la propagation dans le Thesarus MeSH:
	- Diagramme de Venn avant après propagation
	- Analyse par arbre
	- ?? Delta de taille de corpus (peut être redondantavec le reste) ??
	- Graph des distribution de taille de corpus MeSH (moins complexe que les contours plots):
		* Les associations gagnés ou perdus sont celles pour lesquelles le corpus a évolué
		* Pas de variations  pour le corpus des composés
		* Exemples concrets d'associations gagnés et perdues en s'appuyant sur le contour plot
			- Eau + Eukaryotes	
			- Oxyfedrine et Myocardial Ischemia (?? ou l'exemple de Metab2MeSH avec l'AMP Cyclic ??)
		* Exemple généraliste: Imidocarb Dipropionate
- Discussion sur la propagation dans le l'ontologie ChEBI/ChemOnt pour les molécules:
	- Expliquer que c'est exactement le même principe (Peut être mettre une Figure en supp.)
	- Montrer un exemple On peut utiliser la Phenyketonurias
- Limite:
	- La propagation peut également apportés des associations peu pertinentes
		Pour des arbres tel que Organisme, la généralisation faite en propageant des concepts les plus précis au concepts les plus généraux est sémantiquement peu fiable, car on est sur une Taxnomy, c'est différent de l'arbre maladie pour lequel on catégorise les maladies en sous-groupes
	- 
- Perspectives	
	- L'approche est entièrement applicables aux gènes et aux protéines.
	- Réaliser des enrichissment personnalisés pour des listes de métabolites


D'autres outils :
Alkemio
Smalheiser
Samlyser
Metab2MeSh
PolySearch
KnetMiner
ConceptMetab (utilisait metab2mesh)


