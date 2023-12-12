import argparse, configparser, os, glob, sys, json, rdflib, eutils, gzip
import pandas as pd
sys.path.insert(1, 'app/')
from Elink_ressource_creator import Elink_ressource_creator
from Database_ressource_version import Database_ressource_version
from download_functions import check_void

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--log", help="path to log and additional files directory")
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

# Init
PMID_CID_upload_file = config["DEFAULT"].get("upload_file")
PMID_CID_log_file = config["DEFAULT"].get("log_file")
run_as_test = config['ELINK'].getboolean('run_as_test')
apiKey = config['ELINK'].get('api_key')
pmid_cid_version = config['ELINK'].get('version')
pack_size = config['ELINK'].getint('pack_size')
timeout = config['ELINK'].getint('timeout')
max_triples_by_files = config['ELINK'].getint('max_triples_by_files')
ref_uri_prefix = config['ELINK'].get("reference_uri_prefix")
compound_path = config['ELINK'].get("compound_path")
reference_path = config['ELINK'].get("reference_path")
pubchem_ref_id_mapping = config['ELINK'].get("pubchem_ref_id_mapping")

# Check is this PMID resource already exists:
pmid_cid_uri_version = check_void(os.path.join(args.out, "PMID_CID", pmid_cid_version, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/PMID_CID"))
pmid_cid_endpoint_uri_version = check_void(os.path.join(args.out, "PMID_CID_endpoints", pmid_cid_version, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/PMID_CID_endpoints"))

if pmid_cid_uri_version and pmid_cid_endpoint_uri_version:
    print("Resources PMID_CID and PMIC_CID_endpoint already exists")

# If not, create resource:
else:
    print("Start creating resource PMID_CID & PMID_CID_endpoint")
    # Check if PubChem compound source and reference are valid
    compound_uri = check_void(os.path.join(args.out, compound_path, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/PubChem/compound"))
    reference_uri = check_void(os.path.join(args.out, reference_path, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/PubChem/reference"))

    if (not compound_uri) or (not reference_uri):
        print("Paths to resource PubChem reference and/or PubChem compound are not valid, no void.ttl found.")
        sys.exit(3)

    try:
        ids_map = pd.read_csv(pubchem_ref_id_mapping, sep="\t", header=None, dtype=object)
    except pd.errors.ParserError as except_parsing_error:
        print("file at {path} has incorrect format: {err}".format(path=pubchem_ref_id_mapping, err=str(except_parsing_error)))
        sys.exit(1)

    except FileNotFoundError:
        print("File not found at {path}".format(path=pubchem_ref_id_mapping))
        sys.exit(1)

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
                                        ids_map=dict(zip(ids_map.iloc[:,1].tolist(), ids_map.iloc[:,0].tolist())),
                                        #ns_linking_id = ("reference", "PMID"),
                                        ns_linking_id = ("reference", ""), # fix ofilangi 10-2023 - PMID References are no longer prefixed by PMID
                                        ns_linked_id = ("compound", "CID"),
                                        ns_endpoint = ("endpoint", ""),
                                        primary_predicate = ("cito", "discusses"),
                                        secondary_predicate = ("cito", "isCitedAsDataSourceBy"),
                                        namespaces = namespaces,
                                        timeout = timeout)

    # If version was set to None, it has been transform to date in the Elink_ressource_creator objects, if no None it was keeped
    pmid_cid_version = pmid_cid.ressource_version.version

    # Test if associations files from a previous attempt exists
    version_add_f_path = os.path.join(args.log, "additional_files", pmid_cid_version)
    if (os.path.exists(os.path.join(version_add_f_path, "all_linking_ids.txt")) and
        os.path.exists(os.path.join(version_add_f_path, "successful_linking_ids.txt")) and
        os.path.exists(os.path.join(version_add_f_path, "linking_ids_without_linked_ids.txt")) and
        os.path.exists(os.path.join(version_add_f_path, "all_linked_ids.txt")) and
        os.path.exists(os.path.join(version_add_f_path, "s_metdata.txt"))):

        # If additional files from a previous attempt was found, parse them to restart from what has been already done
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
        
        # Check if the PMID_CID and PMID_CID_endpoint exist
        if not len(glob.glob(os.path.join(args.out, "PMID_CID", pmid_cid_version, "*.ttl.gz"))) or not len(glob.glob(os.path.join(args.out, "PMID_CID_endpoints", pmid_cid_version, "*.ttl.gz"))):
            print("Cache files were found at : " + version_add_f_path + " but the PMID_CID and/or PMID_CID_endpoints are missing. If you want to rebuild the PMID_CID and PMID_CID_endpoints directories, please remove the cache files at :" + version_add_f_path)
            sys.exit(3)
        
        # Initialyze list to determine the last outputed file
        l1 = list()
        l2 = list()
        for pmid_cid_path in [os.path.basename(path) for path in glob.glob(os.path.join(args.out, "PMID_CID", pmid_cid_version, "*.ttl.gz"))]:
            l1.append(int(pmid_cid_path.split("PMID_CID_")[1].split(".ttl.gz")[0]))
        
        for pmid_cid_endpoint_path in [os.path.basename(path) for path in glob.glob(os.path.join(args.out, "PMID_CID_endpoints", pmid_cid_version, "*.ttl.gz"))]:
            l2.append(int(pmid_cid_endpoint_path.split("PMID_CID_endpoints_")[1].split(".ttl.gz")[0]))
        
        # The file index is set as the maximum of the last index or PMID_CID and PMIC_CID_endpoints to avoid missing wrong erasing, if they are different ! Or the next index if they are equals
        if max(l1) == max(l2):
            pmid_cid.file_index = max(l1) + 1
        else:
            pmid_cid.file_index = max(max(l1), max(l2))
        print("Starting output file from index: " + str(pmid_cid.file_index))

    else:
        
        all_pmids = list(pmid_cid.ids_map.keys())

        print(str(len(all_pmids)) + " pmids were found !")
        if run_as_test:
            all_pmids = [all_pmids[i] for i in range(0,100000)]
        
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
    pmid_cid.export_ressource_metatdata(args.out, [rdflib.URIRef(reference_uri), rdflib.URIRef(compound_uri)])

    # Export versions and uris versions
    pmid_cid_uri_version = pmid_cid.ressource_version.uri_version
    pmid_cid_endpoint_uri_version = pmid_cid.ressource_version_endpoint.uri_version

# Write in upload file :
with open(os.path.join(args.out, PMID_CID_upload_file), "w") as upload_f:
    upload_f.write("delete from DB.DBA.load_list ;\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID/", pmid_cid_version, '') + "', '*.ttl.gz', '" + str(pmid_cid_uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID/", pmid_cid_version, '') + "', 'void.ttl', '" + str(pmid_cid_uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID_endpoints/", pmid_cid_version, '') + "', '*.ttl.gz', '" + str(pmid_cid_endpoint_uri_version) + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/PMID_CID_endpoints/", pmid_cid_version, '') + "', 'void.ttl', '" + str(pmid_cid_endpoint_uri_version) + "');\n")
    upload_f.write("select * from DB.DBA.load_list;\n")
    upload_f.write("rdf_loader_run();\n")
    upload_f.write("checkpoint;\n")
    upload_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")