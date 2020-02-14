class Pmid:
    """This class represent Pubmed publication, on la définit avec: 
    - A Pubmed PMID identifier
    - a list of sources for the CID - PMID association
    """
    def __init__(self, pmid, source):
        self.pmid = pmid
        self.source = source
    
    # Getters
    def get_pmid(self):
        """Return the Pubmed Identifier"""
        return(self.pmid)