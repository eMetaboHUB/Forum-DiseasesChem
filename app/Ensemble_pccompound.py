from Pccompound import Pccompound
import eutils
import rdflib
import numpy
import sys
import os
from rdflib.namespace import XSD, DCTERMS, RDFS
from datetime import date
import xml.etree.ElementTree as ET
from Database_ressource_version import Database_ressource_version

class Ensemble_pccompound:
    """This class represent an ensembl of Pccompound objects, it's composed of:
    - a list of Pccompound objects
    - a list of cid for which NCBI request to get PMID association failed
    """
    def __init__(self):
        self.pccompound_list = list()        
        self.append_failure = list()
        self.ressource_version = None
    
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
    
    def fill_cids_pmids_graph(self, g, namespaces_dict):
        """This function create a rdflib graph containing all the cid - pmid associations contains in the Ensemble_pccompound object.
        g is a rdflib Graph were fill these triples
        """
        # Add all triples to graph
        for pcc in self.pccompound_list:
            cid = 'CID' + pcc.get_cid()
            for pmid in pcc.get_pmids():
                g.add((namespaces_dict["compound"][cid], namespaces_dict["cito"].isDiscussedBy, namespaces_dict["reference"]['PMID' + pmid]))
    
    def fill_cids_pmids_endpoint_graph(self, g, namespaces_dict):
        """This function create a rdflib graph containing all the cid - pmid endpoints associations contains in the Ensemble_pccompound object.
        g is a rdflib Graph were fill these triples
        """
        for pcc in self.pccompound_list:
            cid = 'CID' + pcc.get_cid()
            for p in pcc.pmid_list:
                pmid = 'PMID' + p.get_pmid()
                source = ",".join(p.get_source())
                s = cid + "_" + pmid
                # Add to graph
                g.add((namespaces_dict["endpoint"][s], namespaces_dict["obo"].IAO_0000136, namespaces_dict["compound"][cid]))
                g.add((namespaces_dict["endpoint"][s], namespaces_dict["cito"].citesAsDataSource, namespaces_dict["reference"][pmid]))
                g.add((namespaces_dict["endpoint"][s], namespaces_dict["dcterms"].contributor, rdflib.Literal(source)))
    
    def get_all_pmids(self):
        """this function allows to extract the union of all pmids associated with Pccompounds objects in the Ensemble_pccompound objects"""
        pmids_union = list(set().union(*([pcc.get_pmids() for pcc in self.pccompound_list])))
        return pmids_union
    
    def get_all_cids(self):
        """this function allows to extract the union of all cids associated with Pccompounds objects in the Ensemble_pccompound objects"""
        cids = [pcc.get_cid() for pcc in self.pccompound_list]
        return cids
    
    def create_CID_PMID_ressource(self, namespace_dict, out_dir):
        self.ressource_version = Database_ressource_version(ressource = "CID_PMID_triples", version_date = date.today().isoformat())
        self.ressource_version.append_data_graph(file = "cid_isDiscussedBy_pmid.trig", namespace_list = ["reference", "compound", "cito"], namespace_dict = namespace_dict)
        self.ressource_version.append_data_graph(file = "cid_pmid_endpoint.trig", namespace_list = ["reference", "compound", "cito", "endpoint", "obo", "dcterms"], namespace_dict = namespace_dict)
        # On remplis les graphs
        self.fill_cids_pmids_graph(g = self.ressource_version.data_graph_dict["cid_isDiscussedBy_pmid"], namespaces_dict = namespace_dict)
        self.fill_cids_pmids_endpoint_graph(g = self.ressource_version.data_graph_dict["cid_pmid_endpoint"], namespaces_dict = namespace_dict)
        # On ajoute les infos :
        self.ressource_version.add_version_namespaces(["void"], namespace_dict)
        self.ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providind link between the PubChem Compound (CID) and the related publications (pmids). Information (nb of triples, etc ...) are provided only for the <cid isDiscussedBy pmid> part of the ressource, cause of endpoint will be redondant informations"))
        self.ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal("CID to PMIDS RDF triples"))
        self.ressource_version.add_version_attribute(namespace_dict["void"]["triples"], rdflib.Literal( len(self.ressource_version.data_graph_dict["cid_isDiscussedBy_pmid"]), datatype=XSD.long ))
        self.ressource_version.add_version_attribute(namespace_dict["void"]["distinctSubjects"], rdflib.Literal( len(set([str(s) for s in self.ressource_version.data_graph_dict["cid_isDiscussedBy_pmid"].subjects()])), datatype=XSD.long ))
        self.ressource_version.add_version_attribute(RDFS["comment"], rdflib.Literal("The total number of distinct pmid is : " + str(len(set([str(o) for o in self.ressource_version.data_graph_dict["cid_isDiscussedBy_pmid"].objects()])))))
        # On écrit les fichiers
        path_out = out_dir + "CID_PMID_triples/" + self.ressource_version.version_date + "/"
        if not os.path.exists(path_out):
            os.makedirs(path_out)
        self.ressource_version.data_graph_dict["cid_isDiscussedBy_pmid"].serialize(destination=path_out + "cid_isDiscussedBy_pmid.trig", format='trig')
        self.ressource_version.data_graph_dict["cid_pmid_endpoint"].serialize(destination=path_out + "cid_pmid_endpoint.trig", format='trig')
        self.ressource_version.version_graph.serialize(destination=out_dir + "CID_PMID_triples/" + "ressource_info_" + self.ressource_version.version_date + ".ttl", format='turtle')
        
