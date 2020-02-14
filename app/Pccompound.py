from Pmid import Pmid
class Pccompound:
    """This class represent PubChem compounds, on la définit avec: 
    - a PubChem compound CID identifier 
    - a list of associated PMID: pccompound_pubmed, pccompound_pubmed_mesh, pccompound_pubmed_publisher
    """
    def __init__(self, cid, pmids, pmids_sources):
        self.cid = cid
        self.pmid_list = [Pmid(pmids[i], pmids_sources[i]) for i in range(len(pmids))]
    
    # Getters
    def get_cid(self):
        return(self.cid)
