# Importing packages
# Using Package eutils 0.6.0
import eutils
import gzip
import requests
import io
import time
import re
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
new_Ensemble_pccompound.append_pccompound("11355423", query_builder)
new_Ensemble_pccompound.append_pccompound("6036", query_builder)

new_Ensemble_pccompound.export_cids_pmids_triples_ttl("cid_to_pmids.ttl")

new_Ensemble_pccompound.export_cid_pmid_endpoint("cid_to_pmids_endpoint.ttl")

all_pmids = new_Ensemble_pccompound.get_all_pmids()
all_cids = new_Ensemble_pccompound.get_all_cids()

# fetch_mesh(test, "data/PubMed_MEDLINE/")
# ensbl_cit_test = Ensemble_citation()
# ensbl_cit_test.open_xml("data/PubMed_MEDLINE/pubmed20n0001.xml.gz")
# print(len(test))
# a = ensbl_cit_test.extract_pmids(test)
# print(len(test))



# A partir de ma liste de tout les pmids dont j'ai besoin je vais chercher à filtrer les fichier RDF References de PubChem.
def parse_pubchem_RDF(PubChem_ref_folfer, all_ids, prefix, out_dir):
    """A function to parse the .ttl.gz PubChem RDF files to only extract line for which id are associated to ids from list
    - PubChem_ref_folfer: The folder where are all the PubChem  RDF files
    - the list of all ids to fetch in files
    """
    # Test if output directory exist:  
    if not  os.path.exists(out_dir):
        os.mkdir(out_dir)
        print("Directory " + out_dir + " Created !")
    else:
        print("Directory " + out_dir + " already exists")
    # Convert pmids list in a set, because the test 'in' will be more efficient
    set_all_ids = set([prefix + id for id in all_ids])
    RDF_ref_files = os.listdir(PubChem_ref_folfer)
    # On parcours tout les fichiers:
    for f_input in RDF_ref_files:
        print("Treating " + f_input + " ...")
        # On parse le nom du fichier pour récupérer la racine et on créée le fichier de sortie :
        f_output_name = f_input.split(".ttl.gz")[0] + "_fitlered.ttl.gz"
        f_output = gzip.open(out_dir + f_output_name, "wt")
        f = gzip.open(PubChem_ref_folfer + f_input,'rt')
        # Il va falloir récupérer les Headers: 
        l_h  = f.readline()
        while l_h.startswith('@', 0, 1):
            f_output.write(l_h)
            l_h = f.readline()
        # On initialise le boolean a Flase
        bool = False
        # Pour chaque ligne, on parse
        for line in f:
            columns = line.split(sep='\t')
            # Si la ligne désigne un triplet (et pas sa suite lorsque l'on a plusieurs objets en turtle )
            if columns[0] != '':
                # Si le pmid appartient à notre liste, on passe bool à True de tel sorte que les ligne suivante soient ajouter au fichier tant qu'un triplet avec un pmid qui n'appartient pas à notre liste est rencontré
                if columns[0] in set_all_ids:
                    bool = True
                else:
                    bool = False
            # Si bool est True, on print la ligne
            if bool:
                f_output.write(line)
            
# Cette fonction à pour but de lancer une requête vers le REST de PubChem et de récupérer le résultat en csv et de l'écire en turtle
def request_RESTful_PubChem(graph, predicate, offset, request_failure_list):
    """ This function send a request to PubChem RESTful serveur and get a response in a csv format and then return the lines in the results as a list, with the last element a boolean that indicated if this result is the last expected
        - graph: The Subject of the triples
        - predicate: the predicate of the triple (witrh the prefix in a turtle syntax)
        - offset: the current offset to fetch
        - request_failure_list: In case os the request raise an Exception (HTTP status > 200) the associated offset will be added to the request_failure_list
        If the number of printed lines in less than 10002 it indicates that we have reached the end because the maximal number of recors is 10000
        Doc at https://pubchemdocs.ncbi.nlm.nih.gov/rdf$_5-2
    """
    # On crée la structure de la requête
    request_base = "https://pubchem.ncbi.nlm.nih.gov/rest/rdf/query?graph=" + graph + "&pred=" + predicate + "&offset=" + offset + "&format=csv"
    try:
        # On lance la requête. Si le statut HTTP de la requête raise est > 200, cela déclenche une exception, on ajoute l'offset_concerné dans la table
        r = requests.get(request_base)
        r.raise_for_status()
    except requests.exceptions.HTTPError as fail_request:
        print("There was an error during the request, with predicate = " + predicate + ", graph = " + graph + ", and offset = " + offset + "\n.The fail request Error was " + str(fail_request) + "\n")
        print("The associated offset " + offset + " is added to the request_failure_list\n")
        request_failure_list.append(offset)
        # Si la requête échoue on renvoie juste un bool True (la liste tronqué du dernier élément étant alors vide, le fichier rempli sera vide également) pour que la fonction continue jusqu'au dernier resultat, on ajoute l'offset à la liste des fails.
        return [True]
    # On récupère le résultat de la requête ligne par line
    lines = str.splitlines(r.text)
    # On append en fin de liste un boolean indiquant s'il s'agit du dernier resultat attendu de la requête. Si le nombre de ligne == 10002 (1 ligne de header + 10000 resultats max + 1 ligne vide)
    lines.append((len(lines) == 10002))
    return lines



def write_in_turtle_syntax(out_dir, graph, predicate, offset, lines, prefix_1, index_1, prefix_2, index_2):
    """ Function to write request results from PubChem RESTful in a turtle syntax
        - out_dir: output directoty to write the file
        - graph: The Subject of the triples
        - predicate: the predicate of the triple (witrh the prefix in a turtle syntax)
        - offset: the current offset to fetch
        - lines: request results, parsed line by line
        - prefix_1: prefix of the Subject of the triples
        - index_1: index of the subject in the splited line
        - prefix_2: prefix of the Object of the triples
        - index_2: index of the Object in the splited line
    """
    f = open( (out_dir + graph + "_" + predicate + "_" + offset + ".ttl"), 'w')
    # On lie par ligne pour formater en turtle: 
    for l_index in range(1, len(lines) - 1):
        parsed_l = re.split("[\"/,]", lines[l_index])
        f.write(prefix_1 + parsed_l[index_1] + "\t" + predicate + "\t" + prefix_2 + parsed_l[index_2] + " .\n")
    f.close()




def REST_ful_bulk_download(graph, predicate, out_dir, start_offset):
    """ - graph: The Subject of the triples
        - predicate: the predicate of the triple (witrh the prefix in a turtle syntax)
        - out_dir: output directoty to write files
    """
    # Test if output directory exist:  
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
        print("Directory " + out_dir + " Created !")
    else:
        print("Directory " + out_dir + " already exists")
    # On initilialise la table request_failure_list:
    request_failure_list = list()
    offset = start_offset
    print("Starting at offset " + str(offset))
    out = request_RESTful_PubChem(graph, predicate, str(offset), request_failure_list)
    # On récupère le dernier élément de la liste en la tronquant, si c'est true, c'est que le fichier à 10002 lignes et qu'on attend encore certainement des résultats.
    is_not_the_last = out.pop()
    # On envoie à la fonction qui va écrire tout àa en turtle. Il faudrait modifier ça si on veut changer de type (exemple récupérer le titre ou bien écrire en xml, etc ...)
    write_in_turtle_syntax(out_dir, graph, predicate, str(offset), out, 'reference:', 6, 'mesh:', 13)
    while(is_not_the_last):
        offset += 10000
        print("offset: " + str(offset))
        out = request_RESTful_PubChem(graph, predicate, str(offset), request_failure_list)
        is_not_the_last = out.pop()
        # If it appears that this results seems to be the last, we check three more time that we can not catch 10000 triples, if we can't, it's the last one
        if not is_not_the_last:
            print("Starting Check !")
            i = 0
            # We check three times, if is_not_the_last become True, we exist the loop and continue with the next offset or if we reach the last check (the third) and it's always the last, so it's the end 
            while (not is_not_the_last) and i < 5:
                out = request_RESTful_PubChem(graph, predicate, str(offset), request_failure_list)
                is_not_the_last = out.pop()
                i +=1
        write_in_turtle_syntax(out_dir, graph, predicate, str(offset), out, 'reference:', 6, 'mesh:', 13)
    print("End !")
    return request_failure_list

        
requests_failed = REST_ful_bulk_download(graph = 'reference', predicate = 'fabio:hasPrimarySubjectTerm', out_dir = 'data/PubChem_PrimarySubjectTermsTriples/', start_offset = 3430000)

# On parse les lignes des fichier RDF .ttl de PubChem pour ne récupérer que les lignes qui impliques des PMIDS que j'ai sélectionner
parse_pubchem_RDF("data/PubChem_References/reference/", all_pmids, "reference:PMID", "pccompound_references_filtered/")

# On parse les lignes des fichier RDF .ttl de PubChem pour ne récupérer que les lignes qui impliques des PubChem compound que j'ai sélectionner
parse_pubchem_RDF("data/PubChem_compound/", all_cids, "compound:CID", "pccompound_filered/")

print("coucou5")
