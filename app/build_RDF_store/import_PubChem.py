import argparse, configparser, os, glob, sys, json, rdflib
sys.path.insert(1, 'app/')
from download_functions import ftp_con, download_pubChem, check_void, download_single_file, get_latest_from_void

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


# Init
PubChem_upload_file = config["DEFAULT"].get("upload_file")
PubChem_log_file =  config["DEFAULT"].get("log_file")
dir_ftp = json.loads(config["PUBCHEM"].get("dir_ftp"))
name = json.loads(config["PUBCHEM"].get("name"))
out_dir = json.loads(config["PUBCHEM"].get("out_dir"))
mask = json.loads(config["PUBCHEM"].get("mask"))
version = json.loads(config["PUBCHEM"].get("version"))
ftp = config["PUBCHEM"].get("ftp")
ftp_path_void = config["PUBCHEM"].get("ftp_path_void")

# Init upload file:
with open(os.path.join(args.out, PubChem_upload_file), "w") as upload_f:
    upload_f.write("delete from DB.DBA.load_list ;\n")

# Download void
dl_pubchem_log = os.path.join(args.log, PubChem_log_file)

with open(dl_pubchem_log, "w") as f_log:
    pass
# Download PubChem void and place it at $pubchem_original_void
pubchem_original_void = os.path.join(args.log, "PubChem_void.ttl")
con = ftp_con(ftp)
download_single_file(ftp_path_void, con, pubchem_original_void, dl_pubchem_log)
con.quit()

if not len(dir_ftp) == len(mask) == len(name) == len(out_dir) == len(version):
    print("Error: PUBCHEM options dir_ftp, mask, resource, out_dir, version don't have the same length, check config file.")
    sys.exit(3)

# For all specified subsets
n = len(dir_ftp)
for i in range(n):
    resource_out_dir = out_dir[i]
    resource_name = name[i]
    resource_dir_ftp = dir_ftp[i]
    resource_mask = mask[i]
    resource_version = version[i]
    
    # The URI of the resource that will be versioned
    meta_resource = rdflib.URIRef("https://forum.semantic-metabolomics.org/PubChem/" + resource_name)

    # if 'latest' was provided:
    if resource_version == "latest":

        # Determine the latest version avaiable
        resource_version = get_latest_from_void(pubchem_original_void)

        # Check if this latest version was already download
        path_to_void = os.path.join(args.out, resource_out_dir, resource_name, resource_version, "void.ttl")
        resource_uri = check_void(path_to_void, meta_resource)

        # If not, download from ftp
        if not resource_uri:
            print("PubChem " + resource_name + " version " + resource_version + " was not found, download.")
            resource_version, resource_uri = download_pubChem(resource_dir_ftp, resource_name, resource_version, ftp, pubchem_original_void, os.path.join(args.out, resource_out_dir), dl_pubchem_log)
    
    # if a version was provided
    else: 
        # Check if the version already exists:
        print("Check if " + resource_dir_ftp + " version " + resource_version + " exists")
        path_to_void = os.path.join(args.out, resource_out_dir, resource_name, resource_version, "void.ttl")
        resource_uri = check_void(path_to_void, meta_resource)
        if not resource_uri:
            print("PubChem Subset " + resource_dir_ftp + " version '" + resource_version  + "' was not found.")
            print("Provide a valid version or download the latest")
            sys.exit(3)
    
    # If a mask was provided, write in upload files
    if resource_mask:
        with open(os.path.join(args.out, PubChem_upload_file), "a") as upload_f:
            upload_f.write("ld_dir_all ('" + os.path.join("./dumps/", resource_out_dir, resource_name, resource_version, '') + "', '" + resource_mask + "', '" + resource_uri + "');\n")
            upload_f.write("ld_dir_all ('" + os.path.join("./dumps/", resource_out_dir, resource_name, resource_version, '') + "', 'void.ttl', '" + resource_uri + "');\n")

# Write footer
with open(os.path.join(args.out, PubChem_upload_file), "a") as upload_f:
    upload_f.write("select * from DB.DBA.load_list;\n")
    upload_f.write("rdf_loader_run();\n")
    upload_f.write("checkpoint;\n")
    upload_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")