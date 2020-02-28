from Pccompound import Pccompound
import eutils
import numpy
import sys
import xml.etree.ElementTree as ET
class Ensemble_pccompound:
    """This class represent an ensembl of Pccompound objects, it's composed of:
    - a list of Pccompound objects
    - a list of cid for which NCBI request to get PMID association failed
    """
    def __init__(self):
        self.pccompound_list = list()        
        self.append_failure = list()
    
    def append_pccompound(self, cid, query_builder):
        """This function append a new Pccompound to the pccompound_list attribute. Using the cid, this function send a request to NCBI server via Eutils to get PMID association
        - cid: a PubChem Compound Identifier 
        - query_builder: a eutils.QueryService object parameterized with cache, retmax, retmode, usehistory and especially the api_key"""
        pmids_by_source = {}
        # Get CID associated PMID. using try we test if request fail or not. If request fail, it's added to append_failure list
        try:
            response = query_builder.elink({"dbfrom": "pccompound", "db": "pubmed", "id": cid})
        except eutils.EutilsError as fail_request:
            print("Request on Eutils for compound %s has failed during process, with error name: %s \n -- Compound cid is added to append_failure list" % (cid, fail_request))
            self.append_failure.append(cid)
            return None
        
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
            [sources[index].append(("\"" + source + "\"")) for index in a[0].tolist()]
        self.pccompound_list.append(Pccompound(cid = cid, pmids = pmids_union, pmids_sources = sources))
        
    def export_cids_pmids_triples_ttl(self, output_file):
        """This function export a Ensemble_pccompound as a triples RDF way (format .ttl). For each CID, all association with PMID are indexed with the cito:isDiscussedBy predicat.
        - output_file: a path to the output file
        """
        # Preparing file and writing prefix
        f = open(output_file, "w")
        f.write("@prefix cito:\t<http://purl.org/spar/cito/> .\n@prefix compound:\t<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/> .\n@prefix reference:\t<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> .\n")
        for pcc in self.pccompound_list:
            pmid_export = " ,\n\t\t".join(["reference:PMID"+pmid for pmid in pcc.get_pmids()]) + " .\n"
            pmid_export = "compound:CID" + pcc.get_cid() + "\tcito:isDiscussedBy\t" + pmid_export
            f.write(pmid_export)
        f.close
        
    def export_cid_pmid_endpoint(self, output_file):
        """This function export a Ensemble_pccompound as a triples RDF way (format .ttl). For each combination of CID & PMID sources are annotated
        - output_file: a path to the output file
        """
        f = open(output_file, "w")
        f.write("@prefix endpoint:	<http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/> .\n@prefix cito:\t<http://purl.org/spar/cito/> .\n@prefix obo:\t<http://purl.obolibrary.org/obo/> .\n@prefix compound:\t<http://rdf.ncbi.nlm.nih.gov/pubchem/compound/> .\n@prefix reference:\t<http://rdf.ncbi.nlm.nih.gov/pubchem/reference/> .\n@prefix dcterms:\t<http://purl.org/dc/terms/> .\n")
        for pcc in self.pccompound_list:
            pmids = pcc.get_pmids()
            subject_list = [("CID" + pcc.get_cid() + "_" + "PMID" + pmid) for pmid in pcc.get_pmids()]
            contributors = [",".join(pmid.get_source()) for pmid in pcc.pmid_list]
            complete_triples = [("endpoint:" + subject_list[index] + "\tobo:IAO_0000136\tcompound:CID" + pcc.get_cid() + " ;\n\t\tcito:citesAsDataSource\treference:PMID" + pmids[index] + " ;\n\t\tdcterms:contributor\t" + contributors[index] + " .\n") for index in range(len(pcc.pmid_list))]
            f.write("".join(complete_triples))
        f.close
        
    def get_all_pmids(self):
        """this function allows to extract the union of all pmids associated with Pccompounds objects in the Ensemble_pccompound objects"""
        pmids_union = list(set().union(*([pcc.get_pmids() for pcc in self.pccompound_list])))
        return pmids_union
        
    def get_all_cids(self):
        """this function allows to extract the union of all cids associated with Pccompounds objects in the Ensemble_pccompound objects"""
        cids = [pcc.get_cid() for pcc in self.pccompound_list]
        return cids
