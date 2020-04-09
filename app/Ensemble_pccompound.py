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
    - append_failure: a list of the cid for which the NCBI eutils request succeeded but for which there was no associated litterature
    - ressource_version: the URI (rdflib.URIRef) that will automatocally be associated to the object as a version of the CID_PMID ressource
    - ressource_version_endpoint: the URI (rdflib.URIRef) that will automatocally be associated to the object as a version of the CID_PMID_enpoint ressource
    """
    def __init__(self):
        self.pccompound_list = list()        
        self.append_failure = list()
        self.ressource_version = None
        self.all_cids = set()
        self.all_pmids = set()
        self.ressource_version_endpoint = None
        self.available_pmids = 0
        self.subjects_cid_pmids = set()
        self.n_triples_cid_pmids = 0
        self.subjects_cid_pmids_enpoint = set()
        self.n_triples_cid_pmids_endpoint = 0
        
    def append_pccompound(self, cid_pack, query_builder):
        """This function append a new Pccompound to the pccompound_list attribute. Using the cid, this function send a request to NCBI server via Eutils to get PMID association
        - cid: a list PubChem Compound Identifier 
        - query_builder: a eutils.QueryService object parameterized with cache, retmax, retmode, usehistory and especially the api_key"""
        # Get CID associated PMID. using try we test if request fail or not. If request fail, it's added to append_failure list
        try:
            response = query_builder.elink({"dbfrom": "pccompound", "db": "pubmed", "id": cid_pack})
        except eutils.EutilsError as fail_request:
            print("Request on Eutils for current compound pack has failed during process, with error name: %s \n -- Compound cids is added to request_failure list" % (fail_request))
            return False
        
        root = ET.fromstring(response)
        # Exploring sets
        for cid_Element in root.findall("./LinkSet"):
            # For each LinkSet, get the associated cid :
            cid = cid_Element.find("./IdList/Id").text
            pmids_by_source = {}
            for pmid_set in cid_Element.findall("./LinkSetDb"):
                # Each source is assigned as a Key value and PMID list as values
                pmids_by_source[(pmid_set.find("./LinkName").text)] = [set.text for set in pmid_set.findall("./Link/Id")]
            # If no refenreces can be found for the cid, exit function and add it to append_failure list
            if len(pmids_by_source) == 0:
                self.append_failure.append(cid)
                continue
            # Create Union and prepare associated sources
            pmids_union = list(set().union(*(pmids_by_source.values())))
            sources = [list() for i in range(len(pmids_union))]
            # For each PMID ressource in the union set, determine which are the orginals sources of the association.
            for source in pmids_by_source.keys():
                a = numpy.array(numpy.isin(pmids_union, pmids_by_source[source])).nonzero()
                [sources[index].append((source)) for index in a[0].tolist()]
            self.pccompound_list.append(Pccompound(cid = cid, pmids = pmids_union, pmids_sources = sources))
            # On incrémente le nombre de pmids ajoutés :
            self.available_pmids += len(pmids_union)
        return True
    
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
    
    def create_CID_PMID_ressource(self, namespace_dict, out_dir, version, cid_list, pack_size, query_builder, max_size):
        """
        This function is used to create a new version of the CID_PMID and CID_PMID_enpoint ressources, by creating all the ressource and data graph associated to from information contained in the object.
        - namespace_dict: dict containing all the used namespaces.
        - out_dir: a path to an directory to write output files.
        - version: the version name. If None, the date will be choose by default.
        """
        # Création des fichiers de sorties :
        if not os.path.exists("additional_files"):
            os.makedirs("additional_files")
        f_success = open("additional_files/successful_cids.txt", 'w')
        f_append_failure = open("additional_files/cids_without_literature.txt", 'w')
        f_request_failure = open("additional_files/cid_request_failed.txt", 'w')
        # On crée les 2 ressources :
        self.ressource_version = Database_ressource_version(ressource = "CID_PMID", version = version)
        self.ressource_version_endpoint = Database_ressource_version(ressource = "CID_PMID_enpoint", version = version)
        # On ajoute les infos pour la première ressource:
        self.ressource_version.add_version_namespaces(["void"], namespace_dict)
        self.ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providind link between the PubChem Compound (CID) and the related publications (pmids)"))
        self.ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal("CID to PMIDS RDF triples"))
        # On ajoute les infos pour la seconde ressource, les endpoint:
        self.ressource_version_endpoint.add_version_namespaces(["void"], namespace_dict)
        self.ressource_version_endpoint.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains additionnal informations about relations between cid and pmids by expliciting sources of this relations"))
        self.ressource_version_endpoint.add_version_attribute(DCTERMS["title"], rdflib.Literal("CID to PMIDS endpoints RDF triples"))
        # On prépare les répertoire : 
        path_out_1 = out_dir + "CID_PMID/" + self.ressource_version.version + "/"
        path_out_2 = out_dir + "CID_PMID_endpoints/" + self.ressource_version.version + "/"
        if not os.path.exists(path_out_1):
            os.makedirs(path_out_1)
        if not os.path.exists(path_out_2):
            os.makedirs(path_out_2)
        cid_packed_list = [cid_list[i * pack_size:(i + 1) * pack_size] for i in range((len(cid_list) + pack_size - 1) // pack_size )]
        print("There are %d packed lists" %(len(cid_packed_list)))
        file_index = 1
        # On initialize les deux premières instances des graphs cid_pmids & cid_pmid_endpoint : 
        cp_name, cpe_name = "cid_pmid_" + str(file_index), "cid_pmid_endpoint_" + str(file_index)
        self.ressource_version.append_data_graph(file = cp_name + ".trig", namespace_list = ["reference", "compound", "cito"], namespace_dict = namespace_dict)
        self.ressource_version_endpoint.append_data_graph(file = cpe_name + ".trig", namespace_list = ["reference", "compound", "cito", "endpoint", "obo", "dcterms"], namespace_dict = namespace_dict)
        for index_list in range(0, len(cid_packed_list)):
            print("-- Start getting pmids of list %d !" %(index_list + 1))
            print("Try to append compounds ...", end = '')
            # On append les compouds: Si false est return c'est qu'il y a eu une erreur dans la requête, sinon on continue
            test_append = self.append_pccompound(cid_packed_list[index_list], query_builder)
            if not test_append:
                print(" <!!!> Fail <!!!> \n There was an issue while querying NCBI server, check parameters. Try to continue to the next packed list. All ids are exported to request failure file.")
                for cid_fail in cid_packed_list[index_list]:
                    f_request_failure.write("%s\n" %(cid_fail))
                continue
            print(" Ok\n", end = '')
            if self.available_pmids > max_size or (index_list == len(cid_packed_list) - 1):
                if index_list == len(cid_packed_list) - 1:
                    print("\t\tEnd was reached with %d new pmids, start to export graph\n" %(self.available_pmids))
                else:
                    print("\t\tMaximal size (%d) was reached with %d new pmids, start to export graph\n" %(max_size, self.available_pmids))
                # On remplis les graphs :
                print("\t\tTry to fill graphs cids_pmids ... ", end = '')
                self.fill_cids_pmids_graph(g = self.ressource_version.data_graph_dict[cp_name], namespaces_dict = namespace_dict)
                print(" Ok\n\t\tTry to fill graphs cids_pmids_enpoint ... ", end = '')
                self.fill_cids_pmids_endpoint_graph(g = self.ressource_version_endpoint.data_graph_dict[cpe_name], namespaces_dict = namespace_dict)
                # On incrémente les nombres de sujets et de triples :
                print(" Ok\n\t\tIncrement numbers of triples and subjects from added triples ...", end = '')
                self.n_triples_cid_pmids += len(self.ressource_version.data_graph_dict[cp_name])
                self.n_triples_cid_pmids_endpoint += len(self.ressource_version_endpoint.data_graph_dict[cpe_name])
                self.subjects_cid_pmids = self.subjects_cid_pmids.union(set([str(s) for s in self.ressource_version.data_graph_dict[cp_name].subjects()]))
                self.subjects_cid_pmids_enpoint = self.subjects_cid_pmids_enpoint.union(set([str(s) for s in self.ressource_version_endpoint.data_graph_dict[cpe_name].subjects()]))
                print(" Ok\n\t\tTry to write and compress graph as .tll in %s and %s ..." %(path_out_1, path_out_2), end = '')
                # On export les graphs :
                self.ressource_version.data_graph_dict[cp_name].serialize(destination=path_out_1 + cp_name + ".trig", format='trig')
                self.ressource_version_endpoint.data_graph_dict[cpe_name].serialize(destination=path_out_2 + cpe_name + ".trig", format='trig')
                # On zip :
                os.system("gzip " + path_out_1 + cp_name + ".trig" + " " + path_out_2 + cpe_name + ".trig")
                # On export les cid successful :
                print(" Ok\n\t\tTry tp export successful cid in additional_files/successful_cids.txt ...", end = '')
                for success_cid in self.get_all_cids():
                    f_success.write("%s\n" %(success_cid))
                print(" Ok\n\t\tTry tp export cid without literature in additional_files/cids_without_literature.txt ...", end = '')
                # On export les append failures :
                for append_failure_cid in self.append_failure:
                    f_append_failure.write("%s\n" %(append_failure_cid))
                print(" Ok\n\t\t Try to append new cids and pmids to the global set ...", end = '')
                self.all_cids = self.all_cids.union(self.get_all_cids())
                self.all_pmids = self.all_pmids.union(self.get_all_pmids())
                print(" Ok\n\t\tTry to clear objects for next iteration ...", end = '')
                # On vide les graphs et les objects : 
                self.ressource_version.data_graph_dict[cp_name].remove((None, None, None))
                self.ressource_version_endpoint.data_graph_dict[cpe_name].remove((None, None, None))
                self.pccompound_list.clear()
                self.append_failure.clear()
                self.available_pmids = 0
                if index_list != len(cid_packed_list) - 1:
                    print(" Ok\n\t\tTry to create new graphs ...", end = '')
                    # On incrémente le fichier :
                    file_index += 1
                    # On créée deux nouveaux graphs :
                    cp_name, cpe_name = "cid_pmid_" + str(file_index), "cid_pmid_endpoint_" + str(file_index)
                    self.ressource_version.append_data_graph(file = cp_name + ".trig", namespace_list = ["reference", "compound", "cito"], namespace_dict = namespace_dict)
                    self.ressource_version_endpoint.append_data_graph(file = cpe_name + ".trig", namespace_list = ["reference", "compound", "cito", "endpoint", "obo", "dcterms"], namespace_dict = namespace_dict)
                print(" Ok\n", end = '')
        # On exporte le graph des metadata :
        print(" Export version graph with metadata ...", end = '')
        self.ressource_version.add_version_attribute(namespace_dict["void"]["triples"], rdflib.Literal(self.n_triples_cid_pmids, datatype=XSD.long ))
        self.ressource_version.add_version_attribute(namespace_dict["void"]["distinctSubjects"], rdflib.Literal(len(self.subjects_cid_pmids), datatype=XSD.long ))
        self.ressource_version_endpoint.add_version_attribute(namespace_dict["void"]["triples"], rdflib.Literal(self.n_triples_cid_pmids_endpoint, datatype=XSD.long ))
        self.ressource_version_endpoint.add_version_attribute(namespace_dict["void"]["distinctSubjects"], rdflib.Literal(len(self.subjects_cid_pmids_enpoint), datatype=XSD.long ))
        self.ressource_version.version_graph.serialize(destination= path_out_1 + "ressource_info_cid_pmid_" + self.ressource_version.version + ".ttl", format='turtle')
        self.ressource_version_endpoint.version_graph.serialize(destination= path_out_2 + "ressource_info_cid_pmid_endpoint_" + self.ressource_version_endpoint.version + ".ttl", format='turtle')
        print(" Ok\n End !\n", end = '')
        f_success.close()
        f_append_failure.close()
        f_request_failure.close()
