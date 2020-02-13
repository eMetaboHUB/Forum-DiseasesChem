class Pccompound:
    """This class represent PubChem compounds, on la définit avec: 
    - son identifiant CID
    - une liste de PMID associés
    """
    def __init__(self, cid, pmid_list):
        self.cid = cid
        self.pmid_list = pmid_list
    