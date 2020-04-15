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
    - all_pmids: a set of all the pmids which were fetch 
    - subjects_cid_pmids: the number of subjects in the cid_pmid graph
    - n_triples_cid_pmids: the total number of triples in the cid_pmid graph
    - subjects_cid_pmids_enpoint: the number of subjects in the cid_pmid_endpoint graph
    - n_triples_cid_pmids_endpoint: the total number of triples in the cid_pmid_endpoint graph
    """
    def __init__(self, ressource_name, version, dbfrom, db, ns_linking_id, ns_linked_id, ns_endpoint, primary_predicate, secondary_predicate, namespaces):       
        self.dbfrom = dbfrom
        self.db = db
        self.namespaces = namespaces
        self.ressource_version = Database_ressource_version(ressource = ressource_name, version = version)
        self.ressource_version_endpoint = Database_ressource_version(ressource = ressource_name + "_enpoint", version = version)
        self.ns_linking_id = ns_linking_id
        self.ns_linked_id = ns_linked_id
        self.ns_endpoint = ns_endpoint
        self.primary_predicate = primary_predicate
        self.secondary_predicate = secondary_predicate
        self.g_linked_id = self.ressource_version.create_data_graph(namespace_list = [self.ns_linking_id[0], self.ns_linked_id[0], self.primary_predicate[0]], namespace_dict = self.namespaces)
        self.g_linked_id_endpoint = self.ressource_version_endpoint.create_data_graph(namespace_list = [self.ns_linking_id[0], self.ns_linked_id[0], self.secondary_predicate[0], self.ns_endpoint[0], "obo", "dcterms"], namespace_dict = self.namespaces)
        self.append_failure = list()
        self.available_linked_ids = 0
        self.all_linked_ids = set()
        self.n_subjects_g_linked_id = 0
        self.n_triples_g_linked_id = 0
        self.n_subjects_g_linked_id_endpoint = 0
        self.n_triples_g_linked_id_endpoint = 0
        
    def append_pccompound(self, id_pack, query_builder):
        """This function append a new Pccompound to the pccompound_list attribute. Using the cid, this function send a request to NCBI server via Eutils to get PMID association
        - id_pack: a list PubChem Compound Identifier 
        - query_builder: a eutils.QueryService object parameterized with cache, retmax, retmode, usehistory and especially the api_key"""
        # Get linking_id associated linked_id. using try we test if request fail or not. If request fail, it's added to append_failure list
        try:
            response = query_builder.elink({"dbfrom": self.dbfrom, "db": self.db, "id": id_pack})
        except eutils.EutilsError as fail_request:
            print("Request on Eutils for current compound pack has failed during process, with error name: %s \n -- Compound cids is added to request_failure list" % (fail_request))
            return False
        
        root = ET.fromstring(response)
        # Exploring sets
        for id_Element in root.findall("./LinkSet"):
            # For each LinkSet, get the associated linking_id :
            linking_id = id_Element.find("./IdList/Id").text
            linked_id_by_link_name = {}
            for linked_id_set in id_Element.findall("./LinkSetDb"):
                # Each source is assigned as a Key value and linked_id list as values
                linked_id_by_link_name[(linked_id_set.find("./LinkName").text)] = [set.text for set in linked_id_set.findall("./Link/Id")]
            # If no refenreces can be found for the linking_id, exit function and add it to append_failure list
            if len(linked_id_by_link_name) == 0:
                self.append_failure.append(linking_id)
                continue
            # Create Union and prepare associated link_name
            linked_id_list = list(set().union(*(linked_id_by_link_name.values())))
            link_name_list = [list() for i in range(len(linked_id_list))]
            # For each linked_id link_name in the union set, determine which are the orginals link_name of the association.
            for link_name in linked_id_by_link_name.keys():
                a = numpy.array(numpy.isin(linked_id_list, linked_id_by_link_name[link_name])).nonzero()
                [link_name_list[index].append((link_name)) for index in a[0].tolist()]
            # Add in graph :
            print("\t\tTry to fill graphs g_linked_id ... ", end = '')
            self.fill_ids_link_graph(linking_id, linked_id_list)
            print(" Ok\n\t\tTry to fill graphs g_linked_id_endpoint ... ", end = '')
            self.fill_ids_link_endpoint_graph(linking_id, linked_id_list, link_name_list)
            # On incrémente le nombre de pmids ajoutés :
            self.available_linked_ids += len(linked_id_list)
        return True
    
    def fill_ids_link_graph(self, linking_id, linked_id_list):
        """This function create a rdflib graph containing all the id - linked_id associations.
        - g: a rdflib Graph that will be filled with these triples
        - linking_id: The linking identifier
        - linked_id_list: the linked id list from the request result
        - ns_linking_id: a tuple containing information on the namespace of the linking id (ns, prefix)
        - ns_linked_id: a tuple containing information on the namespace of the linked id (ns, prefix)
        - premary_predicate: a tuple containing information on the predicate describing the relation between the linking and linked id (ns, predicate)
        """
        # Add all triples to graph
        for linked_id in linked_id_list:
            self.g_linked_id.add((self.namespaces[self.ns_linking_id[0]][self.ns_linking_id[1] + linking_id], self.namespaces[self.primary_predicate[0]][self.primary_predicate[1]], self.namespaces[self.ns_linked_id[0]][self.ns_linked_id[1] + linked_id]))
    
    def fill_ids_link_endpoint_graph(self, linking_id, linked_id_list, link_name_list):
        """This function create a rdflib graph containing all the cid - pmid endpoints associations contains in the Ensemble_pccompound object.
        - g: a rdflib Graph that will be filled with these triples- linking_id: The linking identifier
        - linked_id_list: the linked id list from the request result
        - link_name_list: the link_name list from the request result
        - ns_linking_id: a tuple containing information on the namespace of the linking id (ns, prefix)
        - ns_linked_id: a tuple containing information on the namespace of the linked id (ns, prefix)
        - secondary_predicate: a tuple containing information on the predicate describing the relation between the linking and linked id (ns, predicate) to use in the endpoint
        - ns_endpoint: a tuple containing information on the namespace of the endpoint (ns, prefix)
        """
        for linked_id_index in range(0, len(linked_id_list)):
            linked_id = linked_id_list[linked_id_index]
            link_name = ",".join(link_name_list[linked_id_index])
            subject = linking_id + "_" + linked_id
            # Add to graph
            self.g_linked_id_endpoint.add((self.namespaces[self.ns_endpoint[0]][self.ns_endpoint[1] + subject], self.namespaces["obo"]['IAO_0000136'], self.namespaces[self.ns_linking_id[0]][self.ns_linking_id[1] + linking_id]))
            self.g_linked_id_endpoint.add((self.namespaces[self.ns_endpoint[0]][self.ns_endpoint[1] + subject], self.namespaces[self.secondary_predicate[0]][self.secondary_predicate[1]], self.namespaces[self.ns_linked_id[0]][self.ns_linked_id[1] + linked_id]))
            self.g_linked_id_endpoint.add((self.namespaces[self.ns_endpoint[0]][self.ns_endpoint[1] + subject], self.namespaces["dcterms"]['contributor'], rdflib.Literal(link_name)))
    
    def get_all_linked_ids(self):
        """this function allows to extract the union of all linked_ids, the objects of the g_linked_id graph"""
        all_linked_ids = set([str(s).split(self.namespaces[self.ns_linked_id[0]] + self.ns_linked_id[1])[1] for s in self.g_linked_id.objects()]).union()
        return all_linked_ids
    
    def get_all_linking_ids(self):
        """this function allows to extract of all linking ids, the subjects of the g_linked_id graph"""
        all_linking_ids = set([str(s).split(self.namespaces[self.ns_linking_id[0]] + self.ns_linking_id[1])[1] for s in self.g_linked_id.subjects()])
        return all_linking_ids
    
    def get_all_linked_id_endpoints(self):
        """this function allows to extract the union of all linked_enpoint ids, the subjects of the g_linked_id_endpoint"""
        all_linked_ids_endpoints = set([str(s).split(self.namespaces[self.ns_endpoint[0]] + self.ns_endpoint[1])[1] for s in self.g_linked_id_endpoint.subjects()])
        return all_linked_ids_endpoints
    
    def clean(self):
        self.g_linked_id = None
        self.g_linked_id = self.ressource_version.create_data_graph(namespace_list = [self.ns_linking_id[0], self.ns_linked_id[0], self.primary_predicate[0]], namespace_dict = self.namespaces)
        self.g_linked_id_endpoint = None
        self.g_linked_id_endpoint = self.ressource_version_endpoint.create_data_graph(namespace_list = [self.ns_linking_id[0], self.ns_linked_id[0], self.secondary_predicate[0], self.ns_endpoint[0], "obo", "dcterms"], namespace_dict = self.namespaces)
        self.append_failure = None
        self.append_failure = list()
        self.available_linked_ids = 0
    
    def create_CID_PMID_ressource(self, out_dir, id_list, pack_size, query_builder, max_size):
        """
        This function is used to create a new version of the CID_PMID and CID_PMID_enpoint ressources, by creating all the ressource and data graph associated to from information contained in the object.
        - out_dir: a path to an directory to write output files.
        - cid_list: a list of cids
        - pack_size: the size of the cids pack that have to be send as request
        - query_builder: a eutils.QueryService object parameterized with cache, retmax, retmode, usehistory and especially the api_key
        - max_size : the maximal number of pmids by files
        """
        # Création des fichiers de sorties :
        if not os.path.exists("additional_files"):
            os.makedirs("additional_files")
        f_all_linked_ids = open("additional_files/all_linked_ids.txt", 'w')
        f_success = open("additional_files/successful_linking_ids.txt", 'w')
        f_append_failure = open("additional_files/linking_ids_without_linked_ids.txt", 'w')
        f_request_failure = open("additional_files/linking_ids_request_failed.txt", 'w')
        # On ajoute les infos pour la première ressource:
        ns_void = rdflib.Namespace("http://rdfs.org/ns/void#")
        self.ressource_version.version_graph.bind("void", ns_void)
        self.ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providind link between Entrez Ids from the NCBI database " + self.dbfrom + " to the " + self.db + " database"))
        self.ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal(self.dbfrom + " to " + self.db + " RDF triples"))
        # On ajoute les infos pour la seconde ressource, les endpoint:
        self.ressource_version_endpoint.version_graph.bind("void", ns_void)
        self.ressource_version_endpoint.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains additionnal informations describing relations between Entrez Ids from the NCBI database " + self.dbfrom + " to the " + self.db + " database"))
        self.ressource_version_endpoint.add_version_attribute(DCTERMS["title"], rdflib.Literal(self.dbfrom + " to " + self.db + " endpoint RDF triples"))
        # On prépare les répertoire : 
        path_out_1 = out_dir + self.ressource_version.ressource + "/" + self.ressource_version.version + "/"
        path_out_2 = out_dir + self.ressource_version_endpoint.ressource + "/" + self.ressource_version_endpoint.version + "/"
        if not os.path.exists(path_out_1):
            os.makedirs(path_out_1)
        if not os.path.exists(path_out_2):
            os.makedirs(path_out_2)
        id_packed_list = [id_list[i * pack_size:(i + 1) * pack_size] for i in range((len(id_list) + pack_size - 1) // pack_size )]
        print("There are %d packed lists" %(len(id_packed_list)))
        file_index = 1
        # On initialize les deux premières instances des graphs g_linked_id & g_linked_id_endpoint : 
        g_linked_id_name, g_linked_id_endpoint_name = self.ressource_version.ressource + "_" + str(file_index), self.ressource_version_endpoint.ressource + "_" + str(file_index)
        for index_list in range(0, len(id_packed_list)):
            print("-- Start getting pmids of list %d !" %(index_list + 1))
            print("Try to append compounds ...", end = '')
            # On append les linked_ids: Si false est return c'est qu'il y a eu une erreur dans la requête, sinon on continue
            test_append = self.append_pccompound(id_packed_list[index_list], query_builder)
            if not test_append:
                print(" <!!!> Fail <!!!> \n There was an issue while querying NCBI server, check parameters. Try to continue to the next packed list. All ids are exported to request failure file.")
                for id_fail in id_packed_list[index_list]:
                    f_request_failure.write("%s\n" %(id_fail))
                continue
            print(" Ok\n", end = '')
            if self.available_linked_ids > max_size or (index_list == len(id_packed_list) - 1):
                if index_list == len(id_packed_list) - 1:
                    print("\t\tEnd was reached with %d new linking_id - linked_id association, start to export graph\n" %(self.available_linked_ids))
                else:
                    print("\t\tMaximal size (%d) was reached with %d new linking_id - linked_id association, start to export graph\n" %(max_size, self.available_linked_ids))
                # On incrémente les nombres de sujets et de triples :
                print("\t\tIncrement numbers of triples and subjects from added triples ...", end = '')
                self.n_triples_g_linked_id += len(self.g_linked_id)
                self.n_triples_g_linked_id_endpoint += len(self.g_linked_id_endpoint)
                self.n_subjects_g_linked_id += len(self.get_all_linking_ids())
                self.n_subjects_g_linked_id_endpoint += len(self.get_all_linked_id_endpoints())
                print(" Ok\n\t\tTry to write and compress graph as .tll in %s and %s ..." %(path_out_1, path_out_2), end = '')
                # On export les graphs :
                self.g_linked_id.serialize(destination=path_out_1 + g_linked_id_name + ".trig", format='trig')
                self.g_linked_id_endpoint.serialize(destination=path_out_2 + g_linked_id_endpoint_name + ".trig", format='trig')
                # On zip :
                os.system("gzip " + path_out_1 + g_linked_id_name + ".trig" + " " + path_out_2 + g_linked_id_endpoint_name + ".trig")
                # On export les cid successful :
                print(" Ok\n\t\tTry tp export successful linking ids in additional_files/successful_linking_ids.txt ...", end = '')
                for success_id in self.get_all_linking_ids():
                    f_success.write("%s\n" %(success_id))
                print(" Ok\n\t\tTry tp export linking ids without linked_ids in additional_files/linking_ids_without_linked_ids.txt ...", end = '')
                # On export les append failures :
                for append_failure_cid in self.append_failure:
                    f_append_failure.write("%s\n" %(append_failure_cid))
                print(" Ok\n\t\t Try to append new linked ids to the global set ...", end = '')
                self.all_linked_ids = self.all_linked_ids.union(self.get_all_linked_ids())
                print(" Ok\n\t\tTry to clear objects for next iteration ...", end = '')
                # On vide les graphs et les objects : 
                self.clean()
                if index_list != len(id_packed_list) - 1:
                    print(" Ok\n\t\tTry to create new graphs ...", end = '')
                    # On incrémente le fichier :
                    file_index += 1
                    # On créée deux nouveaux graphs :
                    g_linked_id_name, g_linked_id_endpoint_name = self.ressource_version.ressource + "_" + str(file_index), self.ressource_version_endpoint.ressource + "_" + str(file_index)
                print(" Ok\n", end = '')
        # On exporte le graph des metadata :
        print(" Export version graph with metadata ...", end = '')
        self.ressource_version.add_version_attribute(ns_void["triples"], rdflib.Literal(self.n_triples_g_linked_id, datatype=XSD.long ))
        self.ressource_version.add_version_attribute(ns_void["distinctSubjects"], rdflib.Literal(self.n_subjects_g_linked_id, datatype=XSD.long ))
        self.ressource_version_endpoint.add_version_attribute(ns_void["triples"], rdflib.Literal(self.n_triples_g_linked_id_endpoint, datatype=XSD.long ))
        self.ressource_version_endpoint.add_version_attribute(ns_void["distinctSubjects"], rdflib.Literal(self.n_subjects_g_linked_id_endpoint, datatype=XSD.long ))
        self.ressource_version.version_graph.serialize(destination= path_out_1 + "ressource_info_cid_pmid_" + self.ressource_version.version + ".ttl", format='turtle')
        self.ressource_version_endpoint.version_graph.serialize(destination= path_out_2 + "ressource_info_cid_pmid_endpoint_" + self.ressource_version_endpoint.version + ".ttl", format='turtle')
        print(" Ok\n Export all linked ids ...", end = '')
        for linked_id in self.all_linked_ids:
            f_all_linked_ids.write("%s\n" %(linked_id))
        print(" Ok\n End !\n", end = '')
        f_success.close()
        f_append_failure.close()
        f_request_failure.close()