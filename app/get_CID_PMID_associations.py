# Importing packages
# Using Package eutils 0.6.0
import eutils
import xml.etree.ElementTree as ET
from src import Pccompound



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
for pmid_set in root.findall("./LinkSet/LinkSetDb"):
    print(pmid_set.find("./LinkName").text)


