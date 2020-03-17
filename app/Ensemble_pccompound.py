from Pccompound import Pccompound
import eutils
import rdflib
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
            [sources[index].append((source)) for index in a[0].tolist()]
        self.pccompound_list.append(Pccompound(cid = cid, pmids = pmids_union, pmids_sources = sources))
    
    def create_cids_pmids_graph(self, namespaces_dict):
        """This function create a rdflib graph containing all the cid - pmid associations contains in the Ensemble_pccompound object"""
        ref = namespaces_dict["reference"]
        cpd = namespaces_dict["compound"]
        cito = namespaces_dict["cito"]
        g = rdflib.Graph()
        # On ajoute les namespace en séquence ( c'est pas joli mais obligé de faire comme ça si on veut utilisé une syntaxe prefix ...)
        g.bind("reference", ref)
        g.bind("compound", cpd)
        g.bind("cito", cito)
        # Add all triples to graph
        for pcc in self.pccompound_list:
            cid = 'CID' + pcc.get_cid()
            for pmid in pcc.get_pmids():
                g.add((cpd[cid], cito.isDiscussedBy, ref['PMID' + pmid]))
        return g
    
    def create_cids_pmids_endpoint_graph(self, namespaces_dict):
        ref = namespaces_dict["reference"]
        cpd = namespaces_dict["compound"]
        cito = namespaces_dict["cito"]
        endp = namespaces_dict["endpoint"]
        obo = namespaces_dict["obo"]
        dcterms = namespaces_dict["dcterms"]
        g = rdflib.Graph()
        # On ajoute les namespace en séquence
        g.bind("reference", ref)
        g.bind("compound", cpd)
        g.bind("cito", cito)
        g.bind("endpoint", endp)
        g.bind("obo", obo)
        g.bind("dcterms", dcterms)
        for pcc in self.pccompound_list:
            cid = 'CID' + pcc.get_cid()
            for p in pcc.pmid_list:
                pmid = 'PMID' + p.get_pmid()
                source = ",".join(p.get_source())
                s = cid + "_" + pmid
                # Add to graph
                g.add((endp[s], obo.IAO_0000136, cpd[cid]))
                g.add((endp[s], cito.citesAsDataSource, ref[pmid]))
                g.add((endp[s], dcterms.contributor, rdflib.Literal(source)))
        return g
    
    def get_all_pmids(self):
        """this function allows to extract the union of all pmids associated with Pccompounds objects in the Ensemble_pccompound objects"""
        pmids_union = list(set().union(*([pcc.get_pmids() for pcc in self.pccompound_list])))
        return pmids_union
    
    def get_all_cids(self):
        """this function allows to extract the union of all cids associated with Pccompounds objects in the Ensemble_pccompound objects"""
        cids = [pcc.get_cid() for pcc in self.pccompound_list]
        return cids