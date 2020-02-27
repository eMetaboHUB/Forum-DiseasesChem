# Importing packages
# Using Package eutils 0.6.0
import eutils
import gzip
import io
from pathlib import Path
import os
from Ensemble_pccompound import Ensemble_pccompound
from Ensemble_citation import Ensemble_citation

# The Api_key can be found on the NCBI account.


# Now we must create a function that takes this union list are try to write all PubMed citation associatied elements
# Fonction qui va surement servir a rien .. lol mdr 
# def fetch_mesh(pmids_list, pubmed_citation_folder):
#    """A function to fetch MeSh terms associated to PMID for a PMID list and using a folder that contains all the PubMed XML files
#    - pmids_list: a list of PMIDs
#    - pubmed_citation_folder: a path to the folder that contains all the pubmed XML files"""
#    # List all files in folder
#    xml_citation_files = os.listdir(pubmed_citation_folder)
#    n_file = len(xml_citation_files)
#    # intialiaze lis_Ensemble_citation
#    list_Ensemble_citation = [Ensemble_citation() for i in range(n_file)]
#    # For each file, send path to folder + file name to the list_Ensemble_citation object. 
#    index = 0
#    while ((index < n_file) or (len(pmids_list) == 0)):
#        list_Ensemble_citation[index].open_xml((pubmed_citation_folder + xml_citation_files[index]))
#        print("Exploring file: " + list_Ensemble_citation[index].input_file + "...")
#        # Passing to next file
#        index += 1

apiKey = "0ddb3479f5079f21272578dc6e040278a508"
# Building requests
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)

new_Ensemble_pccompound = Ensemble_pccompound()
new_Ensemble_pccompound.append_pccompound("25203768", query_builder)
new_Ensemble_pccompound.append_pccompound("6036", query_builder)
new_Ensemble_pccompound.append_pccompound("11355423", query_builder)
# new_Ensemble_pccompound.append_pccompound("11355423", query_builder)
new_Ensemble_pccompound.export_cids_pmids_triples_ttl("test3.txt")

new_Ensemble_pccompound.export_cid_pmid_endpoint("test_endpoint.txt")

all_pmids = new_Ensemble_pccompound.get_all_pmids()

# fetch_mesh(test, "data/PubMed_MEDLINE/")
# ensbl_cit_test = Ensemble_citation()
# ensbl_cit_test.open_xml("data/PubMed_MEDLINE/pubmed20n0001.xml.gz")
# print(len(test))
# a = ensbl_cit_test.extract_pmids(test)
# print(len(test))



# A partir de ma liste de tout les pmids dont j'ai besoin je vais chercher à filtrer les fichier RDF References de PubChem.
def parse_pubchem_RDF(PubChem_ref_folfer, all_pmids, out_dir):
    """A function to parse the .ttl.gz PubChem Reference RDf files to only extract line for which PMIDs are associated to CID
    - PubChem_ref_folfer: The folder where are all the PubChem Reference RDf files
    - the list of all pmids from an Ensemble_pccompound object get_all_pmids() 
    """
    # Test if output directory exist:  
    if not  os.path.exists(out_dir):
        os.mkdir(out_dir)
        print("Directory " + out_dir + " Created !")
    else:
        print("Directory " + out_dir + " already exists")
    # Convert pmids list in a set, because the test 'in' will be more efficient
    set_all_pmids = set(["reference:PMID" + pmid for pmid in all_pmids])
    RDF_ref_files = os.listdir(PubChem_ref_folfer)
    # On parcours tout les fichiers:
    for f_input in RDF_ref_files:
        print("Treating " + f_input + " ...")
        # On parse le nom du fichier pour récupérer la racine et on créée le fichier de sortie :
        f_output_name = f_input.split(".ttl.gz")[0] + "_fitlered.ttl.gz"
        f_output = gzip.open(out_dir + f_output_name, "wt")
        f = gzip.open(PubChem_ref_folfer + f_input,'rt')
        # On initialise le boolean a Flase
        bool = False
        # Pour chaque ligne, on parse
        for line in f:
            columns = line.split(sep='\t')
            # Si la ligne désigne un triplet (et pas sa suite lorsque l'on a plusieurs objets en turtle )
            if columns[0] != '':
                # Si le pmid appartient à notre liste, on passe bool à True de tel sorte que les ligne suivante soient ajouter au fichier tant qu'un triplet avec un pmid qui n'appartient pas à notre liste est rencontré
                if columns[0] in set_all_pmids:
                    bool = True
                else:
                    bool = False
            # Si bool est True, on print la ligne
            if bool:
                f_output.write(line)
            



parse_pubchem_RDF("data/PubChem_References/reference/", all_pmids, "filtered_tll/")
