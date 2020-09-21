import requests
import os
import sys
import glob
import multiprocessing as mp
import pandas as pd
import importlib
import sys





def parallelize_query_by_offset(count_id, query, prefix, header, data, url, limit_pack_ids, limit_selected_ids, out_path, n_processes, graph_from):
    """
    This function is used to launch a SPARQL request in parralel according to config file parameters.
    To be parralelize, the total number of modalities for one of the two studied variable (named the grouping variable) need to be cut in smaller groups. the number of groups is determine from the total number of modalities and the fixed group size.
    - count_id: the total number of modalities for the grouping variable
    - query: a string associated to the query with offset and limit prepared to be filled and incremented
    - header: the header dict for the request
    - data: the data dict for the request
    - url: the Virtuoso SPARQL endpoint url
    - limit_pack_ids: the fixed maximal size of each group of ids from the grouping variable
    - limit_selected_ids: the fixed maximal number of lines that have to be exported by Virtuoso, manage the pagination (Virutoso max is 2^20)
    - out_path: path to the output directory
    - n_processes: the maximal number of processes, determining the number of queries send in parallel
    - graph_from: a list of uris associated to the sources grpahs containing needed data for the query
    """
    # Initialyze the pool
    pool = mp.Pool(processes = n_processes, maxtasksperchild = 20)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    # Initialyze .log file
    with open(out_path + "requests.log", "w") as f_log:
        pass
    # First step is to get the total number of cid: 
    # Getting the number of CID, we can prepare the pack of cids respecting limit_size
    if limit_pack_ids > count_id:
        print("limit_pack_ids is bigger than the total number of individuals (" + str(count_id) + "), query will not be send in parallel !")
        n_offset = 1
    else:
        n_offset = count_id // limit_pack_ids
        if (count_id % limit_pack_ids) > 0:
            n_offset += 1
    offset_list = [i * limit_pack_ids for i in range(0, n_offset)]
    print(str(len(offset_list)) + " offset(s) will be computed using " + str(n_processes) + " processes")
    # Apply send_query_by_offset in parallel respecting the number of processes fixed
    results = [pool.apply_async(send_query_by_offset, args=(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, 0, graph_from, out_path)) for offset_pack_ids in offset_list]
    output = [p.get() for p in results]
    # Ended
    pool.close()
    pool.join()


def write_request(lines, out_name):
    """
    This function is used to write lines in the output file
    - lines: a list of lines, by default the result of the SPARQL query
    - out_name: path to the output file
    """
    if len(lines) > 0:
        # Remove the header 
        lines.pop(0)
        with open(out_name, "w") as out:
            for l in lines:
                out.write(l + "\n")

def send_query(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids, graph_from):
    """
    The function which is used to send the query
    - url: the Virtuoso SPARQL endpoint url
    - query: a string associated to the query with offset and limit prepared to be filled and incremented
    - prefix: a string representing prefix of the SPARQL query
    - header: the header dict for the request
    - data: the data dict for the request
    - limit_pack_ids: the fixed maximal size of each group of ids from the grouping variable
    - offset_pack_ids: the offset in identifiers of the grouping variable, used to determine the group of treated identifiers by the request. For example, offset_pack_ids = 10000 and limit_pack_ids = 1000 implies that the 10001th ids to the 11000th will be treated
    - limit_selected_ids: the fixed maximal number of lines that have to be exported by Virtuoso, manage the pagination (Virutoso max is 2^20)
    - offset_selected_ids: same as offset_pack_ids but to deal with pagination of results. For example, offset_pack_ids = 1000000 and limit_pack_ids = 1000000 implies that Virtuoso will return results from the 1000001th lines to at most the 2000000th lines
    - graph_from: a list of uris associated to the sources grpahs containing needed data for the query
    """
    # Fill the query string with the associated parameters
    formated_query = prefix + query % (graph_from, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
    r_data = data
    r_data["query"] = formated_query
    r = requests.post(url = url, headers = header, data = r_data)
    return r

def send_query_by_offset(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids, graph_from, out_path):
    """
    This function is used to treat to treat a request results and to re-send the query with the next pagination offset if needed.
    - url: the Virtuoso SPARQL endpoint url
    - query: a string associated to the query with offset and limit prepared to be filled and incremented
    - prefix: a string representing prefix of the SPARQL query
    - header: the header dict for the request
    - data: the data dict for the request
    - limit_pack_ids: the fixed maximal size of each group of ids from the grouping variable (fixed here !)
    - offset_pack_ids: the offset in identifiers of the grouping variable, used to determine the group of treated identifiers by the request. For example, offset_pack_ids = 10000 and limit_pack_ids = 1000 implies that the 10001th ids to the 11000th will be treated (fixed here !)
    - limit_selected_ids: the fixed maximal number of lines that have to be exported by Virtuoso, manage the pagination (Virutoso max is 2^20)
    - offset_selected_ids: same as offset_pack_ids but to deal with pagination of results. For example, offset_pack_ids = 1000000 and limit_pack_ids = 1000000 implies that Virtuoso will return results from the 1000001th lines to at most the 2000000th lines
    - graph_from: a list of uris associated to the sources grpahs containing needed data for the query
    """
    n_f = 1
    out_name = out_path + "res_offset_%d_f_%d.csv" %(offset_pack_ids, n_f)
    # Send the query at defined pack_id offset, and with intial selected_id offset, 0.
    r = send_query(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids, graph_from)
    # Test if request successed
    if r.status_code != 200:
        print("Error in request at offset pack %d and offset pagination %d, request status code = %d.\nOffsets added to list_fail.log\nCheck requests.log\n" %(offset_pack_ids, offset_selected_ids, r.status_code))
        with open(out_path + "requests.log", "a") as log_fail:
            log_fail.write("for offset pack %d at offset pagination %d :\n" % (offset_pack_ids, offset_selected_ids))
            log_fail.write(r.text + "\n")
        with open(out_path + "list_fail.log", "a") as list_fail:
            list_fail.write("%d\t%d\n" % (offset_pack_ids, offset_selected_ids))
        test = False
    else:
        print("Request succed !")
        # Parse and write lines
        lines = r.text.splitlines()
        # After parsing, r is clean
        r = None
        write_request(lines, out_name)
        # When writing, the header is remove so the number of lines to check is exactly limit_selected_ids
        test = (len(lines) == limit_selected_ids)
        # After testing, lines are clean:
        lines = None
    while test:
        # If the number of lines equals the setted limit, it may reveals that there are remaining lines, increase offset by limit to get them.
        print("Limit reach, trying next offset ... ")
        offset_selected_ids += limit_selected_ids
        n_f += 1
        out_name = out_path + "res_offset_%d_f_%d.csv" %(offset_pack_ids, n_f)
        # Send request
        r = send_query(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids, graph_from)
        if r.status_code != 200:
            print("Error in request at offset pack %d and offset pagination %d, request status code = %d.\nOffsets added to list_fail.log\nCheck requests.log\n" %(offset_pack_ids, offset_selected_ids, r.status_code))
            with open(out_path + "requests.log", "a") as log_fail:
                log_fail.write("for offset pack %d at offset pagination %d :\n" % (offset_pack_ids, offset_selected_ids))
                log_fail.write(r.text + "\n")
            with open(out_path + "list_fail.log", "a") as list_fail:
                list_fail.write("%d\t%d\n" % (offset_pack_ids, offset_selected_ids))
            test = False
            continue
        lines = r.text.splitlines()
        # After testing, lines are clean:
        r = None
        # Export files
        write_request(lines, out_name)
        # Test if it was the last
        test = (len(lines) == limit_selected_ids)
        # After testing, lines are clean:
        lines = None
    return True

def build_PMID_list_by_CID_MeSH(count_id, limit_pack_ids, path_in, n_processes):
    """
    This function is used to call the aggregate_pmids_by_id function in parallel
    - count_id: the total number of modalities for the grouping variable (need to be the same as used for CID_MESH_PMID_LIST)
    - limit_pack_ids: the fixed maximal size of each group of ids from the grouping variable (need to be the same as used for CID_MESH_PMID_LIST)
    - out_path: path to the output directory
    - n_processes: the maximal number of processes, determining the number of queries send in parallel
    """
    # get all offset
    if limit_pack_ids > count_id:
        n_offset = 1
    else:
        n_offset = count_id // limit_pack_ids
        if (count_id % limit_pack_ids) > 0:
            n_offset += 1
    offset_list = [i * limit_pack_ids for i in range(0, n_offset)]
    pool = mp.Pool(processes = n_processes, maxtasksperchild = 20)
    results = [pool.apply_async(aggregate_pmids_by_id, args=(path_in, str(offset))) for offset in offset_list]
    output = [p.get() for p in results]
    # Close Pool
    pool.close()
    pool.join()

def aggregate_pmids_by_id(path_in, offset):
    """
    This function is used to process results of the SPARQL query CID_MESH_PMID_LIST to create a list of PMID separated by a ';' for each outputed combination of CID and MESH.
    - path_in: path to the directory containing the res_offset_* files for the CID_MESH_PMID_LIST query
    - offset: the treated offset
    """
    # In the first step, all files associated to the same offset are read, and then data.frame are concatenate
    print("Working on offset " + offset + " ...")
    df_list = [pd.read_csv(path, sep = ",", names=["ID", "PMID"], dtype="string") for path in glob.glob(path_in + "res_offset_" + offset + "_f_*.csv")]
    df_global = pd.concat(df_list)
    # Aggregate by ID
    agg = df_global.groupby('ID')['PMID'].agg(';'.join).reset_index(name='list_pmids')
    agg.to_csv(path_in + "res_offset_aggregate_" + offset + ".csv", index = False, header = False)

def send_counting_request(prefix, header, data, url, config, key, module):
    """
    This function is used to send a counting query to determine the total number of modalities for a variable (count_id)
    - url: the Virtuoso SPARQL endpoint url
    - query: a string associated to the query with offset and limit prepared to be filled and incremented
    - prefix: a string representing prefix of the SPARQL query
    - config: a configParser object containing parameters for each process
    - key: the name of a section in the configParser object associated to a task
    - header: the header dict for the request
    - data: the data dict for the request
    - module: a module from import_request_file corresponding to a sparql queries file
    """
    r_data = data
    name = config[key].get('name')
    try:
        query = getattr(module, config[key].get('Size_Request_name'))
    except NameError as e:
        print("Specified request name \"" + config[key].get('Size_Request_name') + "\" seems not to exists in the sparql query file, exit.")
        print("Error : " + str(e))
        sys.exit(3)
    graph_from = "\n".join(["FROM <" + uri + ">" for uri in config['VIRTUOSO'].get("graph_from").split('\n')])
    r_data["query"] = prefix + query %(graph_from)
    print("Counting total number of " + name + " ...")
    count_res = requests.post(url = url, headers = header, data = r_data)
    if count_res.status_code != 200:
        print("Error in request " + config[key].get('Size_Request_name') + ", request status code = " + str(count_res.status_code) + "\nImpossible to continue without total counts, exit.\n")
        print(count_res.text)
        sys.exit(3)
    count = int(count_res.text.splitlines().pop(1))
    print("There are " + str(count) + " " + name)
    return count

def launch_from_config(prefix, header, data, url, config, key, out_path, module):
    """
    This functin is used to launch a query from the specified paramteres set in the config file.
    - prefix: a string representing prefix of the SPARQL query
    - header: the header dict for the request
    - data: the data dict for the request
    - url: the Virtuoso SPARQL endpoint url
    - config: a configParser object containing parameters for each process
    - key: the name of a section in the configParser object associated to a task
    - out_path: path to the output directory
    - module: a module from import_request_file corresponding to a sparql queries file
    """
    # Get count:
    count = send_counting_request(prefix, header, data, url, config, key, module)
    out_path_dir = out_path + config[key].get('out_dir') + "/"
    print("Exporting in " + out_path_dir + " ...")
    try:
        request = getattr(module, config[key].get('Request_name')) 
    except NameError as e:
        print("Specified request name \"" + config[key].get('Request_name') + "\" seems not to exists in the sparql query file, exit.")
        print("Error : " + str(e))
        sys.exit(3)
    graph_from = "\n".join(["FROM <" + uri + ">" for uri in config['VIRTUOSO'].get("graph_from").split('\n')])
    parallelize_query_by_offset(count, request, prefix, header, data, url, config[key].getint('limit_pack_ids'), config[key].getint('limit_selected_ids'), out_path_dir, config[key].getint('n_processes'), graph_from)

def prepare_data_frame(config, path_to_COOC, path_to_X, path_to_Y, path_to_U, out_path, split):
    """
    This function is used to build the final data.frame containg all results for next computation. As this table can be really huge and post processes need also to be parallelized, the table is separated in sub-table with a number of lines fixed by file_size.
    Columns are: Modalities of X, Modalities of Y, Total number of individuals with modality X and Y, Total number of individuals with modality X, Total number of individuals with modality Y, Total number of individuals. 
    - config: a configParser object containing parameters for each process
    - path_to_COOC: path to coocurences directory
    - path_to_X: path to counts for modalities X directory
    - path_to_Y: path to counts for modalities Y directory
    - U_size: the total number of individuals
    - out_path: path to the output directory
    - split: bool (True/False) if the result file must be splited in smaller files. File size is set with the file_size config attribute.
    """
    X_name = config['X'].get('name')
    Y_name = config['Y'].get('name')
    Individual_name = config['U'].get('name')
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    print("Import dataframes")
    df_cid_mesh_list = [pd.read_csv(path, sep = ",", names=[X_name, Y_name, "COOC"]) for path in glob.glob(path_to_COOC + "*.csv")]
    cid_mesh = pd.concat(df_cid_mesh_list)
    df_cid_pmid_list = [pd.read_csv(path, sep = ",", names=[X_name, "TOTAL" + "_" + Individual_name + "_" + X_name]) for path in glob.glob(path_to_X + "*.csv")]
    cid_pmid = pd.concat(df_cid_pmid_list)
    df_mesh_pmid_list = [pd.read_csv(path, sep = ",", names=[Y_name, "TOTAL" + "_" + Individual_name + "_" + Y_name]) for path in glob.glob(path_to_Y + "*.csv")]
    mesh_pmid = pd.concat(df_mesh_pmid_list)
    df_univers_list = [pd.read_csv(path, sep = ",", names=["COUNT"]) for path in glob.glob(path_to_U + "*.csv")]
    df_univers = pd.concat(df_univers_list)
    U_size = df_univers["COUNT"].sum()
    print("Merge columns")
    # Step 1: merging total CID counts :
    data = cid_mesh.merge(cid_pmid, on = X_name, how = "left")
    # Step 2: merging total MESH counts :
    data = data.merge(mesh_pmid, on = Y_name, how = "left")
    # Step 3: Add total number of PMID
    data["TOTAL_" + Individual_name] = U_size
    df_size=len(data)
    # Write the metadata file :
    with open(out_path + "metadata.txt", "w") as metadata_f:
        metadata_f.write("Number of %s: %d\n" %(X_name, len(cid_pmid)))
        metadata_f.write("Number of %s: %d\n" %(Y_name, len(mesh_pmid)))
        metadata_f.write("Number of individuals %s: %d\n" %(Individual_name, U_size))
        metadata_f.write("Number of available coocurences between %s and %s: %d\n" %(X_name, Y_name, len(cid_mesh)))
        graph_from = ", ".join(["<" + uri + ">" for uri in config['VIRTUOSO'].get("graph_from").split('\n')])
        metadata_f.write("List of sources graph :%s\n" %(graph_from))
    # If split = True, the result file in split in n several files with a size of file_size
    if split:
        file_size = config['DEFAULT'].getint('file_size')
        for i, start in enumerate(range(0, df_size, file_size)):
            data[start:start+file_size].to_csv(out_path + 'metab2mesh_{}.csv'.format(i), index = False)
    # The result is fully writen on one file
    else:
        data.to_csv(out_path + 'metab2mesh.csv', index = False)
    return data

def ask_for_graph(url, graph_uri):
    """
    This function is used to test if graph a exist without erase
    - url: the Virtuoso SPARQL endpoint url
    - graph_uri: the URI of the graph to test
    """
    header = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html"
    }
    data = {
        "format": "html",
        "query": "ASK WHERE { GRAPH <" + graph_uri + "> { ?s ?p ?o } }"
    }
    r = requests.post(url = url, headers = header, data = data)
    if r.status_code != 200:
        print("Error in request while trying to check if all needed graphs exists.\nImpossible to continue, exit.\n")
        print(r.text)
        sys.exit(3)
    if r.text == "true":
        return True
    return False

def import_request_file(file_name):
    """
    This function is used to load a sparql queries file as a module and return it.
    -file_name: name of the sparql queries file in the dedicated SPARQL directory
    """
    try:
        module = importlib.import_module('SPARQL.' + file_name)
    except Exception as e:
        print("Error while trying to import sparql queries file : " + file_name)
        print(e)
        sys.exit(3)
    return module