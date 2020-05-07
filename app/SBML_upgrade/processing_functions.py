import glob


def create_update_file(path_out, path_to_graph_dir):
    with open(path_out + 'update.sh', "w") as update_f:
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', '*.trig', '');\n")
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', '*.ttl', 'http://database/ressources/');\n")
        update_f.write("rdf_loader_run();\n")
        update_f.write("checkpoint;\n")
        update_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")