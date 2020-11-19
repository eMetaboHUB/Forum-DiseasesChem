import os, time, rdflib, sys, subprocess
from rdflib.namespace import XSD, DCTERMS, VOID
import ftplib
from dateutil import parser
import glob
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version

def download_pubChem(dir, request_ressource, out_path, out_log):
    """
    This function is used to download PubChem rdf files from the ftp server and create a new version of the associated ressource.
    - dir: the path to the directory/file to fetch in the ftp server from ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/
    - request_ressource: the name of the ressource as indicated in the void.ttl file.
    - out_path: a path to a directory to write output files.
    The function return the version created and the uri of this new version. in case of errors during wget downloading, errors are printed in dl_pubchem_*.log
    """
    # Intialyze .log files
    with open(out_log + "dl_pubchem_" + request_ressource + ".log", "wb") as f_log:
        pass
    # On télécharge le fichier void et les données
    print("Trying to check last available version of PubChem RDF on ftp ...")
    # Connect ftp server to check void.ttl last modification date
    try:
        ftp = ftplib.FTP("ftp.ncbi.nlm.nih.gov")
        ftp.login()
        pubchem_mdtm = ftp.voidcmd("MDTM /pubchem/RDF/void.ttl")[4:]
        ftp.quit()
    except ftplib.all_errors as ftplib_e:
        print("Errors while trying to connect to NCBI PubChem FTP server at ftp.ncbi.nlm.nih.gov, check dl_pubchem_" + request_ressource + ".log")
        with open(out_log + "dl_pubchem_" + request_ressource + ".log", "ab") as f_log:
            f_log.write("\n" + str(ftplib_e) + "\n")
        sys.exit(3)
    # Parse data to create pubchem version
    pubchem_last_v = parser.parse(pubchem_mdtm)
    pubchem_last_v = pubchem_last_v.strftime('%Y-%m-%d')
    print("Last PubChem " + request_ressource + "RDF version found on ftp server is : " + pubchem_last_v)
    print("Check if PubChem " + request_ressource + " RDF version " + pubchem_last_v + " was already download ...")
    # From last version date, if associated void.ttl file already exists, exit and return pubchem last version and associated uri
    test_r_info = glob.glob(out_path + request_ressource + "/" + pubchem_last_v + "/" + "void.ttl")
    if len(test_r_info) == 1:
        print("PubChem " + request_ressource + " RDF version " + pubchem_last_v + " is already downloaded, end.\n\n")
        ressource_version = Database_ressource_version(ressource = "PubChem/" + request_ressource, version = pubchem_last_v)
        return pubchem_last_v, str(ressource_version.uri_version)
    else:
        print("Trying to dowload PubChem " + request_ressource + " RDF version " + pubchem_last_v + "\n\n")
    # Download PubChem data
    print("Trying to dowload PubChem void.ttl file ...", end = '')
    # Create output directory for requested ressource and last available version
    version_path = out_path + request_ressource + "/" + pubchem_last_v + "/"
    if not os.path.exists(version_path):
        os.makedirs(version_path)
    try:
        subprocess.run("wget -P " + version_path + " ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/void.ttl", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to download PubChem void.ttl file, check dl_pubchem_" + request_ressource + ".log")
        print(e)
        with open(out_log + "dl_pubchem_" + request_ressource + ".log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to read Pubchem void.ttl file ...", end = '')
    # On parse le fichier des metadatas
    g_metadata = rdflib.Graph()
    g_metadata.parse(version_path + "void.ttl", format='turtle')
    try:
        subprocess.run("rm " + version_path + "void.ttl", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to remove PubChem void.ttl file, check dl_pubchem_" + request_ressource + ".log")
        print(e)
        with open(out_log + "dl_pubchem_" + request_ressource + ".log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to dowload Pubchem " + dir + " directory ...", end = '')
    # On récupère les données que l'on enregistre dans le directory créée
    try:
        subprocess.run("wget -r -A ttl.gz -nH" + " -P " + version_path + " --cut-dirs=5 " + "ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/" + dir, shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to dowload PubChem " + dir + " directory, check dl_pubchem_" + request_ressource + ".log")
        print(e)
        with open(out_log + "dl_pubchem_" + request_ressource + ".log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to build Pubchem " + request_ressource + " new ressource version ...", end = '')
    # On récupère la description en metadata du répertoire téléchargé  pour créer le graph qui sera associé à la ressource
    ressource_version = Database_ressource_version(ressource = "PubChem/" + request_ressource, version = pubchem_last_v)
    ressource_version.version_graph.namespace_manager = g_metadata.namespace_manager
    # On annote la nouvelle version avec les informations du fichier void
    for s,p,o in g_metadata.triples((rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/void.ttl#" + request_ressource), None, None)):
        if p == VOID['dataDump'] and not str(o).startswith("ftp://ftp.ncbi.nlm.nih.gov/pubchem/RDF/" + dir):
            continue
        ressource_version.add_version_attribute(predicate = p, object = o)
    # On écrit le graph le fichier
    ressource_version.version_graph.serialize(version_path + "void.ttl", format = 'turtle')
    print("Ok\nEnd !")
    return ressource_version.version, str(ressource_version.uri_version)

def download_MeSH(out_dir, namespaces_dict, out_log):
    """
    This function is used to download the last version of the MeSH RDF from NIH ftp server, the void.ttl file is also use to bring metadata information about the dowloaded version.
    But contrary to PubChem the modification date is not include in the void.ttl file. So, version is determine from the modification date of the file.
    Ressource is named 'MeSHRDF' as indicate in the void.ttl
    - out_dir: a path to an directory to write output files
    - namespace_list: a list of the namespaces that should be associated to the graph
    The function return the version and the uri of this new version.
    """
    # Intialyze .log files
    with open(out_log + "dl_mesh.log", "wb") as f_log:
        pass
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    print("Trying to check last available version of MeSH RDF on ftp ...")
    # Connect ftp server to check mesh.nt last modification date
    try:
        ftp = ftplib.FTP("ftp.nlm.nih.gov")
        ftp.login()
        mesh_mdtm = ftp.voidcmd("MDTM /online/mesh/rdf/mesh.nt")[4:]
        ftp.quit()
    except ftplib.all_errors as ftplib_e:
        print("Errors while trying to connect to NCBI mesh FTP server at ftp.nlm.nih.gov, check dl_mesh.log")
        with open(out_log + "dl_mesh.log", "a") as f_log:
            f_log.write("\n" + str(ftplib_e) + "\n")
        sys.exit(3)
    # parse date to get last version
    mesh_last_v = parser.parse(mesh_mdtm)
    mesh_last_v = mesh_last_v.strftime('%Y-%m-%d')
    print("Last MeSH RDF version found on ftp server is : " + mesh_last_v)
    print("Check if MeSH RDF version " + mesh_last_v + " was already download ...")
    test_r_info = glob.glob(out_dir + mesh_last_v + "/" + "void.ttl")
    # From last version date, if associated void.ttl file already exists, exit and return mesh last version and associated uri
    if len(test_r_info) == 1:
        print("MeSH RDF version " + mesh_last_v + " is already downloaded, end.\n\n")
        ressource_version = Database_ressource_version(ressource = "MeSHRDF", version = mesh_last_v)
        return mesh_last_v, str(ressource_version.uri_version)
    else:
        print("Trying to dowload MeSH RDF version " + mesh_last_v + "\n\n")
    # Create version output directory
    out_path = out_dir + mesh_last_v + "/"
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    # Download MeSh data
    try:
        subprocess.run("wget -P " + out_path + " ftp://ftp.nlm.nih.gov/online/mesh/rdf/void_1.0.0.ttl", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to download MeSH void.ttl file, check dl_mesh.log")
        print(e)
        with open(out_log + "dl_mesh.log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Trying to read MeSH void.ttl file ...", end = '')
    g_metadata = rdflib.Graph()
    g_metadata.parse(out_path + "void_1.0.0.ttl", format = 'turtle')
    print("Ok\nTrying to dowload MeSH RDF file ...", end = '')
    # Download MeSH RDF
    try:
        subprocess.run("wget -P " + out_path + " ftp://ftp.nlm.nih.gov/online/mesh/rdf/mesh.nt", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to download MeSH mesh.nt file, check dl_mesh.log")
        print(e)
        with open(out_log + "dl_mesh.log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nTrying to parse MeSH original metadata ...", end = '')
    # On crée la nouvelle ressource MeSH
    ressource_version = Database_ressource_version(ressource = "MeSHRDF", version = mesh_last_v)
    ressource_version.version_graph.namespace_manager = g_metadata.namespace_manager
    for s,p,o in g_metadata.triples((rdflib.URIRef("http://id.nlm.nih.gov/mesh/void#MeSHRDF"), None, None)):
        # L'attribut creation dans le void correspond à la date de création originale du fichier soir courant 2014, noous souhaitant que la date de création de notre ressource correspondent à la date de modification du fichier
        if (p == VOID['dataDump']):
            if str(o) == "ftp://ftp.nlm.nih.gov/online/mesh/rdf/mesh.nt":
                ressource_version.add_version_attribute(predicate = p, object = o)
            else:
                continue
        elif (p != DCTERMS["created"]):
            ressource_version.add_version_attribute(predicate = p, object = o)
        else:
            continue
    # On crée le graph de données : 
    print("Ok\nTrying to create MeSH new ressource version ...", end = '')
    mesh_graph = ressource_version.create_data_graph([], None)
    mesh_graph.parse(out_path + "mesh.nt", format = "nt")
    ressource_version.add_version_attribute(namespaces_dict["void"]["triples"], rdflib.Literal( len(mesh_graph), datatype=XSD.long ))
    ressource_version.add_version_attribute(namespaces_dict["void"]["distinctSubjects"], rdflib.Literal( len(set([str(s) for s in mesh_graph.subjects()])), datatype=XSD.long ))
    # Clear graph
    mesh_graph = None
    # On écrit le graph de la ressource
    ressource_version.version_graph.serialize(out_path + "void.ttl", format = 'turtle')
    # On supprime le fichier void initial
    try:
        subprocess.run("rm " + out_path + "void_1.0.0.ttl ", shell = True, check=True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to remove file, check dl_mesh.log")
        print(e)
        with open(out_log + "dl_mesh.log", "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok\nEnd")
    return ressource_version.version, str(ressource_version.uri_version)