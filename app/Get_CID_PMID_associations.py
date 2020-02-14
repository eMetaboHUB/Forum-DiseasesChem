# Importing packages
# Using Package eutils 0.6.0
import eutils
from Ensemble_pccompound import Ensemble_pccompound

apiKey = "0ddb3479f5079f21272578dc6e040278a508"
cid  = "6036"
# Intialize the result list :
cids_pmids_list = list()
# Building request
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 100000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)

new_Ensemble_pccompound = Ensemble_pccompound()
new_Ensemble_pccompound.append_pccompound("25203768", query_builder)
new_Ensemble_pccompound.append_pccompound("6036", query_builder)
new_Ensemble_pccompound.append_pccompound("11355423", query_builder)
new_Ensemble_pccompound.export_cids_pmids_triples_ttl("test2.txt")

new_Ensemble_pccompound.export_cid_pmid_endpoint("test_endpoint.txt")