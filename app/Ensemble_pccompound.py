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
    """This class represent an ensembl of Pccompound objects:
    - pccompound_list: a list of Pccompound objects
    - append_failure: a list of the cid for which the NCBI eutils request fail
    - ressource_version: the URI (rdflib.URIRef) that will automatocally be associated to the object as a version of the CID_PMID ressource
    - ressource_version_endpoint: the URI (rdflib.URIRef) that will automatocally be associated to the object as a version of the CID_PMID_enpoint ressource
    """
    def __init__(self):
        self.pccompound_list = list()        
        self.append_failure = list()
        self.ressource_version = None
        self.ressource_version_endpoint = None
    
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
        - g: a rdflib Graph that will be filled with these triples
        - namespaces_dict:  dict containing all the used namespaces.
        """
        # Add all triples to graph
        for pcc in self.pccompound_list:
            cid = 'CID' + pcc.get_cid()
            for pmid in pcc.get_pmids():
                g.add((namespaces_dict["compound"][cid], namespaces_dict["cito"].isDiscussedBy, namespaces_dict["reference"]['PMID' + pmid]))
    
    def fill_cids_pmids_endpoint_graph(self, g, namespaces_dict):
        """This function create a rdflib graph containing all the cid - pmid endpoints associations contains in the Ensemble_pccompound object.
        - g: a rdflib Graph that will be filled with these triples
        - namespaces_dict:  dict containing all the used namespaces.
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
        """this function allows to extract the union of all cids associated with Pccompounds objects in the Ensemble_pccompound objects which have associated litterature"""
        cids = [pcc.get_cid() for pcc in self.pccompound_list]
        return cids
    
    def create_CID_PMID_ressource(self, namespace_dict, out_dir, version):
        """
        This function is used to create a new version of the CID_PMID and CID_PMID_enpoint ressources, by creating all the ressource and data graph associated to from information contained in the object.
        - namespace_dict: dict containing all the used namespaces.
        - out_dir: a path to an directory to write output files.
        - version: the version name. If None, the date will be choose by default.
        """
        self.ressource_version = Database_ressource_version(ressource = "CID_PMID", version = version)
        self.ressource_version_endpoint = Database_ressource_version(ressource = "CID_PMID_enpoint", version = version)
        
        self.ressource_version.append_data_graph(file = "cid_pmid.trig", namespace_list = ["reference", "compound", "cito"], namespace_dict = namespace_dict)
        self.ressource_version_endpoint.append_data_graph(file = "cid_pmid_endpoint.trig", namespace_list = ["reference", "compound", "cito", "endpoint", "obo", "dcterms"], namespace_dict = namespace_dict)
        # On remplis les graphs
        self.fill_cids_pmids_graph(g = self.ressource_version.data_graph_dict["cid_pmid"], namespaces_dict = namespace_dict)
        self.fill_cids_pmids_endpoint_graph(g = self.ressource_version_endpoint.data_graph_dict["cid_pmid_endpoint"], namespaces_dict = namespace_dict)
        # On ajoute les infos pour la première ressource:
        self.ressource_version.add_version_namespaces(["void"], namespace_dict)
        self.ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providind link between the PubChem Compound (CID) and the related publications (pmids)"))
        self.ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal("CID to PMIDS RDF triples"))
        self.ressource_version.add_version_attribute(namespace_dict["void"]["triples"], rdflib.Literal( len(self.ressource_version.data_graph_dict["cid_pmid"]), datatype=XSD.long ))
        self.ressource_version.add_version_attribute(namespace_dict["void"]["distinctSubjects"], rdflib.Literal( len(set([str(s) for s in self.ressource_version.data_graph_dict["cid_pmid"].subjects()])), datatype=XSD.long ))
        # On ajoute les infos pour la seconde ressource, les endpoint:
        self.ressource_version_endpoint.add_version_namespaces(["void"], namespace_dict)
        self.ressource_version_endpoint.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains additionnal informations about relations between cid and pmids by expliciting sources of this relations"))
        self.ressource_version_endpoint.add_version_attribute(DCTERMS["title"], rdflib.Literal("CID to PMIDS endpoints RDF triples"))
        self.ressource_version_endpoint.add_version_attribute(namespace_dict["void"]["triples"], rdflib.Literal( len(self.ressource_version_endpoint.data_graph_dict["cid_pmid_endpoint"]), datatype=XSD.long ))
        self.ressource_version_endpoint.add_version_attribute(namespace_dict["void"]["distinctSubjects"], rdflib.Literal( len(set([str(s) for s in self.ressource_version_endpoint.data_graph_dict["cid_pmid_endpoint"].subjects()])), datatype=XSD.long ))
        # On écrit les fichiers
        path_out_1 = out_dir + "CID_PMID/" + self.ressource_version.version + "/"
        path_out_2 = out_dir + "CID_PMID_endpoints/" + self.ressource_version.version + "/"
        if not os.path.exists(path_out_1):
            os.makedirs(path_out_1)
        if not os.path.exists(path_out_2):
            os.makedirs(path_out_2)
        self.ressource_version.data_graph_dict["cid_pmid"].serialize(destination=path_out_1 + "cid_pmid.trig", format='trig')
        self.ressource_version_endpoint.data_graph_dict["cid_pmid_endpoint"].serialize(destination=path_out_2 + "cid_pmid_endpoint.trig", format='trig')
        self.ressource_version.version_graph.serialize(destination= path_out_1 + "ressource_info_cid_pmid_" + self.ressource_version.version + ".ttl", format='turtle')
        self.ressource_version_endpoint.version_graph.serialize(destination= path_out_2 + "ressource_info_cid_pmid_endpoint_" + self.ressource_version_endpoint.version + ".ttl", format='turtle')
        
