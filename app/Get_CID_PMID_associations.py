# Importing packages
# Using Package eutils 0.6.0
import eutils
import xml.etree.ElementTree as ET
from Pccompound import Pccompound
from Pmid import Pmid


apiKey = "0ddb3479f5079f21272578dc6e040278a508"
# Building request
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)
# Get CID associated PMID
response = query_builder.elink({"dbfrom": "pccompound", "db": "pubmed", "id": "6036"})
# parsing XML
root = ET.fromstring(response)
# For each CID - PMIS association source: "pccompound_pubmed", "pccompound_pubmed_mesh", "pccompound_pubmed_publisher"
pmids_by_source = {}
# Exploring sets
for pmid_set in root.findall("./LinkSet/LinkSetDb"):
    # Each source is assigned as a Key value and PMID list as values
    pmids_by_source[(pmid_set.find("./LinkName").text)] = [set.text for set in pmid_set.findall("./Link/Id")]

# print(pmids_by_source.values())
pmid_union = set().union(*(pmids_by_source.values()))
print(len(pmid_union))
print(pmid_union)

# TODO: get Intersect done -> Need to well build source params