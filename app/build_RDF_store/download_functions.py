import os, time, rdflib, sys, subprocess
from rdflib.namespace import XSD, DCTERMS, RDFS, VOID, RDF
import ftplib
import gzip
from dateutil import parser
import glob
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version

def download_pubChem(dir, request_ressource, pubchem_latest, ftp, void_path, out_path, log):
    """
    This function is used to download PubChem rdf files from the ftp server and create a new version of the associated ressource.
    - dir: the path to the directory/file to fetch in the ftp server 
    - request_ressource: the name of the ressource as indicated in the void.ttl file.
    - out_path: a path to a directory to write output files.
    - out_log: path to log file
    The function return the version created and the uri of this new version. in case of errors during wget downloading, errors are printed in dl_pubchem_*.log
    """

    # Init
    pubchem_void_ns = "http://rdf.ncbi.nlm.nih.gov/pubchem/void.ttl#"
    void_PubChem = rdflib.URIRef(pubchem_void_ns + "PubChemRDF")
    void_PubChem_resource = rdflib.URIRef(pubchem_void_ns + request_ressource)

    # Create output directory for requested ressource and last available version
    version_path = os.path.join(out_path, request_ressource, pubchem_latest)
    if not os.path.exists(version_path):
        os.makedirs(version_path)

    # Parse void
    print("Read Pubchem void.ttl file ... ", end = '')
    g_metadata = rdflib.Graph()
    g_metadata.parse(void_path, format='turtle')
    print("Ok")

    # Download data
    con = ftp_con(ftp)
    download_dir(dir, con, version_path, log)
    con.quit()

    # Create PubChem resource version
    print("Build Pubchem " + request_ressource + " new ressource version ... ", end = '')
    ressource_version = Database_ressource_version(ressource = "PubChem/" + request_ressource, version = pubchem_latest)
    ressource_version.version_graph.namespace_manager = g_metadata.namespace_manager
    
    # Add source
    ressource_version.add_version_attribute(predicate = RDF["type"], object = VOID.Dataset)
    ressource_version.add_version_attribute(predicate = DCTERMS["source"], object = void_PubChem_resource)

    # Add source info
    for s,p,o in g_metadata.triples((void_PubChem_resource, None, None)):
        if p != VOID['dataDump']:
            ressource_version.version_graph.add((s, p, o))
    
    # Compte source with info about the main PubChem Dataset
    ressource_version.version_graph += g_metadata.triples((void_PubChem, None, None))

    # Write void.ttl
    ressource_version.version_graph.serialize(os.path.join(version_path, "void.ttl"), format = 'turtle')
    g_metadata = None
    print("\n\n")

    return ressource_version.version, str(ressource_version.uri_version)

def download_MeSH(out_dir, mesh_latest, ftp, void_path, mesh_path, out_log, dir_log):
    """
    This function is used to download the last version of the MeSH RDF from NIH ftp server, the void.ttl file is also use to bring metadata information about the dowloaded version.
    But contrary to PubChem the modification date is not include in the void.ttl file. So, version is determine from the modification date of the file.
    Ressource is named 'MeSHRDF' as indicate in the void.ttl
    - out_dir: a path to an directory to write output files
    - namespace_list: a list of the namespaces that should be associated to the graph
    The function return the version and the uri of this new version.
    """

    void_MeSH_uri = rdflib.URIRef("http://id.nlm.nih.gov/mesh/void#MeSHRDF")

    # Create version output directory
    out_path = os.path.join(out_dir, mesh_latest)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    
    # Download MeSH void:
    print("Dowload MeSH void ... ", end = '')
    mesh_original_void = os.path.join(dir_log, "MeSH_void.ttl")
    con = ftp_con(ftp)
    download_single_file(void_path, con, mesh_original_void, out_log)
    con.quit()
    print("Ok")

    # Read MeSH void
    print("Read MeSH void.ttl file ... ", end = '')
    g_metadata = rdflib.Graph()
    g_metadata.parse(mesh_original_void, format = 'turtle')
    print("Ok")


    # Download MeSH RDF
    print("Download MeSH data ... ", end = '')
    con = ftp_con(ftp)
    mesh_f_name = os.path.basename(mesh_path)
    mesh_out_path = os.path.join(out_path, mesh_f_name)
    download_single_file(mesh_path, con, mesh_out_path, out_log)
    con.quit()
    print("Ok")

    print("Parse MeSH original metadata ... ", end = '')
    # Create MeSH version
    ressource_version = Database_ressource_version(ressource = "MeSHRDF", version = mesh_latest)
    ressource_version.version_graph.namespace_manager = g_metadata.namespace_manager

    # Add source info
    ressource_version.add_version_attribute(predicate = RDF["type"], object = VOID.Dataset)
    ressource_version.add_version_attribute(predicate = DCTERMS["source"], object = void_MeSH_uri)

    # Add source triples (except for dataDumps) from the void
    for s,p,o in g_metadata.triples((void_MeSH_uri, None, None)):
        # L'attribut creation dans le void correspond à la date de création originale du fichier soir courant 2014, noous souhaitant que la date de création de notre ressource correspondent à la date de modification du fichier
        if p != VOID['dataDump']:
            ressource_version.version_graph.add((s, p, o))
    
    # Read MeSH graph to complete metadata
    mesh_graph = rdflib.Graph()
    mesh_graph.parse(mesh_out_path, format = "nt")
    print("Ok")
    
    # Complete source triples with number of subjects, triples and date of modification
    ressource_version.version_graph.add((void_MeSH_uri, VOID["triples"], rdflib.Literal(len(mesh_graph), datatype = XSD.long)))
    ressource_version.version_graph.add((void_MeSH_uri, VOID["distinctSubjects"], rdflib.Literal( len(set([str(s) for s in mesh_graph.subjects()])), datatype = XSD.long)))
    ressource_version.version_graph.add((void_MeSH_uri, DCTERMS["modified"], rdflib.Literal(mesh_latest, datatype = XSD.date)))

    # Clear metadata graph
    g_metadata = None
    mesh_graph = None
    
    # On écrit le graph de la ressource
    ressource_version.version_graph.serialize(os.path.join(out_path, "void.ttl"), format = 'turtle')
    print("\n\n")
    
    return ressource_version.version, str(ressource_version.uri_version)

def download_MetaNetX(version_path, log, version, url):

    if not os.path.exists(version_path):
        os.makedirs(version_path)
    
    # Download MeSH RDF
    print("Download MetaNetX version " + version + " ... ", end = '')
    try:
        subprocess.run("wget -P " + version_path + " " + url, shell = True, check = True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to download MetaNetX metanetx.ttl.gz file version " + version + ", check dl_metanetx.log")
        print(e)
        with open(log, "ab") as f_log:
            f_log.write(e.stderr)
        sys.exit(3)
    print("Ok")
    
    print("Create new MetaNetX resource: ")
    ressource_version = Database_ressource_version(ressource = "MetaNetX", version = version)

    # Add source:
    uri_metanetx = rdflib.URIRef("https://www.metanetx.org")
    ressource_version.add_version_attribute(predicate = RDF["type"], object = VOID.Dataset)
    ressource_version.add_version_attribute(predicate = DCTERMS["source"], object = uri_metanetx)

    # Read MetaNetX graph
    print("Parse MetaNetX graph to extract metadata ... ", end = '')
    f = os.path.basename(url)
    g_MetaNetX = rdflib.Graph()
    with gzip.open(os.path.join(version_path, f), "rb") as f_MetaNetX:
        g_MetaNetX.parse(f_MetaNetX, format="turtle")
    print("Ok")

    # Extract metadata from MetaNetX graph
    print("Extract metadata ... ", end = '')
    ressource_version.version_graph.add((uri_metanetx, RDF["type"],  VOID["Dataset"]))
    ressource_version.version_graph.add((uri_metanetx, DCTERMS["description"], rdflib.Literal("MetaNetX is a repository of genome-scale metabolic networks (GSMNs) and biochemical pathways from a number of major resources imported into a common namespace of chemical compounds, reactions, cellular compartments (namely MNXref) and proteins.")))
    ressource_version.version_graph.add((uri_metanetx, DCTERMS["title"], rdflib.Literal("MetaNetX v." + version)))
    ressource_version.version_graph.add((uri_metanetx, VOID["dataDump"], rdflib.URIRef(url)))
    ressource_version.version_graph.add((uri_metanetx, VOID["triples"], rdflib.Literal(len(g_MetaNetX), datatype=XSD.long )))
    ressource_version.version_graph.add((uri_metanetx, VOID["distinctSubjects"], rdflib.Literal(len(set([str(s) for s in g_MetaNetX.subjects()])))))
    ressource_version.version_graph.serialize(os.path.join(version_path, "void.ttl"), format = 'turtle')
    print("Ok")
    # Clear memory
    g_MetaNetX = None

    return str(ressource_version.uri_version)
    
def get_URI_version_from_void(path, meta_resource, strCast = True):
    """This function is used to extract the URI of the versioned resource from the void.

    Args:
        path (str): path to the void.ttl file
        meta_resource (rdflib.term.URIRef): The meta resource for which the versioned URI is the object of the property dcterms:hasVersion
        strCast (bool): The URI has to be casted in string before returning

    Returns:
        [rdflib.term.URIRef]: the URI of the versioned resource
    """
    g_void = rdflib.Graph()
    g_void.parse(path, format = 'turtle')
    URI_version = g_void.value(predicate = DCTERMS['hasVersion'], subject = meta_resource, any = False)
    if strCast:
        URI_version = str(URI_version)
    return URI_version

def get_latest_from_MDTM(ftp, path, log):
    print("Check last available version on " + ftp + " ...")
    # Connect ftp server to check void.ttl last modification date
    try:
        ftp = ftplib.FTP(ftp)
        ftp.login()
        mdtm = ftp.voidcmd("MDTM " + path)[4:]
        ftp.quit()
    except ftplib.all_errors as ftplib_e:
        print("Errors while trying to connect to ftp server at " + ftp + ", check logs at " + log)
        with open(log, "a") as f_log:
            f_log.write("\n" + str(ftplib_e) + "\n")
        sys.exit(3)
    # Parse data to create pubchem version
    latest = parser.parse(mdtm)
    latest = latest.strftime('%Y-%m-%d')
    print("Latest version is " + latest)
    return latest

def get_latest_from_void(path_to_void):
    g_void = rdflib.Graph()
    g_void.parse(path_to_void, format = 'turtle')
    modif_date = g_void.value(predicate = DCTERMS['modified'], subject = rdflib.URIRef("http://rdf.ncbi.nlm.nih.gov/pubchem/void.ttl#PubChemRDF"), any = False)
    return str(modif_date)

def check_void(path_to_void, s):
    resource_uri = None
    if glob.glob(path_to_void):
        print("void at " + path_to_void + "' was found.")
        resource_uri = get_URI_version_from_void(path_to_void, s)
    return resource_uri

def ftp_con(ftp):
    ftp = ftplib.FTP(ftp)
    ftp.login()
    return ftp

def download_single_file(file, con, out, log):
    r = None
    f_out = open(out, "wb")
    try:
        r = con.retrbinary('RETR '+ file, f_out.write)
    except ftplib.all_errors as ftplib_e:
        print("Errors while trying to access file " + file + " from " + con.host)
        print("Check logs at " + log)
        with open(log, "a") as f_log:
            f_log.write(str(ftplib_e) + "\n")
    if r != "226 Transfer complete":
        print("Error: Transfer incomplete of " + file + " from ftp server : " + r)
        print("Check logs at " + log)
        with open(log, "a") as f_log:
            f_log.write("Error: Transfer incomplete of " + file + " on ftp server : " + r + "\n")
    f_out.close()
    with open(log, "a") as f_log:
        f_log.write(file + " downloaded\n")

def download_dir(dir, con, out_dir, log):
    try:
        con.cwd(dir)
        filenames = con.nlst()
    except ftplib.all_errors as ftplib_e:
        print("Error while reaching " + dir + " at " + con.host)
        with open(log, "a") as f_log:
            f_log.write(str(ftplib_e) + "\n")
    print("Download directory: " + dir)
    for f in filenames:
        download_single_file(f, con, os.path.join(out_dir, f), log)