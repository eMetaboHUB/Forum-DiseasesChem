import requests
import os

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
select ?CID ?MeSH ?count
where {
    {
    select (strbefore(strafter(STR(?CID_MeSH),\"http://database/ressources/metab2mesh/\"), \"_\") as ?CID) (strafter(STR(?CID_MeSH),\"_\") as ?MeSH) ?count where {
            ?CID_MeSH <http://database/ressources/metab2mesh/hasCount> ?count
        }
        order by ?CID_MeSH
    }
}
"""

url = "http://localhost:9980/sparql/"


def write_request(res, out_path, out_name, n_f, write_header):
    if res.status_code != 200:
        print("Request seems to failed !")
        return False
    lines = res.text.splitlines()
    if not write_header:
        lines.pop(0)
    with open(out_path + out_name + "_" + str(n_f) + ".csv", "w") as out:
        for l in lines:
            out.write(l + "\n")
    return True

def send_request(url, prefix, str_request, data, header, out_path, out_name, limit):
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    offset = 0
    n_f = 1
    data["query"] = prefix + str_request + "\nLIMIT " + str(limit) + "\nOFFSET " + str(offset)
    print("Send request at offset: " + str(offset))
    res = requests.post(url = url, headers = header, data = data)
    print("write results for file " + out_path + out_name + str(n_f))
    write_request(res, out_path, out_name, n_f, True)
    while len(res.text.splitlines()) == limit + 1:
        offset += limit
        n_f += 1
        data["query"] = prefix + str_request + "\nLIMIT " + str(limit) + "\nOFFSET " + str(offset)
        print("Send request at offset: " + str(offset))
        res = requests.post(url = url, headers = header, data = data)
        print("write results for file " + out_path + out_name + str(n_f))
        write_request(res, out_path, out_name, n_f, False)


# Extraction des CID - MESH
print("Extraction des CID - MESH ...")
send_request(url, prefix, distinct_pmid_by_CID_MeSH, data, header, "../data/metab2mesh/CID_MESH/", "metab2mesh_cid_mesh", 1000000)
print("Extraction des distincts pmids associés à chaque CID ...")
send_request(url, prefix, distinct_pmid_by_CID, data, header, "../data/metab2mesh/CID_PMID/", "metab2mesh_cid", 1000000)
print("Extraction des distincts pmids associés à chaque MeSH ...")
send_request(url, prefix, distinct_pmid_by_MeSH, data, header, "../data/metab2mesh/MeSH_PMID/", "metab2mesh_mesh", 1000000)
print("Extraction du nombre totals de distinct PMIDs ...")
send_request(url, prefix, distinct_all_pmids, data, header, "../data/metab2mesh/PMID/", "metab2mesh_tt", 1000000)

