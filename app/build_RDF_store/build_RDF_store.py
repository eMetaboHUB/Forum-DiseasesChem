import rdflib, eutils, sys, gzip, glob
import argparse, configparser, os
sys.path.insert(1, 'app/')
from Elink_ressource_creator import Elink_ressource_creator
from Database_ressource_version import Database_ressource_version
from parse_pubchem_RDF import parse_pubchem_RDF
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

print("Download MESH :")
mesh_version = download_MeSH(out_path + mesh_out_dir + "/", namespaces)

print("Download References")
reference_version = download_pubChem(reference_dir_on_ftp, reference_r_name, out_path + reference_out_dir + "/")

print("Download Compounds")
compound_version = download_pubChem(compound_dir_on_ftp, compound_r_name, out_path + compound_out_dir + "/")

print("Download Descriptors")
descriptor_version = download_pubChem(descriptor_dir_on_ftp, descriptor_r_name, out_path + descriptor_out_dir + "/")

# The second step is to get all the pmids to compute the associations. The easiest way to determine the total set of pmids is to load the lightest file from the Reference directory and determine all the subjects
# Create a Conjunctive graph :
g = rdflib.ConjunctiveGraph()
for path in glob.glob(out_path + reference_out_dir + "/" + reference_r_name + "/" + reference_version + "/*_type*.ttl.gz"):
    with gzip.open(path, 'rb') as f_ref_type:
        g.parse(f_ref_type, format = "turtle")
all_pmids = [pmid for pmid in g.subjects()]
print(len(all_pmids))




# TODO: C'est ce main qui écrit le fichier d'uplaud avec les bonne version et les bon paths