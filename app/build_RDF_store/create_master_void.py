import sys
import argparse
import os
import glob
import rdflib
from datetime import date
from rdflib.namespace import XSD, DCTERMS, RDF, VOID

# python3 app/build_RDF_store/create_master_void.py --path="./docker-virtuoso/share" --version="2021"

parser = argparse.ArgumentParser()
parser.add_argument("--path", help="path to the Virtuoso share directory")
parser.add_argument("--version", help="version of the triplestore")

args = parser.parse_args()

# Browse recursively all directory inside the triplestore to extract all void.ttl files
all_void = glob.glob(os.path.join(args.path, "**", "void.ttl"), recursive = True)

# Create Master Void :
master_void = rdflib.Graph()
master_void.bind("dcterms", rdflib.Namespace("http://purl.org/dc/terms/"))
master_void.bind("void", rdflib.Namespace("http://rdfs.org/ns/void#"))
master_void_uri = rdflib.URIRef("https://forum.semantic-metabolomics.org/void")

# Add VoID metadata:
master_void.add((master_void_uri, RDF['type'], VOID["DatasetDescription"]))
master_void.add((master_void_uri, DCTERMS['title'], rdflib.Literal("FORUM DiseaseChem RDF Dataset Description")))
master_void.add((master_void_uri, DCTERMS['description'], rdflib.Literal("This is the VoID description for FORUM DiseaseChem RDF datasets.")))
master_void.add((master_void_uri, DCTERMS["created"], rdflib.Literal(date.today().isoformat(), datatype=XSD.date)))

# Parse files: 
for f_void in all_void:
    print(f_void)
    g_void = rdflib.Graph()
    g_void.parse(f_void, format = 'turtle')
    master_void = master_void + g_void

# Export master void

master_void.serialize(destination = os.path.join(args.path, "void_" + args.version + ".ttl"), format='turtle')