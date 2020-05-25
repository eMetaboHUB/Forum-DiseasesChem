import rdflib, eutils, sys, gzip, glob
import argparse, configparser, os
sys.path.insert(1, 'app/')
from Elink_ressource_creator import Elink_ressource_creator
from Database_ressource_version import Database_ressource_version
from download_functions import download_MeSH, download_pubChem

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
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
    "endpoint":	rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/"),
    "obo": rdflib.Namespace("http://purl.obolibrary.org/obo/"),
    "dcterms": rdflib.Namespace("http://purl.org/dc/terms/"),
    "fabio": rdflib.Namespace("http://purl.org/spar/fabio/"),
    "mesh": rdflib.Namespace("http://id.nlm.nih.gov/mesh/"),
    "void": rdflib.Namespace("http://rdfs.org/ns/void#"),
    "skos": rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
}

# Reading paths :

out_path = config['GENERAL'].get('path_out')
# References
reference_out_dir = config['REFERENCE'].get('out_dir_name')
reference_r_name = config['REFERENCE'].get('ressource_name')
reference_dir_on_ftp = config['REFERENCE'].get('dir_on_ftp')
# Compounds
compound_out_dir = config['COMPOUND'].get('out_dir_name')
compound_r_name = config['COMPOUND'].get('ressource_name')
compound_dir_on_ftp = config['COMPOUND'].get('dir_on_ftp')
# Descriptors
descriptor_out_dir = config['DESCRIPTOR'].get('out_dir_name')
descriptor_r_name =config['DESCRIPTOR'].get('ressource_name')
descriptor_dir_on_ftp = config['DESCRIPTOR'].get('dir_on_ftp')
# MeSH 
mesh_out_dir = config['MESH'].get('out_dir_name')
# Elink
run_as_test = config['ELINK'].getboolean('run_as_test')
apiKey = config['ELINK'].get('api_key')
pmid_cid_version = config['ELINK'].get('version')
pack_size = config['ELINK'].getint('pack_size')
timeout = config['ELINK'].getint('timeout')
addtional_files_out_path = config['ELINK'].get('additional_files_out_path')

print("Download MESH :")
mesh_version, mesh_uri = download_MeSH(out_path + mesh_out_dir + "/", namespaces)

print("Download References :")
reference_version, reference_uri = download_pubChem(reference_dir_on_ftp, reference_r_name, out_path + reference_out_dir + "/")

print("Download Compounds :")
compound_version, compound_uri = download_pubChem(compound_dir_on_ftp, compound_r_name, out_path + compound_out_dir + "/")

print("Download Descriptors :")
descriptor_version, descriptor_uri = download_pubChem(descriptor_dir_on_ftp, descriptor_r_name, out_path + descriptor_out_dir + "/")
print("Ok")


# Building requests
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 10000000, 'retmode': 'xml', 'usehistory': 'n'},
                                    api_key = apiKey, email = "maxime.delmas@inrae.fr")
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
                                        timeout = timeout)


# Test if associations files from a previous attempt exists :
version_add_f_path = addtional_files_out_path + "additional_files/" + pmid_cid_version + "/"

if (os.path.exists(version_add_f_path + "all_linking_ids.txt") and
    os.path.exists(version_add_f_path + "successful_linking_ids.txt") and
    os.path.exists(version_add_f_path + "linking_ids_without_linked_ids.txt") and
    os.path.exists(version_add_f_path + "all_linked_ids.txt") and
    os.path.exists(version_add_f_path + "s_metdata.txt")):
    
    # Initialyze pmid list as set to compute subtracting
    all_pmids_set = set()
    print("Cache files from a previous attempt was found.\n")
    print("Read and parse " + version_add_f_path + "all_linking_ids.txt ... ", end = '')
    with open(version_add_f_path + "all_linking_ids.txt", "r") as all_linking_ids_f:
        for id in all_linking_ids_f:
            all_pmids_set.add(id.rstrip())
    
    print("Ok\nRead and parse " + version_add_f_path + "successful_linking_ids.txt ...", end = '')
    successful_linking_ids_set = set()
    with open(version_add_f_path + "successful_linking_ids.txt", "r") as successful_linking_ids_f:
        for id in successful_linking_ids_f:
            successful_linking_ids_set.add(id.rstrip())
    
    print("Ok\nRead and parse " + version_add_f_path + "linking_ids_without_linked_ids.txt ...", end = '')
    linking_ids_without_linked_ids_set = set()
    with open(version_add_f_path + "linking_ids_without_linked_ids.txt", "r") as  linking_ids_without_linked_ids_f:
        for id in linking_ids_without_linked_ids_f:
            linking_ids_without_linked_ids_set.add(id.rstrip())
    
    print("Ok\nRead and parse " + version_add_f_path + "all_linked_ids.txt ... ", end = '')
    all_linked_ids_set = set()
    with open(version_add_f_path + "all_linked_ids.txt", "r") as all_linked_ids_f:
        for id in all_linked_ids_f:
            all_linked_ids_set.add(id.rstrip())
    
    print("Ok\nTry to determine remaining pmids ...", end = '')
    all_pmids = list(all_pmids_set - linking_ids_without_linked_ids_set - successful_linking_ids_set)
    if len(all_pmids) == 0:
        print("Everything seems already done, exit.")
        sys.exit(3)
    print("Ok")
    print(str(len(all_pmids)) + " remaining pmids !")
    print("Try to initialyze all_linked_ids list ...", end = '')
    pmid_cid.all_linked_ids = all_linked_ids_set
    
    print("Ok\nTry to parse previous metadata ... ", end = '')
    with open(version_add_f_path + "s_metdata.txt", "r") as s_metadata_f:
        pmid_cid.n_triples_g_linked_id = int(s_metadata_f.readline())
        pmid_cid.n_triples_g_linked_id_endpoint = int(s_metadata_f.readline())
        pmid_cid.n_subjects_g_linked_id = int(s_metadata_f.readline())
        pmid_cid.n_subjects_g_linked_id_endpoint = int(s_metadata_f.readline())
    
    print("Ok\nTry to retrieve dataDumps files ... ")
    # Initialyze list to determine the last outputed file
    l1 = list()
    l2 = list()
    for pmid_cid_path in [os.path.basename(path) for path in glob.glob(out_path + "PMID_CID/" + pmid_cid_version + "/*.trig.gz")]:
        l1.append(int(pmid_cid_path.split("PMID_CID_")[1].split(".trig.gz")[0]))
        pmid_cid.ressource_version.add_DataDump(pmid_cid_path)
    for pmid_cid_endpoint_path in [os.path.basename(path) for path in glob.glob(out_path + "PMID_CID_endpoints/" + pmid_cid_version + "/*.trig.gz")]:
        l2.append(int(pmid_cid_endpoint_path.split("PMID_CID_endpoints_")[1].split(".trig.gz")[0]))
        pmid_cid.ressource_version_endpoint.add_DataDump(pmid_cid_endpoint_path)
    # The file index is set as the minimum of the last index or PMID_CID and PMIC_CID_endpoints to avoid missing wrong erasing
    if max(l1) == max(l2):
        pmid_cid.file_index = max(l1) + 1
    else:
        pmid_cid.file_index = max(max(l1), max(l2))
    print("Starting output file from index: " + str(pmid_cid.file_index))


else:
    # The second option (in first try) is to get all the pmids to compute the associations. The easiest way to determine the total set of pmids is to load the lightest file from the Reference directory and determine all the subjects
    # Create a Conjunctive graph :
    print("Try to extract all pmids from Reference type graph(s) ...", end = '')
    g = rdflib.ConjunctiveGraph()
    for path in glob.glob(out_path + reference_out_dir + "/" + reference_r_name + "/" + reference_version + "/*_type*.ttl.gz"):
        with gzip.open(path, 'rb') as f_ref_type:
            g.parse(f_ref_type, format = "turtle")

    all_pmids = [str(pmid).split('http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID')[1] for pmid in g.subjects()]

    print("Ok\n" + str(len(all_pmids)) + " pmids were found !")
    # Ex
    with open(version_add_f_path + "all_linking_ids.txt", "w") as all_linking_ids_f:
        for id in all_pmids:
            t = all_linking_ids_f.write("%s\n" %(id))

print("Try to extract CID - PMID associations using Elink processes")

if run_as_test:
    all_pmids = [all_pmids[i] for i in range(0,30000)]

# Run :
pmid_cid.create_ressource(out_path, all_pmids, pack_size, query_builder, 5000000, addtional_files_out_path)

# Looking for failed at first try :
while(len(pmid_cid.request_failure) != 0):
    pmid_cid.create_ressource(out_path, pmid_cid.request_failure, pack_size, query_builder, 5000000, addtional_files_out_path)

pmid_cid.export_ressource_metatdata(out_path, [rdflib.URIRef(reference_uri), rdflib.URIRef(compound_uri)])

pmid_cid_version = pmid_cid.ressource_version.version
pmid_cid_uri_version = pmid_cid.ressource_version.uri_version
pmid_cid_endpoint_uri_version = pmid_cid.ressource_version_endpoint.uri_version

# Final step is to create the file that may be used to load in this data in the correct graphs:

print("Write output file")

with open(out_path + "upload_data.sh", "w") as upload_f:
    upload_f.write("delete from DB.DBA.load_list ;\n")
    # For references
    upload_f.write("ld_dir_all ('./dumps/" + reference_out_dir + "/" + reference_r_name + "/" + reference_version + "/', '*.ttl.gz', '" + reference_uri + "');\n")
    upload_f.write("ld_dir_all ('./dumps/" + reference_out_dir + "/" + reference_r_name + "/" + reference_version + "/', '*.ttl', '" + reference_uri + "');\n")
    # For compounds
    upload_f.write("ld_dir_all ('./dumps/" + compound_out_dir + "/" + compound_r_name + "/" + compound_version + "/', '*.ttl.gz', '" + compound_uri + "');\n")
    upload_f.write("ld_dir_all ('./dumps/" + compound_out_dir + "/" + compound_r_name + "/" + compound_version + "/', '*.ttl', '" + compound_uri + "');\n")
    # For descriptors
    upload_f.write("ld_dir_all ('./dumps/" + descriptor_out_dir + "/" + descriptor_r_name + "/" + descriptor_version + "/', '*.ttl.gz', '" + descriptor_uri + "');\n")
    upload_f.write("ld_dir_all ('./dumps/" + descriptor_out_dir + "/" + descriptor_r_name + "/" + descriptor_version + "/', '*.ttl', '" + descriptor_uri + "');\n")
    # For MeSH
    upload_f.write("ld_dir_all ('./dumps/" + mesh_out_dir + "/" + mesh_version + "/', '*.trig', '');\n")
    upload_f.write("ld_dir_all ('./dumps/" + mesh_out_dir + "/" + mesh_version + "/', '*.ttl', '" + mesh_uri + "');\n")
    # For CID - PMID :
    upload_f.write("ld_dir_all ('./dumps/PMID_CID/" + pmid_cid_version + "/', '*.trig.gz', '');\n")
    upload_f.write("ld_dir_all ('./dumps/PMID_CID/" + pmid_cid_version + "/', '*.ttl', '" + pmid_cid_uri_version + "');\n")
    # For CID - PMID endpoint :
    upload_f.write("ld_dir_all ('./dumps/PMID_CID_endpoints/" + pmid_cid_version + "/', '*.trig.gz', '');\n")
    upload_f.write("ld_dir_all ('./dumps/PMID_CID_endpoints/" + pmid_cid_version + "/', '*.ttl', '" + pmid_cid_endpoint_uri_version + "');\n")
    # Write loaders
    upload_f.write("select * from DB.DBA.load_list;\n")
    upload_f.write("rdf_loader_run();\n")
    upload_f.write("checkpoint;\n")
    upload_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")

print("End")