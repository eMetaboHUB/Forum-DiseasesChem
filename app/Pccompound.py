from Pmid import Pmid
class Pccompound:
    """This class represent PubChem compounds, on la définit avec: 
    - a PubChem compound CID identifier 
    - a list of associated PMID: pccompound_pubmed, pccompound_pubmed_mesh, pccompound_pubmed_publisher
    """
    def __init__(self, cid, pmids, pmids_sources):
        self.cid = cid
        self.pmid_list = [Pmid(pmids[i], pmids_sources[i]) for i in range(len(pmids))]
    
    def get_pmids(self):
        """Return a list of all pmids associated in the Pccompound object"""
        return([Pmid.get_pmid(pmid) for pmid in self.pmid_list])
    
    def get_cid(self):
        """Return the PubChem Compound Identifier"""
        return(self.cid)