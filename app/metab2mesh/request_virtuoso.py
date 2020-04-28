import requests
import os
import multiprocessing as mp

header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/csv"
}
data = {
    "format": "csv",
}

prefix = """
    DEFINE input:inference \"schema-inference-rules\"
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
    PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
    PREFIX voc: <http://myorg.com/voc/doc#>
    prefix cito: <http://purl.org/spar/cito/>
    prefix fabio:	<http://purl.org/spar/fabio/> 
    prefix owl: <http://www.w3.org/2002/07/owl#> 
    prefix void: <http://rdfs.org/ns/void#>
    prefix cid:   <http://rdf.ncbi.nlm.nih.gov/pubchem/compound/>
"""

distinct_pmid_by_CID = """
select ?CID ?count
where{
    {
    select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (count(distinct ?pmid) as ?count) where {
            ?cid cito:isDiscussedBy ?pmid .
            ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
            ?mesh a meshv:TopicalDescriptor .
            ?mesh meshv:treeNumber ?tn .
            FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
        }
        group by ?cid
        order by ?cid
    }
}
"""
distinct_pmid_by_MeSH = """
select ?MESH ?count
where{
    {
        select (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) where {
            ?cid cito:isDiscussedBy ?pmid .
            ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
            ?mesh a meshv:TopicalDescriptor .
            ?mesh meshv:treeNumber ?tn .
            FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
        }
        group by ?mesh
        order by ?mesh
    }
}
"""

distinct_all_pmids = """
    select (count(distinct ?pmid) as ?count) where {
        ?cid cito:isDiscussedBy ?pmid .
        ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
        ?mesh a meshv:TopicalDescriptor .
        ?mesh meshv:treeNumber ?tn .
        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
    }
"""

distinct_pmid_by_CID_MeSH = """
select ?CID ?MESH ?count
where
{
    {
        select ?CID ?MESH ?count
        where 
        {
                {
                    select (strafter(STR(?cid),\"http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID\") as ?CID) (strafter(STR(?mesh),\"http://id.nlm.nih.gov/mesh/\") as ?MESH) (count(distinct ?pmid) as ?count) 
                    where {
                        {
                            select ?cid where {
                                {
                                    select distinct ?cid where {
                                        ?cid cito:isDiscussedBy ?pmid .
                                    }
                                    order by ?cid
                                }
                            }
                            limit %d
                            offset %d
                        }
                        ?cid cito:isDiscussedBy ?pmid .
                        ?pmid fabio:hasSubjectTerm|fabio:hasSubjectTerm/meshv:hasDescriptor ?mesh .
                        ?mesh a meshv:TopicalDescriptor .
                        ?mesh meshv:treeNumber ?tn .
                        FILTER(REGEX(?tn,\"(C|A|D|G|B|F|I|J)\"))
                    }
                    group by ?cid ?mesh
                } 
            bind(uri(concat(\"http://database/ressources/metab2mesh/\", ?CID, \"_\", ?MESH)) as ?id)
        }
        order by ?id
    }
}
limit %d
offset %d
"""

url = "http://localhost:9980/sparql/"


def parallelize_query_by_offset(count_id, query, prefix, header, data, url, limit_pack_ids, limit_selected_ids, out_path, n_processes):
    pool = mp.Pool(processes=n_processes)
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    # First step is to get the total number of cid: 
    # Getting the number of CID, we can prepare the pack of cids respecting limit_size
    n_offset = count_id // limit_pack_ids
    offset_list = [i * limit_pack_ids for i in range(0, n_offset + 1)]
    print(offset_list)
    results = [pool.apply_async(send_query_by_offset, args=(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, 0, out_path)) for offset_pack_ids in offset_list]
    output = [p.get() for p in results]
    os.system("cat " + out_path + "* >> " + out_path + "res_full.csv")

def write_request(lines, out_name):
    if len(lines) > 0:
        lines.pop(0)
        with open(out_name, "w") as out:
            for l in lines:
                out.write(l + "\n")

def send_query(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids):
    formated_query = prefix + query % (limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
    data["query"] = formated_query
    r = requests.post(url = url, headers = header, data = data)
    return r

def send_query_by_offset(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids, out_path):
    """
    In this function limit_pack_ids, offset_pack_ids are fixed and only offset_selected_ids is increased if needed
    """
    n_f = 1
    out_name = out_path + "res_offset_%d_f_%d.csv" %(offset_pack_ids, n_f)
    r = send_query(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
    if r.status_code != 200:
        with open(out_path + "fail.log", "a") as log_fail:
            log_fail.write("%d_%d" % (offset_pack_ids, offset_selected_ids))
        # If the first request fail, we fake it succed so the will still check the superior offset
        test = True
    else:
        print("Request succed !")
        lines = r.text.splitlines()
        write_request(lines, out_name)
        test = (len(lines) == limit_selected_ids)
    while test:
        print("Limit reach, trying next offset ... ")
        offset_selected_ids += limit_selected_ids
        n_f += 1
        out_name = out_path + "res_offset_%d_f_%d.csv" %(offset_pack_ids, n_f)
        r = send_query(query, prefix, header, data, limit_pack_ids, offset_pack_ids, limit_selected_ids, offset_selected_ids)
        if r.status_code != 200:
            with open(out_path + "fail.log", "a") as log_fail:
                log_fail.write("%d_%d" % (offset_pack_ids, offset_selected_ids))
            # If the first request fail, we fake it succed so the will still check the superior offset
            test = True
            continue
        lines = r.text.splitlines()
        write_request(lines, out_name)
        test = (len(lines) == limit_selected_ids + 1)
    return True


count_cid_query = prefix + """
    select (count(distinct ?cid) as ?count_CID) where {
    ?cid cito:isDiscussedBy ?pmid .
}
"""
data["query"] = count_cid_query
count_cid_res = requests.post(url = url, headers = header, data = data)
count_cid = int(count_cid_res.text.splitlines().pop(1))