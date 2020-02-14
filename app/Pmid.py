class Pmid:
    """This class represent Pubmed publication, on la définit avec: 
    - A Pubmed PMID identifier
    - a list of sources for the CID - PMID association
    """
    def __init__(self, pmid, source):
        self.cid = pmid
        self.source = source