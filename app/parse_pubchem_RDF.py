
import gzip
import rdflib
import os, time
from Database_ressource_version import Database_ressource_version
from rdflib.namespace import XSD, DCTERMS

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
    subjects = set()
    n_triples = 0
    path_out = out_dir + filtered_ressource_name + "/" + ressource_filtered_version.version + "/"
    if not os.path.exists(path_out):
        os.makedirs(path_out)
    # Les différents fichiers sont les subjects annotés avec le isPartOf vers la ressource cible. 
    for file_name in os.listdir(input_ressource_directory) :
        # On utilise None pour vider la mémoire associér à la variable
        file_content = None
        file_content = str()
        base_name = file_name.split(".")[0]
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
            current_graph = ressource_filtered_version.create_data_graph(namespace_list  = [], namespace_dict = None)
            current_graph.parse(data = file_content, format = 'turtle')
            n_triples += len(current_graph)
            subjects = subjects.union(set([str(s) for s in current_graph.subjects()]))
            ressource_filtered_version.add_DataDump(base_name + "_filtered" + ".trig")
            current_graph.serialize(destination = path_out + base_name + "_filtered" + ".trig", format='trig')
            # On vide le graph
            current_graph = None
    # On ajoute les infos :
    ressource_filtered_version.add_version_namespaces(["void"], namespace_dict)
    ressource_filtered_version.add_version_attribute(DCTERMS["description"], rdflib.Literal(str(g_ressource.value(subject=input_ressource_uri, predicate=DCTERMS["description"], object=None)) + " - Filtered version", lang = "en" ))
    ressource_filtered_version.add_version_attribute(DCTERMS["title"], rdflib.Literal(str(g_ressource.value(subject=input_ressource_uri, predicate=DCTERMS["title"], object=None)) + " - Filtered version", lang = "en" ))
    ressource_filtered_version.add_version_attribute(namespace_dict["void"]["triples"], rdflib.Literal(n_triples, datatype=XSD.long ))
    ressource_filtered_version.add_version_attribute(namespace_dict["void"]["distinctSubjects"], rdflib.Literal(len(subjects), datatype=XSD.long ))
    ressource_filtered_version.add_version_attribute(DCTERMS["source"], input_ressource_uri)
    ressource_filtered_version.add_version_attribute(DCTERMS["source"], input_ids_uri)
    # On écrit
    ressource_filtered_version.version_graph.serialize(destination=path_out + "ressource_info_" + filtered_ressource_name + "_" + ressource_filtered_version.version + ".ttl", format = 'turtle')
