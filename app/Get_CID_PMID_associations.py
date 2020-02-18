# Importing packages
# Using Package eutils 0.6.0
import eutils
import os
from Ensemble_pccompound import Ensemble_pccompound
from Ensemble_citation import Ensemble_citation

# The Api_key can be found on the NCBI account.
apiKey = "0ddb3479f5079f21272578dc6e040278a508"
# Building requests
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)

# Now we must create a function that takes this union list are try to write all PubMed citation associatied elements

def fetch_mesh(pmids_list, pubmed_citation_folder):
    """A function to fetch MeSh terms associated to PMID for a PMID list and using a folder that contains all the PubMed XML files
    - pmids_list: a list of PMIDs
    - pubmed_citation_folder: a path to the folder that contains all the pubmed XML files"""
    # List all files in folder
    xml_citation_files = os.listdir(pubmed_citation_folder)
    n_file = len(xml_citation_files)
    # intialiaze lis_Ensemble_citation
    list_Ensemble_citation = [Ensemble_citation() for i in range(n_file)]
    # For each file, send path to folder + file name to the list_Ensemble_citation object. 
    index = 0
    while ((index < n_file) or (len(pmids_list) == 0)):
        list_Ensemble_citation[index].open_xml((pubmed_citation_folder + xml_citation_files[index]))
        print("Exploring file: " + list_Ensemble_citation[index].input_file + "...")

        # Passing to next file
        index += 1



new_Ensemble_pccompound = Ensemble_pccompound()
new_Ensemble_pccompound.append_pccompound("25203768", query_builder)
new_Ensemble_pccompound.append_pccompound("6036", query_builder)
new_Ensemble_pccompound.append_pccompound("11355423", query_builder)
new_Ensemble_pccompound.export_cids_pmids_triples_ttl("test3.txt")

new_Ensemble_pccompound.export_cid_pmid_endpoint("test_endpoint.txt")

test = new_Ensemble_pccompound.get_all_pmids()

# fetch_mesh(test, "data/PubMed_MEDLINE/")
ensbl_cit_test = Ensemble_citation()
ensbl_cit_test.open_xml("data/PubMed_MEDLINE/pubmed20n0001.xml.gz")
print(len(test))
a = ensbl_cit_test.extract_pmids(test)
print(len(test))