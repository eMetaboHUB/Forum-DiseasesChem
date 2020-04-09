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
import os, time
from Ensemble_pccompound import Ensemble_pccompound
from Ensemble_citation import Ensemble_citation
from Database_ressource_version import Database_ressource_version



# The Api_key can be found on the NCBI account.
# Creating the directory of all namespaces
namespaces = {
    "cito": rdflib.Namespace("http://purl.org/spar/cito/"),
    "compound": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"),
    "reference": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/reference/"),
    "endpoint":	rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/"),
    "obo": rdflib.Namespace("http://purl.obolibrary.org/obo/"),
    "dcterms": rdflib.Namespace("http://purl.org/dc/terms/"),
    "fabio": rdflib.Namespace("http://purl.org/spar/fabio/"),
    "mesh": rdflib.Namespace("http://id.nlm.nih.gov/mesh/"),
    "void": rdflib.Namespace("http://rdfs.org/ns/void#"),
    "skos": rdflib.Namespace("http://www.w3.org/2004/02/skos/core")
}

# Listes des features Compounds - Descriptors que l'on souhaite récupérées : 
feature_list = ["_Canonical_SMILES",
"_Covalent_Unit_Count",
"_Defined_Atom_Stereo_Count",
"_Defined_Bond_Stereo_Count",
"_Exact_Mass",
"_Hydrogen_Bond_Acceptor_Count",
"_Hydrogen_Bond_Donor_Count",
"_IUPAC_InChI",
"_Isomeric_SMILES",
"_Isotope_Atom_Count",
"_Molecular_Formula",
"_Molecular_Weight",
"_Mono_Isotopic_Weight",
"_Non-hydrogen_Atom_Count",
"_Preferred_IUPAC_Name",
"_Rotatable_Bond_Count",
"_Structure_Complexity",
"_TPSA",
"_Total_Formal_Charge",
"_Undefined_Atom_Stereo_Count",
"_Undefined_Bond_Stereo_Count",
"_XLogP3-AA"]


def merge_SMBL_and_annot_graphs(path_to_SMBL_RDF, list_annot_graph, path_to_annot_graph):
    """
    This function is used to build a conjuctive graph with rdflib, merging triples from the original SBML graph and triples from annotations graphs
    - path_to_SMBL_RDF: a path to the SMBL graph (.ttl)
    - a list of annotation graph files that have to be loaded
    - a path to the directory containing annotation graphs
    """
    sbml = rdflib.ConjunctiveGraph()
    sbml.parse(path_to_SMBL_RDF, format='turtle')
    for annot_graph in list_annot_graph:
        sbml.parse(path_to_annot_graph + annot_graph, format='trig')
    return(sbml)

def extract_ids_from_SMBL_by_URI_prefix(smbl_graph, uri_prefix):
    """
    This function is used to request a sbml graph in sparl to extract all identifiers that match a prefix URI.
    - the sbml_graph, a rdflib.Graph object
    - uri_prefix: the URI prefix
    """
    # On va chercher tout les id avec une requête sparql qui correspondent à ce prefix :
    query = smbl_graph.query(
        """
        select distinct (strafter(STR(?ref),\"""" + uri_prefix + """\") as ?id)
        where {
            ?species a SBMLrdf:Species .
            ?species bqbiol:is ?ref .
            FILTER(STRSTARTS(STR(?ref), \"""" + uri_prefix + """\"))
            }
        """)
    # On récupère et formate correctement la liste d'ids
    id_list = [id[0].toPython() for id in query]
    return(id_list)

def create_Ensemble_pccompound_from_SMBL(smbl_graph, query_builder):
    """
    This function is used to build an Ensemble_pccompound from CID identifiers presents in the sbml graph, by first extracting all CID from PubChem URIs.
    - smbl_graph: the sbml Graph
    - a query_builder
    """
    cid_list = extract_ids_from_SMBL_by_URI_prefix(smbl_graph, "http://identifiers.org/pubchem.compound/")
    # On crée l'object Ensemble_pccompound
    print(len(cid_list))
    new_Ensemble_pccompound = Ensemble_pccompound()
    # Pour chaque cid, on va chercher ses références en utilsiant la fonction append_pccompound.
    for cid in cid_list:
        print("Appening " + cid + " ...")
        new_Ensemble_pccompound.append_pccompound(cid, query_builder)
    print("There was " + str(len(new_Ensemble_pccompound.append_failure)) + " cid for which there was no publication found !")
    return(new_Ensemble_pccompound)



# A partir de ma liste de tout les pmids dont j'ai besoin je vais chercher à filtrer les fichier RDF References de PubChem.
def parse_pubchem_RDF(input_ressource_directory, all_ids, prefix, input_ressource_file, input_ressource_uri, out_dir, filtered_ressource_name, input_ids_uri, isZipped, namespace_dict, version, separator):
    """A function used to create a filtered version of a ressource, by parsing the reference file and extract only triples for which the subject is contains in a defined set.
    Files are not lood as graph using rdflib, but are read as normal files because for heavy files, importing the graph is not memory efficient.
    - input_ressource_directory: a path to the directory containing all the RDF files referenced has 'partOf' the reference source in the input_ressource_file
    - input_ressource_file: a ressource_info file containing informations about the reference ressource.
    - all_ids: a list of all the ids that should be used to parse the RDF files associated to the ressource.
    - prefix: the string representing the prefix that shoud be added to the id to create the URI of subjects in the file.
    - input_ressource_uri: the rdflib.UriRef associated to the reference ressource in the input_ressource_file
    - out_dir: a path to an directory to write output files.
    - filtered_ressource_name: the name of the new ressource, creating from the parsing of the reference file.
    - input_ids_uri: the rdflib.UriRef associated to the reference ressource from which the set of all_ids was created.
    - isZipped: is the reference files are zipped: True/False.
    - namespace_dict: dict containing all the used namespaces.
    - version: the version name. If None, the date will be choose by default.
    - separator: the separator used in triples (.ttl) files to separated subject/predicate/object: \t or ' '
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
        # On initialise le boolean a False
        bool = False
        # Un second simplement pour tester si au moins 1 élément a été récupérer et s'il faut donc créer un graph 
        g_bool = False
        # Pour chaque ligne, on parse
        for line in f_input:
            columns = line.split(sep=separator)
            # Si la ligne désigne un triplet le début d'un triplet
            if columns[0] != '':
                # Si le pmid appartient à notre liste, on passe bool à True de tel sorte que les ligne suivante soient ajouter au fichier tant qu'un triplet avec un pmid qui n'appartient pas à notre liste est rencontré
                if columns[0] in set_all_ids:
                    bool = True
                    g_bool = True
                else:
                    bool = False
            # Si bool est True, on print la ligne
            if bool:
                file_content += line
        f_input.close()
        # if the obtained graph is empty, it's removed !
        if g_bool:
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
    # On écrit
    path_out = out_dir + filtered_ressource_name + "/" + ressource_filtered_version.version + "/"
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    ressource_filtered_version.version_graph.serialize(destination=path_out + "ressource_info_" + filtered_ressource_name + "_" + ressource_filtered_version.version + ".ttl", format = 'turtle')
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
    """
    This function is used to add triples to a graph g from a csv file
    - g: the graph where to add triples
    - lines: the list of lines of the csv file
    - namespace_dict: dict containing all the used namespaces.
    - predicate: the string of the predicate which is used in the csv file (prefix:predicate)
    """
    p_ns = re.split(":", predicate)
    for l_index in range(1, len(lines) - 1):
        parsed_l = re.split("[\",]", lines[l_index])
        g.add((rdflib.URIRef(parsed_l[1]), namespaces_dict[p_ns[0]][p_ns[1]], rdflib.URIRef(parsed_l[4])))


def REST_ful_bulk_download(graph, predicate, out_name, start_offset, out_dir, ressource_name, namespaces_list, namespaces_dict, version):
    """ This function is used to create a new version of a ressource for which triples are fetch using rhe PubChem REST api using the subject database and the predicate.
    - graph: the subject database of the triples to fetch from the REST api of PubChem.
    - predicate: the predicate of the triple (with the prefix in a turtle syntax)
    - out_name: the name of output RDF file
    - start_offset: the offset used to start (Cf. PubChem REST api doc)
    - out_dir: a path to an directory to write output files
    - ressource_name: the name of the created ressource
    - namespace_list: a list of the namespaces that should be associated to the graph
    - namespace_dict: a dict containing all the used namespaces.
    - version: the version name. If None, the date will be choose by default.
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
            while (not is_not_the_last) and i < 10:
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
    This function is used to download PubChem rdf files from the ftp server and create a new version of the associated ressource.
    - dir: the path to the directory/file to fetch in the ftp server from ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/
    - request_ressource: the name of the ressource as indicated in the void.ttl file.
    - out_path: a path to a directory to write output files
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
    os.system("mv void.ttl " + out_path)
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

def dowload_MeSH(out_dir, namespaces_dict):
    """
    This function is used to download the last version of the MeSH RDF from NIH ftp server, the void.ttl file is also use to bring metadata information about the dowloaded version.
    But contrary to PubChem the modification date is not include in the void.ttl file, so version should be added by the user.
    Ressource is named 'MeSHRDF' as indicate in the void.ttl
    - out_dir: a path to an directory to write output files
    - namespace_list: a list of the namespaces that should be associated to the graph
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    # On télécharge le fichier void et les données
    os.system("wget -P " + out_dir + " ftp://ftp.nlm.nih.gov/online/mesh/rdf/void_1.0.0.ttl ")
    g_metada = rdflib.Graph()
    g_metada.parse(out_dir + "void_1.0.0.ttl", format = 'turtle')
    # téléchargement du MeSH RDF
    os.system("wget -P " + out_dir + " ftp://ftp.nlm.nih.gov/online/mesh/rdf/mesh.nt")
    # On récupère la date de modification
    version = time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(out_dir + "mesh.nt")))
    out_path = out_dir + version + "/"
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    # On déplace les fichiers aux endroits correspondant à la version
    os.system("rm " + out_dir + "void_1.0.0.ttl ")
    os.system("mv " + out_dir + "mesh.nt " + out_path + "mesh.nt")
    # On crée la nouvelle ressource MeSH
    ressource_version = Database_ressource_version(ressource = "MeSHRDF", version = version)
    ressource_version.version_graph.namespace_manager = g_metada.namespace_manager
    for s,p,o in g_metada.triples((rdflib.URIRef("http://id.nlm.nih.gov/mesh/void#MeSHRDF"), None, None)):
        # L'attribut creation dans le void correspond à la date de création originale du fichier soir courant 2014, noous souhaitant que la date de création de notre ressource correspondent à la date de modification du fichier
        if p != DCTERMS["created"]:
            ressource_version.add_version_attribute(predicate = p, object = o)
    # On crée le graph de données : 
    ressource_version.append_data_graph("mesh.trig", [], None)
    ressource_version.data_graph_dict["mesh"].bind("mesh", rdflib.Namespace("http://id.nlm.nih.gov/mesh/"))
    ressource_version.data_graph_dict["mesh"].parse(out_path + "mesh.nt", format = "nt")
    ressource_version.data_graph_dict["mesh"].serialize(destination = out_path + "mesh.trig", format='trig')
    ressource_version.add_version_attribute(namespaces_dict["void"]["triples"], rdflib.Literal( len(ressource_version.data_graph_dict["mesh"]), datatype=XSD.long ))
    ressource_version.add_version_attribute(namespaces_dict["void"]["distinctSubjects"], rdflib.Literal( len(set([str(s) for s in ressource_version.data_graph_dict["mesh"].subjects()])), datatype=XSD.long ))
    # On écrit le graph de la ressource 
    ressource_version.version_graph.serialize(out_dir + "ressource_info_MeSHRDF" + "_" + version + ".ttl", format = 'turtle')



# TODO: Créer la fonction de parsing de graph pour les PubChem compounds (si besoin) afin de ne récupérer que les propriété qui nous interressent. On pourrait le faire en utilisant une sélection de type CHEMINF que celles-ci doivent avoir.
# TODO: Créer une fonction qui permettrait de filtrer les objets. Par exemple la propriété Stereoisomer a pour objets une ensemble de CID, mais tout ces CID ne sont pas présents dans notre graph, car par exemple tous n'appartiennent pas au réseau. les filtrer ?



apiKey = "0ddb3479f5079f21272578dc6e040278a508"
# Building requests
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)
# On crée le graph SBML mergé :
smbl_graph = merge_SMBL_and_annot_graphs("data/HumanGEM/HumanGEM.ttl", ["synonyms.trig", "infered_uris.trig", "infered_uris_synonyms.trig"], "data/annot_graphs/2020-04-06/")
# On fetch les pmids à partir des cid du SMBL !! :
sbml_cid_pmid = create_Ensemble_pccompound_from_SMBL(smbl_graph, query_builder)
# "synonyms.trig", "infered_uris.trig", "infered_uris_synonyms.trig" , "data/annot_graphs/2020-04-06/"
sbml_all_pmids = sbml_cid_pmid.get_all_pmids()
# When we want to filter the PubChem Compound RDF we must use all the CID, even if they failed to append litterature !!
sbml_all_cids = sbml_cid_pmid.get_all_cids() + sbml_cid_pmid.append_failure
# Create Graph
sbml_cid_pmid.create_CID_PMID_ressource(namespaces, "data/", "SMBL_2020-04-06")
smbl_compound_ids_features_list = [id + f for id in sbml_all_cids for f in feature_list]



dowload_MeSH("data/MeSH/", namespaces)

dowload_pubChem("reference", "reference", "data/PubChem_References/")

dowload_pubChem("compound/general/pc_compound_type.ttl.gz", "compound", "data/PubChem_Compound/")
dowload_pubChem("compound/general", "compound", "/media/mxdelmas/DisqueDur/data_max/PubChem_Compound/")
dowload_pubChem("descriptor/compound", "descriptor", "/media/mxdelmas/DisqueDur/data_max/PubChem_Compound/")


requests_failed = REST_ful_bulk_download(graph = 'reference', predicate = 'fabio:hasPrimarySubjectTerm', out_name = 'PrimarySubjectTerm',
                                         start_offset = 0, out_dir = "data/PubChem_References/",
                                         ressource_name = "PrimarySubjectTerm", namespaces_list = ["reference", "fabio", "mesh"],
                                         namespaces_dict = namespaces,
                                         version = None)





### ==== WITH SBML FILE ==== ###



parse_pubchem_RDF(input_ressource_directory = "data/PubChem_References/reference/2020-03-06/", 
                  all_ids = sbml_all_pmids,
                  prefix = "reference:PMID", 
                  out_dir = "data/PubChem_References/",
                  input_ressource_file = "data/PubChem_References/reference/ressource_info_reference_2020-03-06.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/reference/2020-03-06"),
                  filtered_ressource_name = "referenceFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/SMBL_2020-04-06"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = "SMBL_2020-04-06",
                  separator = '\t')

parse_pubchem_RDF(input_ressource_directory = "data/PubChem_References/PrimarySubjectTerm/2020-03-20/",
                  all_ids = sbml_all_pmids,
                  prefix = "reference:PMID",
                  out_dir = "data/PubChem_References/",
                  input_ressource_file = "data/PubChem_References/PrimarySubjectTerm/ressource_info_PrimarySubjectTerm_2020-03-20.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PrimarySubjectTerm/2020-03-20"),
                  filtered_ressource_name = "PrimarySubjectTermFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/SMBL_2020-04-06"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = "SMBL_2020-04-06",
                  separator = ' ')

parse_pubchem_RDF(input_ressource_directory = "/media/mxdelmas/DisqueDur/data_max/PubChem_Compound/compound/2020-03-06/",
                  all_ids = sbml_all_cids,
                  prefix = "compound:CID",
                  out_dir = "data/PubChem_Compound/",
                  input_ressource_file = "/media/mxdelmas/DisqueDur/data_max/PubChem_Compound/compound/ressource_info_compound_2020-03-06.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/compound/2020-03-06"),
                  filtered_ressource_name = "CompoundFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/SMBL_2020-04-06"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = "SMBL_2020-04-06",
                  separator = '\t')

parse_pubchem_RDF(input_ressource_directory = "/media/mxdelmas/DisqueDur/data_max/PubChem_Descriptor/descriptor/2020-03-06/",
                  all_ids = smbl_compound_ids_features_list,
                  prefix = "descriptor:CID",
                  out_dir = "data/PubChem_Descriptor/",
                  input_ressource_file = "/media/mxdelmas/DisqueDur/data_max/PubChem_Descriptor/descriptor/ressource_info_descriptor_2020-03-06.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/descriptor/2020-03-06"),
                  filtered_ressource_name = "DescriptorFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/SMBL_2020-04-06"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = "SMBL_2020-04-06",
                  separator = '\t')