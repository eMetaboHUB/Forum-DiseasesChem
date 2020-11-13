import pandas as pd
import argparse
import sys
import os.path
import configparser
import rdflib
import subprocess
sys.path.insert(1, 'app/')
from Database_ressource_version import Database_ressource_version
from rdflib.namespace import XSD, DCTERMS, RDFS, VOID, RDF


parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--c2mconfig", help="path to the configuration of the compound2MeSH analysis (metab2mesh_requesting_virtuoso)")
parser.add_argument("--c2mname", help="name of the raw ressource used in computation processes (eg. CID_MESH)")
parser.add_argument("--input", help="path to the input result table")
parser.add_argument("--version", help="Analysis version")
parser.add_argument("--out", help="path to output directory")
args = parser.parse_args()

# parser.add_argument("--uri", help="uri on the input table on the ftp")
# source = args.uri


if not os.path.exists(args.config):
    print("Config file : " + args.config + " does not exist")
    sys.exit(3)

try:    
    config = configparser.ConfigParser()
    config.read(args.config)
except configparser.Error as e:
    print(e)
    sys.exit(3)

# Get args
input_table_path = args.input
version = args.version
path_to_dumps = args.out
ftp = config['FTP'].get('ftp')
chunk_size = config['PARSER'].getint('chunk_size')
column_parsed = config['PARSER'].get('column')
threshold = config['PARSER'].getfloat('threshold')
ressource_name = config["METADATA"]["ressource"]
file_prefix = config['OUT'].get('file_prefix')

# sources
c2m_config = args.c2mconfig
c2m_name = args.c2mname

out_path = path_to_dumps + "/" + ressource_name + "/" + version + "/"

if not os.path.exists(out_path):
    os.makedirs(out_path)

# Namespaces
namespaces = {k:rdflib.Namespace(v) for k,v in zip(config['NAMESPACE'].get("name").split('\n'), config['NAMESPACE'].get("ns").split('\n'))}

# ON fait pareil pour les sujets et les objets
namespace_s = namespaces[config['SUBJECTS'].get('namespace')]
namespace_o = namespaces[config['OBJECTS'].get('namespace')]
prefix_s = config['SUBJECTS'].get('prefix')
prefix_o = config['OBJECTS'].get('prefix')
predicate = namespaces[config['PREDICATES'].get('namespace')][config['PREDICATES'].get('name')]

# On récupère les colonnes des sujets et des objets
L = list([config['SUBJECTS'].get('name'), config['OBJECTS'].get('name')])

# Test if input file exists:
if not os.path.exists(input_table_path):
    print("The input table at " + input_table_path + " does not exists")
    sys.exit(3)

# Intialyze graph :
ressource = Database_ressource_version(ressource = ressource_name, version = version)
g = ressource.create_data_graph(namespaces.keys(), namespaces)
f_i = 1

# Intialyze counts:
n_subjects = 0
n_objects = 0

# a = requests.put("https://pfem.clermont.inra.fr/pydio/public/7af464/test.csv", data=open("data/metab2mesh/with_Mesh_Thesaurus/2020-07-07/tutu.csv", 'r').read(), auth=("none","F0rum_p455w0rd"))

print("Starting read file by chunk of size " + str(chunk_size))
df_chunk = pd.read_csv(input_table_path, chunksize=chunk_size)
for chunk in df_chunk:
    print("Filtering chunk ... ", end = '')
    filtered_data = chunk[(chunk[column_parsed] <= threshold)]
    filtered_data = filtered_data[L]
    print("Ok\nConverting data to triples ... ", end = '')
    for i in range(len(filtered_data)):
        g.add((namespace_s[prefix_s + str(filtered_data.iloc[i, 0])], predicate, namespace_o[prefix_o + str(filtered_data.iloc[i, 1])]))
    if(len(g) > 1000000):
        print("Ok\n1000000 triples limit reach, start serialyze graph ... ", end = '')
        # On ajoute les comptages pour les metadata
        n_subjects += len(set([str(s) for s in g.subjects()]))
        n_objects += len(g)
        g.serialize(destination=out_path + "/" + file_prefix + "_" + str(f_i) + ".trig", format='trig')
        ressource.add_DataDump(file_prefix + "_" + str(f_i) + ".trig.gz", ftp)
        g = ressource.create_data_graph(namespaces.keys(), namespaces)
        f_i += 1

# On serialyze le dernier graph :
if(len(g)) != 0:
    print("Ok\nStart serialyzing last graph ... ", end = '')
    n_subjects += len(set([str(s) for s in g.subjects()]))
    n_objects += len(g)
    g.serialize(destination=out_path + "/" + file_prefix + "_" + str(f_i) + ".trig", format='trig')
    ressource.add_DataDump(file_prefix + "_" + str(f_i) + ".trig.gz", ftp)
    print("Ok\n")

# On zip
try:
    subprocess.run("gzip -f " + out_path + "/" + file_prefix + "_*.trig", shell = True, check=True, stderr = subprocess.PIPE)
except subprocess.CalledProcessError as e:
    print("Error while trying to compress files at " + out_path + "/" + file_prefix + "_*.trig : " + str(e))
    sys.exit(3)

print("Export Metadata ... ")
ressource.add_version_attribute(RDF["type"], VOID["Linkset"])
for uri_targeted_ressource in config['METADATA'].get("targets").split('\n'):
    ressource.add_version_attribute(VOID["target"], rdflib.URIRef(uri_targeted_ressource))
ressource.add_version_attribute(VOID["triples"], rdflib.Literal(n_objects, datatype=XSD.long))
ressource.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(n_subjects, datatype=XSD.long))
ressource.add_version_attribute(DCTERMS["description"], rdflib.Literal("For more information about this analysis, please refer to the configuration file on repository at : " + args.config + ". You can also find the initial table of results on the ftp server at " + ftp + "."))
ressource.add_version_attribute(DCTERMS["title"], rdflib.Literal("This graph contains significant associations between " + L[0] + " and " + L[1] + " using a threshold on " + column_parsed + " at " + str(threshold)))

# Sources 
# Needed namespaces
ns = {"dcat":rdflib.Namespace("http://www.w3.org/ns/dcat#")}
# Creation of the ressource
c2m_ressource = Database_ressource_version(ressource = c2m_name, version = version)
c2m_ressource.add_version_namespaces(["dcat"], ns)
c2m_ressource.add_version_attribute(RDF["type"], ns["dcat"]["Dataset"])
uri_distribution = c2m_ressource.uri_version + "/data"
c2m_ressource.add_version_attribute(ns["dcat"]["distribution"], uri_distribution)
c2m_ressource.version_graph.add((uri_distribution, RDF["type"], ns["dcat"]["Distribution"]))
c2m_ressource.version_graph.add((uri_distribution, ns["dcat"]["downloadURL"], rdflib.URIRef(ftp + c2m_name + "/" + version + "/r_fisher_q_w.csv")))
c2m_ressource.version_graph.add((uri_distribution, ns["dcat"]["mediaType"], rdflib.URIRef("text/csv")))
# Parse config of computation processes to retrieve source graphs
c2m = configparser.ConfigParser()
c2m.read(c2m_config)
for g in c2m['VIRTUOSO'].get("graph_from").split('\n'):
    c2m_ressource.add_version_attribute(DCTERMS["source"], rdflib.URIRef(g))
ressource.add_version_attribute(DCTERMS["source"], c2m_ressource.uri_version)
ressource.version_graph = ressource.version_graph + c2m_ressource.version_graph

ressource.version_graph.serialize(destination= out_path + "void.ttl", format='turtle')

print("Ok\nExport upload_file ... ", end = '')
with open(path_to_dumps + "/" + "upload_Enrichment_" + config['SUBJECTS'].get('name') + "_" + config['OBJECTS'].get('name') + ".sh", "w") as upload_f:
    upload_f.write("delete from DB.DBA.load_list ;\n")
    upload_f.write("ld_dir_all ('./dumps/" + ressource_name + "/" + version + "/', '*.trig.gz', '');\n")
    upload_f.write("ld_dir_all ('./dumps/" + ressource_name + "/" + version + "/', 'void.ttl', '" + str(ressource.uri_version) + "');\n")
    upload_f.write("select * from DB.DBA.load_list;\n")
    upload_f.write("rdf_loader_run();\n")
    upload_f.write("checkpoint;\n")
    upload_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")
print("Ok")