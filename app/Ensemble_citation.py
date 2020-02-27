import gzip
import numpy
from pathlib import Path
from Citation import Citation
import xml.etree.ElementTree as ET

class Ensemble_citation:
    """This class represent an ensembl of PubMed citations descripted in a XML format. This class is composed with :
    - input_file: a XML PubMed citation file as name *pubmed20n0001*
    - xml_citations: an xml.etree.ElementTree object from the input_file"""
    def __init__(self):
        self.input_file = None
        self.xml_citations = None
    
    def open_xml(self, input_file):
        """Function used to open an pubmed.xml.gz file, and transformed it as an xml.etree.ElementTree object.
        - input_file: path to the Pubmed XML file"""
        f = gzip.open(input_file)
        self.input_file = Path(input_file).stem
        self.xml_citations = ET.parse(f)
    
    def extract_pmids(self, pmid_list):
        """The goal of the function is to extract Pubmed_Citation XML Element that have corresponding PMIDs is the pmid_list, and after extraction, to remove extracted pmids from the pmid_list
        - pmid_list: the list of pmids"""
        # Get all pmids
        xml_pmids = [pmid_citation.text for pmid_citation in self.xml_citations.findall("./PubmedArticle/MedlineCitation/PMID")]
        # Test if there is some pmids is the XML file that are also in the pmid_list
        pmid_intersect = list(set(xml_pmids) & set(pmid_list))
        if len(pmid_intersect) == 0:
            return None
        # If there is some, get XML associated elements index in XML tree for intersect pmids
        matching_index = numpy.array(numpy.isin(xml_pmids, pmid_intersect)).nonzero()
        # Extract associated XML element
        all_citations = self.xml_citations.findall("./PubmedArticle/MedlineCitation")
        selected_xml_citations = [Citation(all_citations[index]) for index in matching_index[0].tolist()]
        # Check if all intersect pmids have an extracted XML element:
        selected_xml_citations_pmids = [tt.get_pmid() for tt in selected_xml_citations]
        print("Check if all intersect pmids have an extracted XML element : " + str(set(selected_xml_citations_pmids) == set(pmid_intersect)))
        # Remove catched elements from the pmid list : 
        for viewed_pmid in pmid_intersect:
            pmid_list.remove(viewed_pmid)
        
        return selected_xml_citations
