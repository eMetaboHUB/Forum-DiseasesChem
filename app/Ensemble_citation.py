import gzip
from pathlib import Path
import xml.etree.ElementTree as ET
class Ensemble_citation:
    """This class represent an ensembl of PubMed citations descripted in a XML format. This class is composed with :
    - input_file: a XML PubMed citation file as name *pubmed20n0001*
    - xml_citations: an xml.etree.ElementTree object from the input_file"""
    def __init__(self):
        self.input_file = None
        self.xml_citations = None
    
    def open_xml(self, input_file):
        """Function used to open an pubmed.xml.gz file, and transformed it as an xml.etree.ElementTree object."""
        f = gzip.open(input_file)
        self.input_file = Path(input_file).stem
        self.xml_citations = ET.parse(f)