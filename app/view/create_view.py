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

print("- Send compound related MeSH query -")
# CID -[skos:related]-> MeSH
get_view(url = url, prefix = prefix1, request = getattr(module, 'cid_mesh'), g_from = [config["GRAPHS"].get("cid_mesh"), config["GRAPHS"].get("mesh")], cpd_list = ids["CID"], out = os.path.join(args.out, "cid-mesh.csv"))

# MeSH -[hasParent]-> MeSH
print("Ok\nSend MeSH hierarchical relations query -")
get_view(url = url, prefix = prefix2, request = getattr(module, 'mesh_hierarchical_relations'), g_from = [config["GRAPHS"].get("mesh")], out = os.path.join(args.out, "mesh-parentTreeNumber-relations.csv"))

# MeSH -[hasLabel]-> MeSH
print("- Send MeSH label query -")
get_view(url = url, prefix = prefix1, request = getattr(module, 'mesh_label'), g_from = [config["GRAPHS"].get("mesh")], out = os.path.join(args.out, "mesh-labels.csv"))

# MeSH -[skos:related]-> MeSH
print("- Send contextual (MeSH - MeSH) relations query -")
get_view(url = url, prefix = prefix1, request = getattr(module, 'cid_mesh_related_mesh'), g_from = [config["GRAPHS"].get("cid_mesh"), config["GRAPHS"].get("mesh_mesh"), config["GRAPHS"].get("mesh")], cpd_list = ids["CID"], out = os.path.join(args.out, "mesh-mesh-relations.csv"))

# CID -[type]-> ChEBI
print("- Send cid - ChEBI relations query - ")
get_view(url = url, prefix = prefix2, request = getattr(module, 'cid_chebi'), g_from = [config["GRAPHS"].get("cid_chebi_type")], cpd_list = ids["CID"], out = os.path.join(args.out, "cid-chebi.csv"))

# ChEBI -[hasParent]-> ChEBI
# Attention: dans les relations contextuelles, on cherche des MeSH reliés ensemble, MAIS, les deux membres de la relation sont reliés aux composé d'intéret. C'est donc les relations related, entre MeSH reliés aux composés.
print("- Send ChEBI hierarchical relations query -")
get_view(url = url, prefix = prefix1, request = getattr(module, 'chebi_hierarchical_relations'), g_from = [config["GRAPHS"].get("chebi")], out = os.path.join(args.out, "chebi-subClassOf-relations.csv"))

print("- Send ChEBI label query -")
get_view(url = url, prefix = prefix1, request = getattr(module, 'chebi_label'), g_from = [config["GRAPHS"].get("chebi")], out = os.path.join(args.out, "chebi-labels.csv"))

# ChEBI -[skos:related]-> MeSH
print("- Send ChEBI - MeSH to MeSH relations query -")
get_view(url = url, prefix = prefix1, request = getattr(module, 'cid_related_chebi_related_mesh'), g_from = [config["GRAPHS"].get("cid_chebi_type"), config["GRAPHS"].get("chebi"), config["GRAPHS"].get("chebi_mesh")], cpd_list = ids["CID"], out = os.path.join(args.out, "chebi-mesh-relations.csv"))

# CID -[type]-> ChemOnt
print("- Send cid - ChemOnt relations query -")
get_view(url = url, prefix = prefix2, request = getattr(module, 'cid_chemont'), g_from = [config["GRAPHS"].get("cid_chemont_type")], cpd_list = ids["CID"], out = os.path.join(args.out, "cid-chemont.csv"))

# ChemOnt -[hasParent]-> ChemOnt
print("- Send ChemOnt hierarchical relations query -")
get_view(url = url, prefix = prefix1, request = getattr(module, 'chemont_hierarchical_relations'), g_from = [config["GRAPHS"].get("chemont")], out = os.path.join(args.out, "chemont-subClassOf-relations.csv"))

print("- Send ChEBI label query -", end = '')
get_view(url = url, prefix = prefix1, request = getattr(module, 'chemont_label'), g_from = [config["GRAPHS"].get("chemont")], out = os.path.join(args.out, "chemont-labels.csv"))

# ChemOnt -[skos:related]-> ChemOnt
print("- Send Chemont - MeSH to MeSH relations query -")
get_view(url = url, prefix = prefix1, request = getattr(module, 'cid_related_chemont_related_mesh'), g_from = [config["GRAPHS"].get("cid_chemont_type"), config["GRAPHS"].get("chemont"), config["GRAPHS"].get("chemont_mesh")], cpd_list = ids["CID"], out = os.path.join(args.out, "chemont-mesh-relations.csv"))
print("Ok")