import argparse, sys, os
import configparser
import subprocess
import rdflib
from sbml_processing_functions import *
from Id_mapping import Id_mapping
from download_functions import check_void
from Database_ressource_version import Database_ressource_version
from rdflib.namespace import RDF, RDFS, XSD, DCTERMS, VOID

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="path to the configuration file")
parser.add_argument("--out", help="path to output directory")
args = parser.parse_args()

# Intialyze attributes and paths: 

if not os.path.exists(args.config):
    print("Config file : " + args.config + " does not exist")
    sys.exit(3)

try:    
    config = configparser.ConfigParser()
    config.read(args.config)
except configparser.Error as e:
    print(e)
    sys.exit(3)

# Init
model_xml_path = config["SBML"].get("path")
sbml_version = config["SBML"].get("version")
path_to_dumps = args.out
meta_table = config["META"].get("path")
update_f_name = config["DEFAULT"].get("upload_file")
path_to_g_SBML =  config["RDF"].get("path")

# When converted in RDF
gem_file = os.path.basename(path_to_g_SBML)
gem_dir = os.path.dirname(path_to_g_SBML)


with open(os.path.join(path_to_dumps, update_f_name), "w") as update_f:
    pass

# Check if this version already exist by checkink the Intra-mapping void
intra_eq_uri = check_void(os.path.join(path_to_dumps, "Id_mapping", "Intra", "SBML", sbml_version, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/Id_mapping/Intra/SBML"))
sbml_uri = check_void(os.path.join(path_to_dumps, gem_dir, "void.ttl"), rdflib.URIRef("https://forum.semantic-metabolomics.org/SBML"))

if intra_eq_uri and sbml_uri:
    print("Skip computation, the resource already exists.")

# If not, create the resource 
else:
    
    # Check if the provided sbml is available
    if not glob.glob(model_xml_path):
        print("Can't find file at " + model_xml_path)
        sys.exit(3)

    # 1) Convert model xml to rdf
    
    if not os.path.exists(gem_dir):
        os.makedirs(gem_dir)
    if not os.path.exists(os.path.dirname(os.path.join(path_to_dumps,path_to_g_SBML))):
        os.makedirs(os.path.dirname(os.path.join(path_to_dumps, path_to_g_SBML)))

    # Create resource
    sbml = Database_ressource_version(ressource = "SBML", version = sbml_version)
    sbml_uri = str(sbml.uri_version)

    print("Convert " + model_xml_path + " to rdf ... ", end = '')
    try:
        subprocess.run("java -jar app/build/sbml2rdf/SBML2RDF.jar -i " + model_xml_path + " -o " + os.path.join(path_to_dumps, path_to_g_SBML) + " -u " + sbml_uri, shell = True, check = True, stderr = subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Error during trying to convert " + model_xml_path + " to rdf at " + os.path.join(path_to_dumps, path_to_g_SBML) + ", check .log")
        print(e)
        sys.exit(3)
    print("Ok")
    
    print("Create void.ttl ... ", end = '')
    # create void
    g = rdflib.Graph()
    g.parse(os.path.join(path_to_dumps, path_to_g_SBML), format = 'turtle')
    sbml.add_version_attribute(RDF["type"],  VOID["Dataset"])
    sbml.add_version_attribute(DCTERMS["description"], rdflib.Literal(config["VOID"].get("description")))
    sbml.add_version_attribute(DCTERMS["title"], rdflib.Literal(config["VOID"].get("title")))
    sbml.add_version_attribute(VOID["triples"], rdflib.Literal(len(g), datatype=XSD.long ))
    sbml.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(len(set([str(s) for s in g.subjects()]))))
    sbml.add_version_attribute(RDFS["seeAlso"], rdflib.Literal(config["VOID"].get("seeAlso")))
    sbml.add_version_attribute(DCTERMS["source"], rdflib.Literal(config["VOID"].get("source")))
    sbml.version_graph.serialize(os.path.join(path_to_dumps, gem_dir, "void.ttl"), format = 'turtle')
    print("Ok")

    # Intialyze Object:
    map_ids = Id_mapping(sbml_version)
    print("Import configuration table ... ", end = '')
    map_ids.import_table_infos(meta_table, "\t")
    print("OK\nImport identifiers from SBML rdf graph to create SBML URIs intra equivalences ... ", end = '')
    map_ids.get_graph_ids_set(os.path.join(path_to_dumps, path_to_g_SBML), sbml_uri, 'turtle')

    # Else create intra-mapping
    print("- SBML Intra-mapping")
    intra_eq_uri = map_ids.export_intra_eq(os.path.join(path_to_dumps, "Id_mapping", "Intra"), "SBML")
    print("Ok")

print("Export upload file")
with open(os.path.join(path_to_dumps, update_f_name), "a") as update_f:
    update_f.write("delete from DB.DBA.load_list ;\n")
    update_f.write("ld_dir_all ('./dumps/" + os.path.join(gem_dir, '') + "', '" + gem_file + "', '" + sbml_uri + "');\n")
    update_f.write("ld_dir_all ('./dumps/" + os.path.join(gem_dir, '') + "', '" + "void.ttl" + "', '" + sbml_uri + "');\n")
    update_f.write("ld_dir_all ('./dumps/" + os.path.join("Id_mapping", "Intra", "SBML", sbml_version, '') + "', '" + "*.ttl.gz" + "', '" + str(intra_eq_uri) + "');\n")
    update_f.write("ld_dir_all ('./dumps/" + os.path.join("Id_mapping", "Intra", "SBML", sbml_version, '') + "', '" + "void.ttl" + "', '" + str(intra_eq_uri) + "');\n")
    update_f.write("rdf_loader_run();\n")
    update_f.write("checkpoint;\n")
    update_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")