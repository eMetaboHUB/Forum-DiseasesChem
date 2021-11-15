import argparse, configparser, os, glob, sys, json, rdflib
sys.path.insert(1, 'app/')
from download_functions import get_latest_from_MDTM, download_MeSH, check_void

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

# init
mesh_out_dir = "MeSH"
mesh_upload_file = config["DEFAULT"].get("upload_file")
mesh_log_file = config["DEFAULT"].get("log_file")
mesh_version = config["MESH"].get("version")
ftp = config["MESH"].get("ftp")
ftp_path_mesh = config["MESH"].get("ftp_path_mesh")
ftp_path_void = config["MESH"].get("ftp_path_void")

# Intialyze .log files
log_path = os.path.join(args.log, mesh_log_file)
with open(log_path, "w") as f_log:
    pass

meta_resource = rdflib.URIRef("https://forum.semantic-metabolomics.org/MeSHRDF")

# if 'latest' was provided:
if mesh_version == "latest":
    # Get the latest version
    mesh_version = get_latest_from_MDTM(ftp, ftp_path_mesh, log_path)
    
    # Check is the latest version was already downloaded
    path_to_void = os.path.join(args.out, mesh_out_dir, mesh_version, "void.ttl")
    mesh_uri = check_void(path_to_void, meta_resource)

    # If not, download from ftp
    if not mesh_uri:
        print("MeSH version " + mesh_version + " was not found, download.")
        mesh_version, mesh_uri = download_MeSH(os.path.join(args.out, mesh_out_dir), mesh_version, ftp, ftp_path_void, ftp_path_mesh, log_path, args.log)

# if a version was provided
else:
    # Check if this version has already been created
    print("Version '" + mesh_version + "' was provided for MeSH")
    path_to_void = os.path.join(args.out, mesh_out_dir, mesh_version, "void.ttl")
    mesh_uri = check_void(path_to_void, meta_resource)

    # If not, exit
    if not mesh_uri:
        print("MeSH version " + mesh_version + "' was not found.")
        print("Provide a valid version or download the latest")
        sys.exit(3)

# Write upload files
with open(os.path.join(args.out, mesh_upload_file), "a") as upload_f:
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/", mesh_out_dir, mesh_version, '') + "', 'mesh.nt', '" + mesh_uri + "');\n")
    upload_f.write("ld_dir_all ('" + os.path.join("./dumps/", mesh_out_dir,  mesh_version, '') + "', 'void.ttl', '" + mesh_uri + "');\n")