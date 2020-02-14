# Importing packages
# Using Package eutils 0.6.0
import eutils
import numpy
import xml.etree.ElementTree as ET
from Ensemble_pccompound import Ensemble_pccompound
from Pccompound import Pccompound
from Pmid import Pmid

np = numpy
apiKey = "0ddb3479f5079f21272578dc6e040278a508"
cid  = "6036"
# Intialize the result list :
cids_pmids_list = list()
# Building request
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)
# Get CID associated PMID
response = query_builder.elink({"dbfrom": "pccompound", "db": "pubmed", "id": cid})
# parsing XML
root = ET.fromstring(response)
# For each CID - PMIS association source: "pccompound_pubmed", "pccompound_pubmed_mesh", "pccompound_pubmed_publisher"
pmids_by_source = {}
# Exploring sets
for pmid_set in root.findall("./LinkSet/LinkSetDb"):
    # Each source is assigned as a Key value and PMID list as values
    pmids_by_source[(pmid_set.find("./LinkName").text)] = [set.text for set in pmid_set.findall("./Link/Id")]
# Create Union and prepare associated sources

pmids_union = list(set().union(*(pmids_by_source.values())))
sources = [list() for i in range(len(pmids_union))]
# For each PMID ressource in the union set, determine which are the orginals sources of the association.
for source in pmids_by_source.keys():
    a = np.array(np.isin(pmids_union, pmids_by_source[source])).nonzero()
    [sources[index].append(source) for index in a[0].tolist()]

cids_pmids_list.append(Pccompound(cid = cid, pmids = pmids_union, pmids_sources = sources))

new_Ensemble_pccompound = Ensemble_pccompound(cids_pmids_list)