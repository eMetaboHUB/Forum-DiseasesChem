# Importing packages
# Using Package eutils 0.6.0
import eutils
import gzip
import rdflib
import requests
import io
from datetime import date
import time
import re
from rdflib.namespace import XSD, DCTERMS
from pathlib import Path
import os
from Ensemble_pccompound import Ensemble_pccompound
from Ensemble_citation import Ensemble_citation
from Database_ressource_version import Database_ressource_version



# The Api_key can be found on the NCBI account.

namespaces = {
    "cito": rdflib.Namespace("http://purl.org/spar/cito/"),
    "compound": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"),
    "reference": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/reference/"),
    "endpoint":	rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/"),
    "obo": rdflib.Namespace("http://purl.obolibrary.org/obo/"),
    "dcterms": rdflib.Namespace("http://purl.org/dc/terms/"),
    "fabio": rdflib.Namespace("http://purl.org/spar/fabio/"),
    "mesh": rdflib.Namespace("http://id.nlm.nih.gov/mesh/"),
    "void": rdflib.Namespace("http://rdfs.org/ns/void#")
}

apiKey = "0ddb3479f5079f21272578dc6e040278a508"
# Building requests
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)

new_Ensemble_pccompound = Ensemble_pccompound()
new_Ensemble_pccompound.append_pccompound("11355423", query_builder)
new_Ensemble_pccompound.append_pccompound("6036", query_builder)

new_Ensemble_pccompound.create_CID_PMID_ressource(namespaces, "data/", None)

all_pmids = new_Ensemble_pccompound.get_all_pmids()
all_cids = new_Ensemble_pccompound.get_all_cids()



# A partir de ma liste de tout les pmids dont j'ai besoin je vais chercher à filtrer les fichier RDF References de PubChem.
def parse_pubchem_RDF(input_ressource_directory, all_ids, prefix, input_ressource_file, input_ressource_uri, out_dir, filtered_ressource_name, input_ids_uri, isZipped, namespace_dict, version, separator):
    """A function to parse the .ttl.gz PubChem RDF files to only extract line for which id are associated to ids from list
    - PubChem_ref_folfer: The folder where are all the PubChem  RDF files
    - the list of all ids to fetch in files
    """
    # Convert pmids list in a set, because the test 'in' will be more efficient
    set_all_ids = set([prefix + id for id in all_ids])
    ressource_filtered_version = Database_ressource_version(ressource = filtered_ressource_name, version = version)
    # On récupère le graph RDF qui décrit avec ses métadatas la ressource à filtrer
    g_ressource = rdflib.Graph()
    g_ressource.parse(input_ressource_file, format='turtle')
    # Les différents fichiers sont les subjects annotés avec le isPartOf vers la ressource cible. 
    for s,p,o in g_ressource.triples((None, DCTERMS['isPartOf'], input_ressource_uri)):
        file_content = str()
        file_name = str(g_ressource.value(subject = s, predicate = DCTERMS['source'], object=None))
        base_name = file_name.split(".")[0]
        file_out = base_name + "_filtered.trig"
        if isZipped:
            f_input = gzip.open(input_ressource_directory + file_name,'rt')
        else:
            f_input = open(input_ressource_directory + file_name,'r')
        print("Treating " + file_name + " ...")
        # Il va falloir récupérer les namespaces: 
        l_h  = f_input.readline()
        while l_h.startswith('@', 0, 1):
            file_content += l_h
            l_h = f_input.readline()
        # On initialise le boolean a Flase
        bool = False
        # Pour chaque ligne, on parse
        for line in f_input:
            columns = line.split(sep=separator)
            # Si la ligne désigne un triplet le début d'un triplet
            if columns[0] != '':
                # Si le pmid appartient à notre liste, on passe bool à True de tel sorte que les ligne suivante soient ajouter au fichier tant qu'un triplet avec un pmid qui n'appartient pas à notre liste est rencontré
                if columns[0] in set_all_ids:
                    bool = True
                else:
                    bool = False
            # Si bool est True, on print la ligne
            if bool:
                file_content += line
        f_input.close()
        # On créée alors le nouveau graph: Pas besoin de spécifier des namespace car ce seront les même que dans le fichier source
        ressource_filtered_version.append_data_graph(file = file_out, namespace_list  = [], namespace_dict = None)
        ressource_filtered_version.data_graph_dict[base_name + "_filtered"].parse(data = file_content, format = 'turtle')
    # On ajoute les infos :
    ressource_filtered_version.add_version_namespaces(["void"], namespace_dict)
    ressource_filtered_version.add_version_attribute(DCTERMS["description"], rdflib.Literal(str(g_ressource.value(subject=input_ressource_uri, predicate=DCTERMS["description"], object=None)) + " - Filtered version", lang = "en" ))
    ressource_filtered_version.add_version_attribute(DCTERMS["title"], rdflib.Literal(str(g_ressource.value(subject=input_ressource_uri, predicate=DCTERMS["title"], object=None)) + " - Filtered version", lang = "en" ))
    ressource_filtered_version.add_version_attribute(namespace_dict["void"]["triples"], rdflib.Literal(sum([len(g) for g in ressource_filtered_version.data_graph_dict.values()]) , datatype=XSD.long ))
    ressource_filtered_version.add_version_attribute(namespace_dict["void"]["distinctSubjects"], rdflib.Literal( len(set([s for g in ressource_filtered_version.data_graph_dict.values() for s in g.subjects()])), datatype=XSD.long ))
    ressource_filtered_version.add_version_attribute(DCTERMS["source"], input_ressource_uri)
    ressource_filtered_version.add_version_attribute(DCTERMS["source"], input_ids_uri)
    # 
    path_out = out_dir + filtered_ressource_name + "/" + ressource_filtered_version.version + "/"
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    ressource_filtered_version.version_graph.serialize(destination=out_dir + filtered_ressource_name + "/" + "ressource_info_" + filtered_ressource_name + "_" + ressource_filtered_version.version + ".ttl", format = 'turtle')
    for f_name, g_data in ressource_filtered_version.data_graph_dict.items():
         g_data.serialize(destination = path_out + f_name + ".trig", format='trig')



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


def add_triples_from_csv(g, lines, namespaces_dict, predicate):
    p_ns = re.split(":", predicate)
    for l_index in range(1, len(lines) - 1):
        parsed_l = re.split("[\",]", lines[l_index])
        g.add((rdflib.URIRef(parsed_l[1]), namespaces_dict[p_ns[0]][p_ns[1]], rdflib.URIRef(parsed_l[4])))


def REST_ful_bulk_download(graph, predicate, out_name, start_offset, out_dir, ressource_name, namespaces_list, namespaces_dict, version):
    """ - graph: The Subject of the triples (c'est pété comme nom mais c'est comme ça qu'ils l'appellent ...)
        - predicate: the predicate of the triple (witrh the prefix in a turtle syntax)
        - out_dir: output directoty to write files
        Vue que l'offset commence à 0, si il y a plusieurs paquets il y en aura 10000 de plus dans le premier
    """
    # On initilialise la table request_failure_list:
    request_failure_list = list()
    offset = start_offset
    pack_rank = 1
    print("Create new ressource")
    ressource_version = Database_ressource_version(ressource = ressource_name, version = version)
    ressource_version.append_data_graph(out_name + "_" + str(pack_rank) + ".ttl.gz", namespaces_list, namespaces_dict)
    print("Creating directoty")
    path_out = out_dir + ressource_name + "/" + ressource_version.version + "/"
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    print("Starting at offset " + str(offset))
    out = request_RESTful_PubChem(graph, predicate, str(offset), request_failure_list)
    # On récupère le dernier élément de la liste en la tronquant, si c'est true, c'est que le fichier à 10002 lignes et qu'on attend encore certainement des résultats.
    is_not_the_last = out.pop()
    # On additionne au graph:
    print("- Add to Graph -")
    add_triples_from_csv(ressource_version.data_graph_dict[out_name + "_" + str(pack_rank)], out, namespaces, predicate)
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
        print("- Add to Graph -")
        add_triples_from_csv(ressource_version.data_graph_dict[out_name + "_" + str(pack_rank)], out, namespaces, predicate)
        # On fait des paquets de 10.000.000 par fichiers
        if (offset % 10000000) == 0:
            print("Creating pack")
            ressource_version.data_graph_dict[out_name + "_" + str(pack_rank)].serialize(destination=path_out + out_name + "_" + str(pack_rank) + ".ttl", format='turtle')
            os.system("gzip " + path_out + out_name + "_" + str(pack_rank) + ".ttl")
            pack_rank += 1
            ressource_version.append_data_graph(out_name + "_" + str(pack_rank) + ".ttl.gz", namespaces_list, namespaces_dict)
        if offset == 100000:
            is_not_the_last = False
    print("End !")
    # Compléter l'annotation de la ressource :
    ressource_version.add_version_namespaces(["void"], namespaces_dict)
    ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providind link between the pmid and the major MeSH associated to the publication"))
    ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal("PMID to Primary Subject Term RDF triples"))
    ressource_version.add_version_attribute(namespaces_dict["void"]["triples"], rdflib.Literal( sum([len(g) for g in ressource_version.data_graph_dict.values()]) , datatype=XSD.long ))
    ressource_version.add_version_attribute(namespaces_dict["void"]["distinctSubjects"], rdflib.Literal( len(set([s for g in ressource_version.data_graph_dict.values() for s in g.subjects()])), datatype=XSD.long ))
    # On écrits les fichiers dans les répertoires correspondants
    ressource_version.data_graph_dict[out_name + "_" + str(pack_rank)].serialize(destination=path_out + out_name + "_" + str(pack_rank) + ".ttl", format='turtle')
    ressource_version.version_graph.serialize(out_dir + ressource_name + "/" + "ressource_info_" + ressource_name + "_" + ressource_version.version + ".ttl", format = 'turtle')
    
    os.system("gzip " + path_out + out_name + "_" + str(pack_rank) + ".ttl")
    return request_failure_list

        
def dowload_pubChem(dir, request_ressource, out_path):
    """
    - request_ressource: one of the void:subset of the PubChem RDF, such as :compound, reference, etc... 
    """
    # On télécharge le fichier void et les données
    os.system("wget ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/void.ttl")
    # On parse le fichier des metadatas
    g_metada = rdflib.Graph()
    g_metada.parse("void.ttl", format='turtle')
    global_modif_date = g_metada.value(subject=rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/void.ttl#PubChemRDF"), predicate=rdflib.URIRef("http://purl.org/dc/terms/modified"), object=None)
    # On crée un repertoire correspondant au subset PubChem récupéré et à la date de récupération
    version_path = out_path + request_ressource + "/" + str(global_modif_date) + "/"
    if not os.path.exists(version_path):
        os.makedirs(version_path)
    os.system("mv void.ttl " + out_path + request_ressource + "/")
    # On récupère les données que l'on enregistre dans le directory créée
    os.system("wget -r -A ttl.gz -nH" + " -P " + version_path + " --cut-dirs=5 " + "ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/" + dir)
    # On récupère la description en metadata du répertoire téléchargé  pour créer le graph qui sera associé à la ressource
    ressource_version = Database_ressource_version(ressource = "PubChem/" + request_ressource, version = str(global_modif_date))
    ressource_version.version_graph.namespace_manager = g_metada.namespace_manager
    # On annote la nouvelle version avec les informations du fichier void
    for s,p,o in g_metada.triples((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/void.ttl#" + request_ressource), None, None)):
        ressource_version.add_version_attribute(predicate = p, object = o) 
    for graph_file in os.listdir(version_path):
        # On va crée un URI complémentaire en ajoutant le nom du ichier pour les identifiers
        ressource_version.append_data_graph(graph_file, [], None)
    # On écrit le graph le fichier
    ressource_version.version_graph.serialize(out_path + request_ressource + "/" + "ressource_info_" + request_ressource + "_" + str(global_modif_date) + ".ttl", format = 'turtle')


dowload_pubChem("reference", "reference", "data/PubChem_References/")


requests_failed = REST_ful_bulk_download(graph = 'reference', predicate = 'fabio:hasPrimarySubjectTerm', out_name = 'PrimarySubjectTerm',
                                         start_offset = 0, out_dir = "data/TEST/",
                                         ressource_name = "PrimarySubjectTerm", namespaces_list = ["reference", "fabio", "mesh"],
                                         namespaces_dict = namespaces,
                                         version = None)

# On parse les lignes des fichier RDF .ttl de PubChem pour ne récupérer que les lignes qui impliques des PMIDS que j'ai sélectionner
parse_pubchem_RDF(input_ressource_directory = "data/PubChem_References/reference/2020-03-06/", 
                  all_ids = all_pmids,
                  prefix = "reference:PMID", 
                  out_dir = "data/PubChem_References/",
                  input_ressource_file = "data/PubChem_References/reference/ressource_info_reference_2020-03-06.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/reference/2020-03-06"),
                  filtered_ressource_name = "referenceFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/2020-03-20"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = None,
                  separator = '\t')

# On parse les lignes des fichier RDF .ttl de PubChem pour ne récupérer que les lignes qui impliques des PubChem compound que j'ai sélectionner
parse_pubchem_RDF(input_ressource_directory = "data/PubChem_References/PrimarySubjectTerm/2020-03-20/",
                  all_ids = all_pmids,
                  prefix = "reference:PMID",
                  out_dir = "data/PubChem_References/",
                  input_ressource_file = "data/PubChem_References/PrimarySubjectTerm/ressource_info_PrimarySubjectTerm_2020-03-20.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/PrimarySubjectTerm/2020-03-20"),
                  filtered_ressource_name = "PrimarySubjectTermFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/2020-03-20"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = None,
                  separator = ' ')


dowload_pubChem("compound/general/pc_compound_type.ttl.gz", "compound", "data/PubChem_Compound/")