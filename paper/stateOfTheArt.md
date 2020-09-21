#State of the art
----------------------------------------------
Pionneer work of Swanson : arrowsmith
----------------------------------------------
##Polysearch

#justification
>"Keeping pace with the rapidly growing body of biomedi- cal literature is proving to be almost impossible."

#method

#validation

----------------------------------------------
##Metab2Mesh
----------------------------------------------
##Alkemio

#justification
>"Mining millions of available citations to search reported associations between chemicals and topics of interest would require substantial human time"

#method
naïve Bayesian classifier that models biases in word usage in a set of PubMed citations related to a topic of interest.

use chemical mesh annotations to retrieve compounds

goal : rank compounds. Can't go from compounds to mesh

#validation
vs facta et polysearch
----------------------------------------------

CoPub
EBIMed
CiteXplore
GoPubMed


based on small number of articles, often one phrase in one article, thus prone to spurrious association.  
[Example: Polyvidone and Covid-19 is, at the time of writting, the only retrieved association between the disease and a human metabolite. It is solely based on the folowing sentence:"Novel coronavirus disease (COVID-19) outbreak: Now is the time to refresh pandemic plans" from [], because "refresh" is listed as a synonym of Polyvidone, since it belongs in the composition of a commercial collyr product nammed "Refresh". In fact, as we write those words, we may also makes things worst by strenghtening the association bewteen the two concepts, which examplify the volatility of such associations.] However, we argue that such errors are of little harm, since polysearch and other TM tools are easilly reviewed, and a quick read would easilly dismiss any misleading associations. TM associations are designed for in-depth analaysis and serendipitous discovery, and wouldn't be advised for large scale analaysis such as inference from knowledge networks. Thus, we believe that both approaches, while aiming at different goals, are complementary. TM could be of importnant help for grasping the nature of an association behind a broad 'topic confluence'. 