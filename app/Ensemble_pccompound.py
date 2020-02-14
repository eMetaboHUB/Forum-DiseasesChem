from Pccompound import Pccompound
class Ensemble_pccompound:
    """This class represent an ensembl of Pccompound objects, it's composed of:
    - a list of cid
    - a size attribute
    - a corresponding list of Pccompound objects
    """
    def __init__(self, pccompound_list):
        self.pccompound_list = pccompound_list        
        self.size = len(pccompound_list)
    
    def export_cids_pmids_triples_ttl(self, output_file):
        # Preparing file and writing prefix
        f = open(output_file, "w")
        f.write("@prefix cito:\t<http://purl.org/spar/cito/> .\n@prefix compound:\t<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/> .\n@prefix reference:\t<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> .\n")
        # for (pcc in pccompound_list):
        for pcc in self.pccompound_list:
            pmid_export = " ,\n\t\t".join(["reference:PMID"+pmid for pmid in pcc.get_pmids()]) + " .\n"
            pmid_export = "compound:CID" + pcc.get_cid() + "\tcito:isDiscussedBy\t" + pmid_export
            f.write(pmid_export)
        f.close