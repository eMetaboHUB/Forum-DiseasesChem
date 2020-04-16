

import requests
import os, time
import re
import rdflib
from Database_ressource_version import Database_ressource_version
from rdflib.namespace import XSD, DCTERMS

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
    subjects = set()
    n_triples = 0
    print("Create new ressource")
    ressource_version = Database_ressource_version(ressource = ressource_name, version = version)
    current_graph = ressource_version.create_data_graph(namespaces_list, namespaces_dict)
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
    add_triples_from_csv(current_graph, out, namespaces_dict, predicate)
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
        add_triples_from_csv(current_graph, out, namespaces_dict, predicate)
        # On fait des paquets de 10.000.000 par fichiers
        if (offset % 10000000) == 0:
            print("Creating pack")
            ressource_version.add_DataDump(out_name + "_" + str(pack_rank) + ".ttl")
            current_graph.serialize(destination=path_out + out_name + "_" + str(pack_rank) + ".ttl", format='turtle')
            # On ajoute les stats de nombre de sujets et triplets : 
            n_triples += len(current_graph)
            subjects = subjects.union(set([str(s) for s in current_graph.subjects()]))
            # On clean la mémoire associé au graph maintenant qu'il est écrit
            current_graph = None
            os.system("gzip " + path_out + out_name + "_" + str(pack_rank) + ".ttl")
            pack_rank += 1
            current_graph = ressource_version.create_data_graph(namespaces_list, namespaces_dict)
    print("End !")
    # On fait pour le dernier graph
    ressource_version.add_DataDump(out_name + "_" + str(pack_rank) + ".ttl")
    current_graph.serialize(destination=path_out + out_name + "_" + str(pack_rank) + ".ttl", format='turtle')
    os.system("gzip " + path_out + out_name + "_" + str(pack_rank) + ".ttl")
    n_triples += len(current_graph)
    subjects = subjects.union(set([str(s) for s in current_graph.subjects()]))
    current_graph = None
    # Compléter l'annotation de la ressource :
    ressource_version.add_version_namespaces(["void"], namespaces_dict)
    ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providind link between the pmid and the major MeSH associated to the publication"))
    ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal("PMID to Primary Subject Term RDF triples"))
    ressource_version.add_version_attribute(namespaces_dict["void"]["triples"], rdflib.Literal(n_triples , datatype=XSD.long ))
    ressource_version.add_version_attribute(namespaces_dict["void"]["distinctSubjects"], rdflib.Literal(len(subjects) , datatype=XSD.long ))
    # On écrits les fichiers dans les répertoires correspondants
    ressource_version.version_graph.serialize(out_dir + ressource_name + "/" + "ressource_info_" + ressource_name + "_" + ressource_version.version + ".ttl", format = 'turtle')
    
    return request_failure_list