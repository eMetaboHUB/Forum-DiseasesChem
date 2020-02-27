import xml.etree.ElementTree as ET

class Citation:
    """This class represent a PubMed citation
    - pmid: the PMID of the associated PubMed citation
    """
    
    def __init__(self, xml_citation_element):
        self.pmid = xml_citation_element.find("./MedlineCitation/PMID").text
        self.pub_date = None
        self.bibliographic_citation = self.create_bibliographic_citation(xml_citation_element)
    
    def create_bibliographic_citation(self, xml_citation_element):
        bib_citation = xml_citation_element.find("./MedlineCitation/Article/Journal/Title").text + '.' 
        # For the date: all publication does not have the same annotation. Some have only Years, otheres Years and Month, Years Month and Days, si we choose to iteratve voer all the childs of PubDate
        for date_info in xml_citation_element.find("./MedlineCitation/Article/Journal/JournalIssue/PubDate").getchildren():
            bib_citation += ' ' + date_info.text
        bib_citation += ';'
        # As indicate in the Mesline doc: "Some records contain <Issue> but lack <Volume>; some records contain <Volume> but lack <Issue>; and some records contain Volume and Issue data in the Volume element.", so:
        if not xml_citation_element.find("./MedlineCitation/Article/Journal/JournalIssue/Volume") is None:
            bib_citation += xml_citation_element.find("./MedlineCitation/Article/Journal/JournalIssue/Volume").text
        if not xml_citation_element.find("./MedlineCitation/Article/Journal/JournalIssue/Issue") is None:
            bib_citation +=  '(' + xml_citation_element.find("./MedlineCitation/Article/Journal/JournalIssue/Issue").text + ')'
        bib_citation += xml_citation_element.find("./MedlineCitation/Article/Pagination/MedlinePgn").text + '.'
        return(bib_citation)
    
    def get_pmid(self):
        return(self.pmid)