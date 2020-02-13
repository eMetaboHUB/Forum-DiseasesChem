from Pmid import Pmid
class Pccompound:
    """This class represent PubChem compounds, on la définit avec: 
    - son identifiant CID
    - une liste de PMID associés
    """
    def __init__(self, cid, n_pmid):
        self.cid = cid
        self.pmid_list = [Pmid("", "") for i in range(n_pmid)]