import xml.etree.ElementTree as ET

class Citation:
    """This class represent a PubMed citation
    - pmid: the PMID of the associated PubMed citation
    """
    
    def __init__(self, xml_citation_element):
        self.pmid = xml_citation_element.find("./PMID").text
    
    def get_pmid(self):
        return(self.pmid)