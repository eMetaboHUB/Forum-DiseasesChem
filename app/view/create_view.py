import configparser
import pandas as pd
import argparse
import os
import io
import sys
import importlib
from processing_functions import *

parser = argparse.ArgumentParser()
parser.add_argument("--ids", help="path to the csv chemical file")
parser.add_argument("--config", help="path to output directory")
parser.add_argument("--out", help="path to output directory")
parser.add_argument("--log", help="path to log directory")
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

# Get virtuoso endpoint url
print("=============================================")
url = config["VIRTUOSO"].get("url")
print("Use endpoint at " + url)
print("=============================================")

print("Get ids ... ", end = '')
try:
    ids = pd.read_csv(filepath_or_buffer = args.ids, dtype = {'CID':str, 'MESH':str})
    print("Ok")
    print("There are " + str(len(ids["CID"])) + " chemicals in the list.")
    print("There are " + str(len(ids["MESH"])) + " MeSH descriptors in the list.")
except IOError as e:
    print("There was an error during reading of chemical csv file: " + str(e))
    sys.exit(3)

print("=============================================")
print("Get SPARQL queries ... ", end = '')
try:
    module = importlib.import_module('SPARQL.requests')
    print("Ok")
except Exception as e:
    print("Error while trying to import sparql queries file in app/view/SPARQL/requests.py")
    print(e)
    sys.exit(3)

# prefix1 allow inference, while prefix2 don't.
prefix1 = getattr(module, 'prefix1')
prefix2 = getattr(module, 'prefix2')

print("=============================================")

print("Send compound related MeSH query ... ", end = '')
# CID -[skos:related]-> MeSH
get_view(url, prefix1, getattr(module, 'cid_mesh'), [config["GRAPHS"].get("cid_mesh"), config["GRAPHS"].get("mesh")], ids["CID"], os.path.join(args.out, "cid-mesh.csv"))

# MeSH -[hasParent]-> MeSH
print("Ok\nSend MeSH hierarchical relations query ... ", end = '')
get_view(url, prefix2, getattr(module, 'mesh_hierarchical_relations'), [config["GRAPHS"].get("cid_mesh"), config["GRAPHS"].get("mesh")], ids["CID"], os.path.join(args.out, "mesh-parentTreeNumber-relations.csv"))

# MeSH -[skos:related]-> MeSH
print("Ok\nSend contextual (MeSH - MeSH) relations query ... ", end = '')
# get_view(url, prefix1, getattr(module, 'mesh_mesh'), [config["GRAPHS"].get("cid_mesh"), config["GRAPHS"].get("mesh_mesh"), config["GRAPHS"].get("mesh")], ids["CID"], os.path.join(args.out, "mesh-mesh-relations.csv"))

# CID -[type]-> ChEBI
print("Ok\nSend cid - ChEBI relations query ... ", end = '')
get_view(url, prefix2, getattr(module, 'cid_chebi'), [config["GRAPHS"].get("cid_chebi_type")], ids["CID"], os.path.join(args.out, "cid-chebi.csv"))

# ChEBI -[hasParent]-> ChEBI
print("Ok\nSend ChEBI hierarchical relations query ... ", end = '')
get_view(url, prefix1, getattr(module, 'chebi_hierarchical_relations'), [config["GRAPHS"].get("cid_chebi_type"), config["GRAPHS"].get("chebi")], ids["CID"], os.path.join(args.out, "chebi-subClassOf-relations.csv"))

# ChEBI -[skos:related]-> MeSH
print("Ok\nSend ChEBI - MeSH to MeSH relations query ... ", end = '')
get_view(url, prefix1, getattr(module, 'cid_related_chebi_related_mesh'), [config["GRAPHS"].get("cid_chebi_type"), config["GRAPHS"].get("chebi"), config["GRAPHS"].get("chebi_mesh")], ids["CID"], os.path.join(args.out, "chebi-mesh-relations.csv"))

# CID -[type]-> ChemOnt
print("Ok\nSend cid - ChemOnt relations query ... ", end = '')
get_view(url, prefix2, getattr(module, 'cid_chemont'), [config["GRAPHS"].get("cid_chemont_type")], ids["CID"], os.path.join(args.out, "cid-chemont.csv"))

# ChemOnt -[hasParent]-> ChemOnt
print("Ok\nSend ChemOnt hierarchical relations query ... ", end = '')
get_view(url, prefix1, getattr(module, 'chemont_hierarchical_relations'), [config["GRAPHS"].get("cid_chemont_type"), config["GRAPHS"].get("chemont")], ids["CID"], os.path.join(args.out, "chemont-subClassOf-relations.csv"))

# ChemOnt -[skos:related]-> ChemOnt
print("Ok\nSend Chemont - MeSH to MeSH relations query ... ", end = '')
get_view(url, prefix1, getattr(module, 'cid_related_chemont_related_mesh'), [config["GRAPHS"].get("cid_chemont_type"), config["GRAPHS"].get("chemont"), config["GRAPHS"].get("chemont_mesh")], ids["CID"], os.path.join(args.out, "chemont-mesh-relations.csv"))
print("Ok")