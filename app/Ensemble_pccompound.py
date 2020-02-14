from Pccompound import Pccompound
import eutils
import numpy
import xml.etree.ElementTree as ET
class Ensemble_pccompound:
    """This class represent an ensembl of Pccompound objects, it's composed of:
    - a list of cid
    - a size attribute
    - a corresponding list of Pccompound objects
    """
    def __init__(self):
        self.pccompound_list = list()        
        self.size = 0
        self.append_failure = list()
    
    def append_pccompound(self, cid, query_builder):
        pmids_by_source = {}
        # Get CID associated PMID
        response = query_builder.elink({"dbfrom": "pccompound", "db": "pubmed", "id": cid})
        root = ET.fromstring(response)
        # Exploring sets
        for pmid_set in root.findall("./LinkSet/LinkSetDb"):
            # Each source is assigned as a Key value and PMID list as values
            pmids_by_source[(pmid_set.find("./LinkName").text)] = [set.text for set in pmid_set.findall("./Link/Id")]
        # If no refenreces can be found for the cid, exit function and add it to append_failure list
        if len(pmids_by_source) == 0:
            self.append_failure.append(cid)
            return None
        # Create Union and prepare associated sources
        pmids_union = list(set().union(*(pmids_by_source.values())))
        sources = [list() for i in range(len(pmids_union))]
        # For each PMID ressource in the union set, determine which are the orginals sources of the association.
        for source in pmids_by_source.keys():
            a = numpy.array(numpy.isin(pmids_union, pmids_by_source[source])).nonzero()
            [sources[index].append(source) for index in a[0].tolist()]
        self.pccompound_list.append(Pccompound(cid = cid, pmids = pmids_union, pmids_sources = sources))
    
    def export_cids_pmids_triples_ttl(self, output_file):
        # Preparing file and writing prefix
        f = open(output_file, "w")
        f.write("@prefix cito:\t<http://purl.org/spar/cito/> .\n@prefix compound:\t<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/> .\n@prefix reference:\t<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> .\n")
        for pcc in self.pccompound_list:
            pmid_export = " ,\n\t\t".join(["reference:PMID"+pmid for pmid in pcc.get_pmids()]) + " .\n"
            pmid_export = "compound:CID" + pcc.get_cid() + "\tcito:isDiscussedBy\t" + pmid_export
            f.write(pmid_export)
        f.close
