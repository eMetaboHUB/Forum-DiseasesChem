import glob, requests

def create_update_file_from_ressource(path_out, path_to_graph_dir):
    """
    This function is used to load graph which represent a ressource, with one or several .trig files associated to data graph and one ressource_info_**.ttl file describing the ressource
    """
    with open(path_out + 'update.sh', "w") as update_f:
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', '*.trig', '');\n")
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', 'ressource_info_*.ttl', 'http://database/ressources');\n")
        update_f.write("rdf_loader_run();\n")
        update_f.write("checkpoint;\n")
        update_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")

def create_update_file_from_graph_dir(path_out, path_to_graph_dir):
    """
    This function is used to load grpah from a directory, the URI of each graph must be indicated using a <source-file>.<ext>.graph file containing the URI (Cf.http://vos.openlinksw.com/owiki/wiki/VOS/VirtBulkRDFLoader)
    """
    with open(path_out + 'update.sh', "w") as update_f:
        update_f.write("ld_dir_all ('./dumps/" + path_to_graph_dir + "', '*.ttl', '');\n")
        update_f.write("rdf_loader_run();\n")
        update_f.write("checkpoint;\n")
        update_f.write("select * from DB.DBA.LOAD_LIST where ll_error IS NOT NULL;\n")

def test_if_graph_exists(url, graph_uri):
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html"
    }
    data = {
        "format": "html",
        "query": "ASK WHERE { GRAPH <" + graph_uri + "> { ?s ?p ?o } }"
    }
    r = requests.post(url = url, headers = header, data = data)
    if r.text == "true":
        return True
    return False

def request_annotation(url, query, sbml_uri, annot_graph_uri, version, header, data):
    data["query"] = query %(version, sbml_uri, "\n".join(["FROM <" + uri + ">" for uri in annot_graph_uri]))
    r = requests.post(url = url, headers = header, data = data)
    print(r.text)
    if r.status_code != 200:
        return False
    return True