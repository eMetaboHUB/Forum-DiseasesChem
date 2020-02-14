from Pmid import Pmid
class Pccompound:
    """This class represent PubChem compounds, on la définit avec: 
    - son identifiant CID
    - une liste de PMID associés
    """
    def __init__(self, cid, pmids, pmids_sources):
        self.cid = cid
        self.pmid_list = [Pmid(pmids[i], pmids_sources[i]) for i in range(len(pmids))]
