import rdflib, eutils, sys, gzip, glob
import argparse, configparser, os
import json
sys.path.insert(1, 'app/')
from Elink_ressource_creator import Elink_ressource_creator
from Database_ressource_version import Database_ressource_version
from download_functions import *

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--log", help="path to log and additional files directory")
parser.add_argument("--version", help="version of the PMID-CID ressource, if none, the date is used")
args = parser.parse_args()

if not os.path.exists(args.config):
    print("Config file : " + args.config + " does not exist")
    sys.exit(3)

try:    
    config = configparser.ConfigParser()
    config.read(args.config)
except configparser.Error as e:
    print(e)
    sys.exit(3)

# Intialyze attributes and paths: 

# Creating the directory of all namespaces
namespaces = {
    "cito": rdflib.Namespace("http://purl.org/spar/cito/"),
    "compound": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"),
    "reference": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/reference/"),
    "endpoint":	rdflib.Namespace("https://forum.semantic-metabolomics.org/mention/"),
    "obo": rdflib.Namespace("http://purl.obolibrary.org/obo/"),
    "dcterms": rdflib.Namespace("http://purl.org/dc/terms/"),
    "fabio": rdflib.Namespace("http://purl.org/spar/fabio/"),
    "mesh": rdflib.Namespace("http://id.nlm.nih.gov/mesh/"),
    "void": rdflib.Namespace("http://rdfs.org/ns/void#"),
    "skos": rdflib.Namespace("http://www.w3.org/2004/02/skos/core#"),
    "source": rdflib.Namespace('http://rdf.ncbi.nlm.nih.gov/pubchem/source/'),
    "concept": rdflib.Namespace('http://rdf.ncbi.nlm.nih.gov/pubchem/concept/')
}

# FTP info
ftp = config['FTP'].get('ftp')

# Write ouput file header :
with open(os.path.join(args.out, "upload_data.sh"), "w") as upload_f, open(os.path.join(args.out, "pre_upload.sh"), "w") as pre_upload:
    upload_f.write("delete from DB.DBA.load_list ;\n")
    pre_upload.write("delete from DB.DBA.load_list ;\n")

# MetaNetX
if config.has_section("METANETX"):
    MetaNetX_out_dir = "MetaNetX"
    MetaNetX_version = config['METANETX'].get("version")
    MetaNetX_uri = download_MetaNetX(os.path.join(args.out, MetaNetX_out_dir), args.log, MetaNetX_version)
    with open(os.path.join(args.out, "upload_MetaNetX.sh"), "w") as upload_MetaNetX:
        upload_MetaNetX.write("delete from DB.DBA.load_list ;\n")
        upload_MetaNetX.write("ld_dir_all ('" + os.path.join("./dumps/", MetaNetX_out_dir, MetaNetX_version, '') + "', 'metanetx.ttl.gz', '" + MetaNetX_uri + "');\n")
        upload_MetaNetX.write("ld_dir_all ('" + os.path.join("./dumps/", MetaNetX_out_dir, MetaNetX_version, '') + "', 'void.ttl', '" + MetaNetX_uri + "');\n")

# MeSH
if config.has_section("MESH"):
    mesh_out_dir = "MeSH"
    mesh_version = config["MESH"].get("version")
    ftp = config["MESH"].get("ftp")
    ftp_path_mesh = config["MESH"].get("ftp_path_mesh")
    ftp_path_void = config["MESH"].get("ftp_path_void")

    # Intialyze .log files
    log_path = os.path.join(args.log, "dl_mesh.log")
    with open(log_path, "wb") as f_log:
        pass

    meta_resource = rdflib.URIRef("https://forum.semantic-metabolomics.org/MeSHRDF")
    # if 'latest' was provided:
    if mesh_version == "latest":
        mesh_version = get_latest_from_MDTM(ftp, ftp_path_mesh, log_path)
        
        # Check void
        path_to_void = os.path.join(args.out, mesh_out_dir, mesh_version, "void.ttl")
        mesh_uri = check_void(path_to_void, meta_resource)

        # If no resource was found, download from ftp
        if not mesh_uri:
            mesh_version, mesh_uri = download_MeSH(os.path.join(args.out, mesh_out_dir), mesh_version, ftp, ftp_path_void, ftp_path_mesh, log_path, args.log)

    # if a version was provided
    else:
        print("Version '" + mesh_version + "' was provided for MeSH")
        path_to_void = os.path.join(args.out, mesh_out_dir, mesh_version, "void.ttl")
        mesh_uri = check_void(path_to_void, meta_resource)

        # Check if the version exists
        if not mesh_uri:
            print("MeSH version " + mesh_version + "' was not found.")
            print("Provide a valid version or download the latest")
            sys.exit(3)
    
    # Write upload files
    with open(os.path.join(args.out, "upload_data.sh"), "a") as upload_f, open(os.path.join(args.out, "pre_upload.sh"), "a") as pre_upload:
        upload_f.write("ld_dir_all ('" + os.path.join("./dumps/", mesh_out_dir, mesh_version, '') + "', 'mesh.nt', '" + mesh_uri + "');\n")
        upload_f.write("ld_dir_all ('" + os.path.join("./dumps/", mesh_out_dir,  mesh_version, '') + "', 'void.ttl', '" + mesh_uri + "');\n")
        # Also for pre-upload:
        pre_upload.write("ld_dir_all ('" + os.path.join("./dumps/", mesh_out_dir, mesh_version, '') + "', 'mesh.nt', '" + mesh_uri + "');\n")
        pre_upload.write("ld_dir_all ('" + os.path.join("./dumps/", mesh_out_dir, mesh_version, '') + "', 'void.ttl', '" + mesh_uri + "');\n")


# PUBCHEM

# Init PubChem Subset: 
PubChem_subsets = dict()

if config.has_section("PUBCHEM"):
    print("Download and prepare resources from PubChem: ")
    dir_ftp = json.loads(config["PUBCHEM"].get("dir_ftp"))
    name = json.loads(config["PUBCHEM"].get("name"))
    out_dir = json.loads(config["PUBCHEM"].get("out_dir"))
    mincore = json.loads(config["PUBCHEM"].get("mincore"))
    maxcore = json.loads(config["PUBCHEM"].get("maxcore"))
    version = json.loads(config["PUBCHEM"].get("version"))

    ftp = config["PUBCHEM"].get("ftp")
    ftp_path_void = config["PUBCHEM"].get("ftp_path_void")

    if not len(dir_ftp) == len(mincore) == len(maxcore) == len(name) == len(out_dir) == len(version):
        print("Error: PUBCHEM options dir_ftp, mincore, resource, out_dir, version and maxcore don't have the same length, check config file.")
        sys.exit(3)
    n = len(dir_ftp)
    for i in range(n):
        resource_out_dir = out_dir[i]
        resource_name = name[i]
        resource_dir_ftp = dir_ftp[i]
        resource_mincore = mincore[i]
        resource_maxcore = maxcore[i]
        resource_version = version[i]
        
        # Intialyze .log files
        log_path = os.path.join(args.log, "dl_pubchem_" + resource_name + ".log")
        with open(log_path, "wb") as f_log:
            pass
        
        # The URI of the resource that will be versioned
        meta_resource = rdflib.URIRef("https://forum.semantic-metabolomics.org/PubChem/" + resource_name)

        # if 'latest' was provided:
        if resource_version == "latest":
            resource_version = get_latest_from_MDTM(ftp, ftp_path_void, log_path)

            # Check void
            path_to_void = os.path.join(args.out, resource_out_dir, resource_name, resource_version, "void.ttl")
            resource_uri = check_void(path_to_void, meta_resource)

            # If no resource was found, download from ftp
            if not resource_uri:
                resource_version, resource_uri = download_pubChem(resource_dir_ftp, resource_name, resource_version, ftp, ftp_path_void, os.path.join(args.out, resource_out_dir), log_path, args.log)
        
        # if a version was provided
        else: 
            # Check if the version exist:
            print("Check if " + resource_dir_ftp + " version " + resource_version + " exists")
            path_to_void = os.path.join(args.out, resource_out_dir, resource_name, resource_version, "void.ttl")
            resource_uri = check_void(path_to_void, meta_resource)
            if not resource_uri:
                print("PubChem Subset " + resource_dir_ftp + " version '" + resource_version  + "' was not found.")
                print("Provide a valid version or download the latest")
                sys.exit(3)
        
        # Add to PubChem Subset dict: 
        PubChem_subsets[resource_name] = {"dir_ftp": resource_dir_ftp, "out_dir": resource_out_dir, "name": resource_name, "mincore": resource_mincore, "maxcore": resource_maxcore, "version": resource_version, "uri": resource_uri}
        if resource_maxcore:
            with open(os.path.join(args.out, "upload_data.sh"), "a") as upload_f:
                upload_f.write("ld_dir_all ('" + os.path.join("./dumps/", resource_out_dir, resource_name, resource_version, '') + "', '" + resource_maxcore + "', '" + resource_uri + "');\n")
                upload_f.write("ld_dir_all ('" + os.path.join("./dumps/", resource_out_dir, resource_name, resource_version, '') + "', 'void.ttl', '" + resource_uri + "');\n")
        if resource_mincore:
            with open(os.path.join(args.out, "pre_upload.sh"), "a") as pre_upload:
                pre_upload.write("ld_dir_all ('" + os.path.join("./dumps/", resource_out_dir, resource_name, resource_version, '') + "', '" + resource_mincore + "', '" + resource_uri + "');\n")
                pre_upload.write("ld_dir_all ('" + os.path.join("./dumps/", resource_out_dir, resource_name, resource_version, '') + "', 'void.ttl', '" + resource_uri + "');\n")

# Elink
if config.has_section("ELINK"):
    run_as_test = config['ELINK'].getboolean('run_as_test')
    apiKey = config['ELINK'].get('api_key')
    pmid_cid_version = args.version
    pack_size = config['ELINK'].getint('pack_size')
    timeout = config['ELINK'].getint('timeout')
    max_triples_by_files = config['ELINK'].getint('max_triples_by_files')
    ref_uri_prefix = config['ELINK']["reference_uri_prefix"]
    all_pmids = None
    # Building requests
    query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 10000000, 'retmode': 'xml', 'usehistory': 'n'},
                                    api_key = apiKey, email = "service.pfem@inrae.fr")
    # Build Elink ressource creator: 
    pmid_cid = Elink_ressource_creator(ressource_name = "PMID_CID", 
                                        version = pmid_cid_version, 
                                        dbfrom = "pubmed",
                                        db = "pccompound",
                                        ns_linking_id = ("reference", "PMID"),
                                        ns_linked_id = ("compound", "CID"),
                                        ns_endpoint = ("endpoint", ""),
                                        primary_predicate = ("cito", "discusses"),
                                        secondary_predicate = ("cito", "isCitedAsDataSourceBy"),
                                        namespaces = namespaces,
                                        timeout = timeout,
                                        ftp = ftp)
    # If version was set to None, it has been transform to date in the Elink_ressource_creator objects, if no None it was keeped
    pmid_cid_version = pmid_cid.ressource_version.version
    # Test if associations files from a previous attempt exists :
    version_add_f_path = os.path.join(args.log, "additional_files", pmid_cid_version)
    if (os.path.exists(os.path.join(version_add_f_path, "all_linking_ids.txt")) and
        os.path.exists(os.path.join(version_add_f_path, "successful_linking_ids.txt")) and
        os.path.exists(os.path.join(version_add_f_path, "linking_ids_without_linked_ids.txt")) and
        os.path.exists(os.path.join(version_add_f_path, "all_linked_ids.txt")) and
        os.path.exists(os.path.join(version_add_f_path, "s_metdata.txt"))):
        # If additional files from a previous attempt was found, try to parse them to restart from what has been already done
        # Initialyze pmid list as set to compute subtracting
        all_pmids_set = set()
        print("Cache files from a previous attempt was found.\n")
        print("Read and parse " + version_add_f_path + "all_linking_ids.txt ... ", end = '')
        with open(os.path.join(version_add_f_path, "all_linking_ids.txt"), "r") as all_linking_ids_f:
            for id in all_linking_ids_f:
                all_pmids_set.add(id.rstrip())
        
        print("Ok\nRead and parse " + version_add_f_path + "successful_linking_ids.txt ...", end = '')
        successful_linking_ids_set = set()
        with open(os.path.join(version_add_f_path, "successful_linking_ids.txt"), "r") as successful_linking_ids_f:
            for id in successful_linking_ids_f:
                successful_linking_ids_set.add(id.rstrip())
        
        print("Ok\nRead and parse " + version_add_f_path + "linking_ids_without_linked_ids.txt ...", end = '')
        linking_ids_without_linked_ids_set = set()
        with open(os.path.join(version_add_f_path, "linking_ids_without_linked_ids.txt"), "r") as  linking_ids_without_linked_ids_f:
            for id in linking_ids_without_linked_ids_f:
                linking_ids_without_linked_ids_set.add(id.rstrip())
        
        print("Ok\nRead and parse " + version_add_f_path + "all_linked_ids.txt ... ", end = '')
        all_linked_ids_set = set()
        with open(os.path.join(version_add_f_path, "all_linked_ids.txt"), "r") as all_linked_ids_f:
            for id in all_linked_ids_f:
                all_linked_ids_set.add(id.rstrip())
        
        print("Ok\nTry to determine remaining pmids ...", end = '')
        all_pmids = list(all_pmids_set - linking_ids_without_linked_ids_set - successful_linking_ids_set)
        print("Ok")
        print(str(len(all_pmids)) + " remaining pmids !")
        print("Try to initialyze all_linked_ids list ...", end = '')
        pmid_cid.all_linked_ids = all_linked_ids_set
        
        print("Ok\nTry to parse previous metadata ... ", end = '')
        with open(os.path.join(version_add_f_path, "s_metdata.txt"), "r") as s_metadata_f:
            pmid_cid.n_triples_g_linked_id = int(s_metadata_f.readline())
            pmid_cid.n_triples_g_linked_id_endpoint = int(s_metadata_f.readline())
            pmid_cid.n_subjects_g_linked_id = int(s_metadata_f.readline())
            pmid_cid.n_subjects_g_linked_id_endpoint = int(s_metadata_f.readline())
        
        print("Ok\nTry to retrieve dataDumps files ... ")
        
        # Check if the PMID_CID and PMID_CID_endpoint exist
        if not len(glob.glob(os.path.join(args.out, "PMID_CID", pmid_cid_version, "*.ttl.gz"))) or not len(glob.glob(os.path.join(args.out, "PMID_CID_endpoints", pmid_cid_version, "*.ttl.gz"))):
            print("Cache files were found at : " + version_add_f_path + " but the PMID_CID and/or PMID_CID_endpoints are missing. If you want to rebuild the PMID_CID and PMID_CID_endpoints directories, please remove the cache files at :" + version_add_f_path)
            sys.exit(3)
        
        # Initialyze list to determine the last outputed file
        l1 = list()
        l2 = list()
        for pmid_cid_path in [os.path.basename(path) for path in glob.glob(os.path.join(args.out, "PMID_CID", pmid_cid_version, "*.ttl.gz"))]:
            l1.append(int(pmid_cid_path.split("PMID_CID_")[1].split(".ttl.gz")[0]))
            pmid_cid.ressource_version.add_DataDump(pmid_cid_path, ftp)
        for pmid_cid_endpoint_path in [os.path.basename(path) for path in glob.glob(os.path.join(args.out, "PMID_CID_endpoints", pmid_cid_version, "*.ttl.gz"))]:
            l2.append(int(pmid_cid_endpoint_path.split("PMID_CID_endpoints_")[1].split(".ttl.gz")[0]))
            pmid_cid.ressource_version_endpoint.add_DataDump(pmid_cid_endpoint_path, ftp)
        # The file index is set as the maximum of the last index or PMID_CID and PMIC_CID_endpoints to avoid missing wrong erasing, if they are different ! Or the next index if they are equals
        if max(l1) == max(l2):
            pmid_cid.file_index = max(l1) + 1
        else:
            pmid_cid.file_index = max(max(l1), max(l2))
        print("Starting output file from index: " + str(pmid_cid.file_index))
    
    else:
        # The second option (in first try) is to get all the pmids to compute the associations. The easiest way to determine the total set of pmids is to load the lightest file from the Reference directory and determine all the subjects
        if not "reference" in PubChem_subsets:
            print("Impossible to access to pmids from PubChem Reference RDF Store, unknown last version. The data will be download ONLY if needed ! Please, add the PubChem subset 'reference' to the list of required PubChem subsets in the config file, exit.")
            sys.exit(3)
        print("Try to extract all pmids from Reference type graph(s) ...", end = '')
        reference_out_dir = PubChem_subsets["reference"]["out_dir"]
        reference_r_name = PubChem_subsets["reference"]["name"]
        reference_version = PubChem_subsets["reference"]["version"]
        path_list = glob.glob(os.path.join(args.out, reference_out_dir, reference_r_name, reference_version, "*_type*.ttl.gz"))
        if len(path_list) == 0:
            print("No *_type*.ttl.gz files from PubChem ftp was found at " + os.path.join(args.out, reference_out_dir, reference_r_name, reference_version))
            print("Impossible to determine pmids set, exit.")
            sys.exit(3)
        g = rdflib.ConjunctiveGraph()
        for path in path_list:
            with gzip.open(path, 'rb') as f_ref_type:
                g.parse(f_ref_type, format = "turtle")
        
        all_pmids = [str(pmid).split(ref_uri_prefix)[1] for pmid in g.subjects()]

        print(" Ok\n" + str(len(all_pmids)) + " pmids were found !")
        if run_as_test:
            all_pmids = [all_pmids[i] for i in range(0,5000)]
        # Export all_pmids list as linking ids list in addtional path
        if not os.path.exists(version_add_f_path):
            os.makedirs(version_add_f_path)
        with open(os.path.join(version_add_f_path, "all_linking_ids.txt"), "w") as all_linking_ids_f:
            for id in all_pmids:
                t = all_linking_ids_f.write("%s\n" %(id))
    
    # From a previous attempt or a first try, use all_pmids list to compute associations :
    print("Try to extract CID - PMID associations using Elink processes")
    # Run :
    pmid_cid.create_ressource(args.out, all_pmids, pack_size, query_builder, max_triples_by_files, args.log)
    # Looking for failed at first try :
    while(len(pmid_cid.request_failure) != 0):
        pmid_cid.create_ressource(args.out, pmid_cid.request_failure, pack_size, query_builder, max_triples_by_files, args.log)
    # Export ressource metadata
    pmid_cid.export_ressource_metatdata(args.out, [rdflib.URIRef(PubChem_subsets["reference"]["uri"]), rdflib.URIRef(PubChem_subsets["compound"]["uri"])])
    # Export versions and uris versions
    pmid_cid_uri_version = pmid_cid.ressource_version.uri_version
    pmid_cid_endpoint_uri_version = pmid_cid.ressource_version_endpoint.uri_version
    # Write in upload file :
    with open(os.path.join(args.out, "upload_data.sh"), "a") as upload_f, open(os.path.join(args.out, "pre_upload.sh"), "a") as pre_upload:
        upload_f.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID/", pmid_cid_version, '') + "', '*.ttl.gz', '" + str(pmid_cid_uri_version) + "');\n")
        upload_f.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID/", pmid_cid_version, '') + "', 'void.ttl', '" + str(pmid_cid_uri_version) + "');\n")
        upload_f.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID_endpoints/", pmid_cid_version, '') + "', '*.ttl.gz', '" + str(pmid_cid_endpoint_uri_version) + "');\n")
        upload_f.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID_endpoints/", pmid_cid_version, '') + "', 'void.ttl', '" + str(pmid_cid_endpoint_uri_version) + "');\n")
        # For pre-upload, we need just type to compute with ChEBI:
        pre_upload.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID/", pmid_cid_version, '') + "', '*.ttl.gz', '" + str(pmid_cid_uri_version) + "');\n")
        pre_upload.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID/", pmid_cid_version, '') + "', 'void.ttl', '" + str(pmid_cid_uri_version) + "');\n")
        pre_upload.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID_endpoints/", pmid_cid_version, '') + "', '*.ttl.gz', '" + str(pmid_cid_endpoint_uri_version) + "');\n")
        pre_upload.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID_endpoints/", pmid_cid_version, '') + "', 'void.ttl', '" + str(pmid_cid_endpoint_uri_version) + "');\n")

print("=================================================================================\n")
# Write ouput file footer :
print("Write uplaod file")
with open(os.path.join(args.out, "upload_data.sh"), "a") as upload_f, open(args.out + "pre_upload.sh", "a") as pre_upload:
    upload_f.write("select * from DB.DBA.load_list;\n")
    upload_f.write("rdf_loader_run();\n")
    upload_f.write("checkpoint;\n")
    upload_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")
    # The same for pre-upload.sh
    pre_upload.write("select * from DB.DBA.load_list;\n")
    pre_upload.write("rdf_loader_run();\n")
    pre_upload.write("checkpoint;\n")
    pre_upload.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")

print("End")