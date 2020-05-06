import requests
import os
import glob
import multiprocessing as mp
import pandas as pd
from sparql_queries import *





def parallelize_query_by_offset(count_id, query, prefix, header, data, url, limit_pack_ids, limit_selected_ids, out_path, n_processes):
    # Initialyze the pool
    pool = mp.Pool(processes = n_processes, maxtasksperchild = 20)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
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
    print(offset_list)
    # Apply send_query_by_offset in parallel respecting the number of processes fixed
    results = [pool.apply_async(send_query_by_offset, args=(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, 0, out_path)) for offset_pack_ids in offset_list]
    output = [p.get() for p in results]
    # Ended
    pool.close()
    pool.join()


def write_request(lines, out_name):
    if len(lines) > 0:
        # Remove the header 
        lines.pop(0)
        with open(out_name, "w") as out:
            for l in lines:
                out.write(l + "\n")

def send_query(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids):
    # Fill the query string with the associated parameters
    formated_query = prefix + query % (limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
    r_data = data
    r_data["query"] = formated_query
    r = requests.post(url = url, headers = header, data = r_data)
    return r

def send_query_by_offset(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids, out_path):
    """
    In this function limit_pack_ids, offset_pack_ids are fixed and only offset_selected_ids is increased if needed
    """
    n_f = 1
    out_name = out_path + "res_offset_%d_f_%d.csv" %(offset_pack_ids, n_f)
    # Send the query at defined pack_id offset, and with intial selected_id offset, 0.
    r = send_query(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
    # Test if request successed
    if r.status_code != 200:
        with open(out_path + "fail.log", "a") as log_fail:
            log_fail.write("%d_%d" % (offset_pack_ids, offset_selected_ids))
        # If the first request fail, we fake it succed so the will still check the superior offset
        test = True
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
        r = send_query(url, query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
        if r.status_code != 200:
            with open(out_path + "fail.log", "a") as log_fail:
                log_fail.write("%d_%d" % (offset_pack_ids, offset_selected_ids))
            # If the first request fail, we fake it succed so the will still check the superior offset
            test = True
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
    # In the first step, all files associated to the same offset are read, and then data.frame are concatenate
    print("Working on offset " + offset + " ...")
    df_list = [pd.read_csv(path, sep = ",", names=["ID", "PMID"], dtype="string") for path in glob.glob(path_in + "res_offset_" + offset + "_f_*.csv")]
    df_global = pd.concat(df_list)
    # Aggregate by ID
    agg = df_global.groupby('ID')['PMID'].agg(';'.join).reset_index(name='list_pmids')
    agg.to_csv(path_in + "res_offset_aggregate_" + offset + ".csv", index = False, header = False)

def send_counting_request(prefix, header, data, url, config, key):
    r_data = data
    print(config[key].get('Size_Request_name'))
    name = config[key].get('name')
    r_data["query"] = prefix + eval(config[key].get('Size_Request_name'))
    print("Counting total number of " + name + " ...")
    count_res = requests.post(url = url, headers = header, data = r_data)
    count = int(count_res.text.splitlines().pop(1))
    print("There are " + str(count) + " " + name)
    return count

def launch_from_config(prefix, header, data, url, config, key, out_path):
    # Get count:
    count = send_counting_request(prefix, header, data, url, config, key)
    out_path_dir = out_path + config[key].get('out_dir') + "/"
    print("Exporting in " + out_path_dir + " ...")
    request = eval(config[key].get('Request_name'))
    parallelize_query_by_offset(count, request, prefix, header, data, url, config[key].getint('limit_pack_ids'), config[key].getint('limit_selected_ids'), out_path_dir, config[key].getint('n_processes'))

def prepare_data_frame(config, path_to_COOC, path_to_X, path_to_Y, U_size, out_path, file_size):
    X_name = config['X'].get('name')
    Y_name = config['Y'].get('name')
    Individual_name = config['U'].get('name')
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    print("Import dataframes")
    df_cid_mesh_list = [pd.read_csv(path, sep = ",", names=[X_name, Y_name, "COOC"]) for path in glob.glob(path_to_COOC + "*")]
    cid_mesh = pd.concat(df_cid_mesh_list)
    df_cid_pmid_list = [pd.read_csv(path, sep = ",", names=[X_name, "TOTAL" + "_" + Individual_name + "_" + X_name]) for path in glob.glob(path_to_X + "*")]
    cid_pmid = pd.concat(df_cid_pmid_list)
    df_mesh_pmid_list = [pd.read_csv(path, sep = ",", names=[Y_name, "TOTAL" + "_" + Individual_name + "_" + Y_name]) for path in glob.glob(path_to_Y + "*")]
    mesh_pmid = pd.concat(df_mesh_pmid_list)
    print("Merge columns")
    # Step 1: merging total CID counts :
    data = cid_mesh.merge(cid_pmid, on = X_name, how = "left")
    # Step 2: merging total MESH counts :
    data = data.merge(mesh_pmid, on = Y_name, how = "left")
    # Step 3: Add total number of PMID
    data["TOTAL_" + Individual_name] = U_size
    df_size=len(data)
    for i, start in enumerate(range(0, df_size, file_size)):
        data[start:start+file_size].to_csv(out_path + 'metab2mesh_{}.csv'.format(i), index = False)
    return data