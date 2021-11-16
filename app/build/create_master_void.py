import sys
import argparse
import os
import glob
import rdflib
import configparser
from datetime import date
from rdflib.namespace import XSD, DCTERMS, RDF, VOID, FOAF


parser = argparse.ArgumentParser()
parser.add_argument("--path", help="path to the Virtuoso share directory")
parser.add_argument("--config", help="path to config file")

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

version = config["RELEASE"].get("version")
ftp = config["RELEASE"].get("ftp")

# New namespaces
ns_voag = rdflib.Namespace("http://voag.linkedmodel.org/schema/voag#")
ns_freq = rdflib.Namespace("http://purl.org/cld/freq/")

# Create Master Void :
master_void = rdflib.Graph()
master_void.bind("dcterms", rdflib.Namespace("http://purl.org/dc/terms/"))
master_void.bind("void", rdflib.Namespace("http://rdfs.org/ns/void#"))
master_void.bind("voag", ns_voag)
master_void.bind("freq", ns_freq)
master_void_uri = rdflib.URIRef("https://forum.semantic-metabolomics.org/void")

# Add VoID metadata:
master_void.add((master_void_uri, RDF['type'], VOID["Dataset"]))
master_void.add((master_void_uri, DCTERMS['title'], rdflib.Literal("FORUM DiseaseChem RDF Dataset Description")))
master_void.add((master_void_uri, DCTERMS['description'], rdflib.Literal("This is the VoID description for FORUM DiseaseChem RDF datasets.")))
master_void.add((master_void_uri, DCTERMS["created"], rdflib.Literal(date(2020,3,16), datatype = XSD.date)))
master_void.add((master_void_uri, DCTERMS["modified"], rdflib.Literal(date.today().isoformat(), datatype = XSD.date)))
master_void.add((master_void_uri, FOAF["homepage"], rdflib.URIRef("https://forum-webapp.semantic-metabolomics.fr")))
master_void.add((master_void_uri, ns_voag["frequencyOfChange"], ns_freq["annual"]))
master_void.add((master_void_uri, VOID["sparqlEndpoint"], rdflib.URIRef("https://forum.semantic-metabolomics.fr/sparql")))
master_void.add((master_void_uri, VOID["dataDump"], rdflib.URIRef(os.path.join(ftp, "dumps", version, "share.tar.gz"))))

#TODO add license, creator

# Browse recursively all directory inside the triplestore to extract all void.ttl files
all_void = glob.glob(os.path.join(args.path, "**", "void.ttl"), recursive = True)

# Parse files: 
for f_void in all_void:
    print("Integrate void file: " + f_void)
    g_void = rdflib.Graph()
    g_void.parse(f_void, format = 'turtle')
    master_void = master_void + g_void

# Add all subsets from meta graphs
all_meta_graphs = config['RELEASE'].get("graph").split('\n')
for g in all_meta_graphs:
    uri_g = rdflib.URIRef(g)
    versioned_graph = master_void.value(subject = uri_g, predicate = DCTERMS["hasVersion"])
    print("Integrate versioned resource " + str(versioned_graph) + " to the set of subsets")
    master_void.add((master_void_uri, VOID["subset"], versioned_graph))


master_void.serialize(destination = os.path.join(args.path, "void_" + version + ".ttl"), format='turtle')