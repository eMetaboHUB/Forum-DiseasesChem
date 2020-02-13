class Pmid:
    """This class represent Pubmed publication, on la définit avec: 
    - son identifiant pmid
    - une liste de MeSH associés
    """
    def __init__(self, pmid, source):
        self.cid = pmid
        self.source = source