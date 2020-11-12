import eutils
import rdflib
import numpy
import sys
import os
import requests
import signal
import subprocess
sys.path.insert(1, 'app/')
from rdflib.namespace import XSD, DCTERMS, RDFS, VOID, RDF
from datetime import date
import xml.etree.ElementTree as ET
from Database_ressource_version import Database_ressource_version

# Prepare TimeoutExceptions
class TimeOutException(Exception):
   pass

def alarm_handler(signum, frame):
    raise TimeOutException()

class Elink_ressource_creator:
    """This class represent an ensembl of Pccompound objects:
    - dbfrom: The NCBI Entrez database for linking ids
    - db: The NCBI Entrez database for linked ids
    - namespaces: a dict containing namespace names as keys and associated rdflib.Namespace() objects as values
    - ressource_version: Database_ressource_version objects representing a new version of the association between linking_ids and linked ids association
    - ressource_version_endpoint: Database_ressource_version objects representing a new version of the additionnal information about associations between linking_ids and linked ids association
    - ns_linking_id: a tuple representing namespace name and associated prefix (if one should be added next before the id) for linking ids
    - ns_linked_id: a tuple representing namespace name and associated prefix (if one should be added next before the id) for linked ids
    - ns_endpoint: a tuple representing namespace name and associated prefix (if one should be added next before the id) for endpoints ids
    - primary_predicate: a tuple representing the primary predicate with namespace name and predicate name, that will be used to illutrate the relation between linking ids and linked ids
    - secondary_predicate: a tuple representing the secondary predicate with namespace name and predicate name, that will be used to illutrate the additionnal relation between linking ids and linked ids in the endpoint graph
    - g_linked_id: a rdflib graph storing association between linking ids and linked ids using the primary_predicate
    - g_linked_id_endpoint: a rdflib graph storing describing associations between linking ids and linked ids using the secondary_predicate
    - append_failure: a list of the linking ids for which the NCBI eutils request succeeded but for which there was no associated linked ids
    - request_failure: a list of linkings ids for which there was a eutils.EutilsError or a RequestException. For all ids contained in the request failure, a new attempt will be processed until th request succeded. 
    - available_linked_ids: a variable that store the current number of linking ids added to graphs
    - all_linked_ids: a set of all the linked ids which were added to graphs 
    - n_subjects_g_linked_id: the number of subjects in the g_linked_id graph
    - n_triples_g_linked_id: the total number of triples in the g_linked_id graph
    - n_subjects_g_linked_id_endpoint: the number of subjects in the g_linked_id_endpoint graph
    - n_triples_g_linked_id_endpoint: the total number of triples in the g_linked_id_endpoint graph
    """
    def __init__(self, ressource_name, version, dbfrom, db, ns_linking_id, ns_linked_id, ns_endpoint, primary_predicate, secondary_predicate, namespaces, timeout):       
        self.dbfrom = dbfrom
        self.db = db
        self.file_index = 1
        self.namespaces = namespaces
        self.ressource_version = Database_ressource_version(ressource = ressource_name, version = version)
        self.ressource_version_endpoint = Database_ressource_version(ressource = ressource_name + "_endpoints", version = version)
        self.ns_linking_id = ns_linking_id
        self.ns_linked_id = ns_linked_id
        self.ns_endpoint = ns_endpoint
        self.primary_predicate = primary_predicate
        self.secondary_predicate = secondary_predicate
        self.g_linked_id = self.ressource_version.create_data_graph(namespace_list = [self.ns_linking_id[0], self.ns_linked_id[0], self.primary_predicate[0]], namespace_dict = self.namespaces)
        self.g_linked_id_endpoint = self.ressource_version_endpoint.create_data_graph(namespace_list = [self.ns_linking_id[0], self.ns_linked_id[0], self.secondary_predicate[0], self.ns_endpoint[0], "obo", "dcterms"], namespace_dict = self.namespaces)
        self.append_failure = list()
        self.request_failure = list()
        self.available_linked_ids = 0
        self.all_linked_ids = set()
        self.n_subjects_g_linked_id = 0
        self.n_triples_g_linked_id = 0
        self.n_subjects_g_linked_id_endpoint = 0
        self.n_triples_g_linked_id_endpoint = 0
        self.r_timeout = timeout
        
    def append_linked_ids(self, id_packed_list, index_list, query_builder, pack_size, add_f_out_path):
        """This function append a new Pccompound to the pccompound_list attribute. Using the cid, this function send a request to NCBI server via Eutils to get PMID association
        - id_packed_list: a list of pack of ids
        - index_list: the index of the current pack
        - query_builder: a eutils.QueryService object parameterized with cache, retmax, retmode, usehistory and especially the api_key
        - pack_size: the pack ids size
        """
        id_pack = id_packed_list[index_list]
        # Get linking_id associated linked_id. using try we test if request fail or not. If request fail, it's added to append_failure list
        print("Send request ...")
        # Intialyze signal timeout :
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(self.r_timeout)
        try:
            response = query_builder.elink({"dbfrom": self.dbfrom, "db": self.db, "id": id_pack})
        except TimeOutException:
            print("\nRequest timeout was reached !")
            with open(add_f_out_path + "elink.log", "a") as f_log:
                f_log.write("from id " + str(index_list * pack_size + 1) + " to id " + str((index_list + 1) * pack_size) + " :\n")
                f_log.write("Request Timeout\n")
                signal.alarm(0)
                return False
        except eutils.EutilsError as fail_request:
            print("\nRequest on Eutils for current compound pack has failed during process, with error name: %s \n" % (fail_request))
            with open(add_f_out_path + "elink.log", "a") as f_log:
                f_log.write("from id " + str(index_list * pack_size + 1) + " to id " + str((index_list + 1) * pack_size) + " :\n")
                f_log.write(str(fail_request) + "\n")
                signal.alarm(0)
            return False
        except (ValueError, requests.exceptions.RequestException) as e:
            print("\nThere was an request error: %s \n-- Compound cids is added to request_failure list" %(e))
            with open(add_f_out_path + "elink.log", "a") as f_log:
                f_log.write("from id " + str(index_list * pack_size + 1) + " to id " + str((index_list + 1) * pack_size) + " :\n")
                f_log.write(str(e) + "\n")
                signal.alarm(0)
            return False
        signal.alarm(0)
        print("Try to parse request results ...")
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
            self.fill_ids_link_graph(linking_id, linked_id_list)
            self.fill_ids_link_endpoint_graph(linking_id, linked_id_list, link_name_list)
            # On incrémente le nombre de pmids ajoutés :
            self.available_linked_ids += len(linked_id_list)
        return True
    
    def fill_ids_link_graph(self, linking_id, linked_id_list):
        """This function fill the g_linked_id graph with linking ids and linked ids associations.
        - linking_id: The linking identifier
        - linked_id_list: the linked id list from the request result
        """
        # Add all triples to graph
        for linked_id in linked_id_list:
            self.g_linked_id.add((self.namespaces[self.ns_linking_id[0]][self.ns_linking_id[1] + linking_id], self.namespaces[self.primary_predicate[0]][self.primary_predicate[1]], self.namespaces[self.ns_linked_id[0]][self.ns_linked_id[1] + linked_id]))
    
    def fill_ids_link_endpoint_graph(self, linking_id, linked_id_list, link_name_list):
        """This function create a rdflib graph containing all the cid - pmid endpoints associations contains in the Ensemble_pccompound object.
        - linking_id: The linking identifier
        - linked_id_list: the linked id list from the request result
        - link_name_list: the link_name list from the request result
        """
        for linked_id_index in range(0, len(linked_id_list)):
            linked_id = linked_id_list[linked_id_index]
            subject = self.ns_linking_id[1] + linking_id + "_" + self.ns_linked_id[1] + linked_id
            # Add to graph
            self.g_linked_id_endpoint.add((self.namespaces[self.ns_endpoint[0]][self.ns_endpoint[1] + subject], self.namespaces["obo"]['IAO_0000136'], self.namespaces[self.ns_linking_id[0]][self.ns_linking_id[1] + linking_id]))
            self.g_linked_id_endpoint.add((self.namespaces[self.ns_endpoint[0]][self.ns_endpoint[1] + subject], self.namespaces[self.secondary_predicate[0]][self.secondary_predicate[1]], self.namespaces[self.ns_linked_id[0]][self.ns_linked_id[1] + linked_id]))
            for link_name in link_name_list[linked_id_index]:
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
        """This function allow to clean and empty memory for bulky attributes"""
        self.g_linked_id = None
        self.g_linked_id = self.ressource_version.create_data_graph(namespace_list = [self.ns_linking_id[0], self.ns_linked_id[0], self.primary_predicate[0]], namespace_dict = self.namespaces)
        self.g_linked_id_endpoint = None
        self.g_linked_id_endpoint = self.ressource_version_endpoint.create_data_graph(namespace_list = [self.ns_linking_id[0], self.ns_linked_id[0], self.secondary_predicate[0], self.ns_endpoint[0], "obo", "dcterms"], namespace_dict = self.namespaces)
        self.append_failure = None
        self.append_failure = list()
        self.available_linked_ids = 0
    
    def export_ressource_metatdata(self, out_dir, uri_targeted_ressources):
        """
        This function is used to export the metadata graph.
        - out_dir: a path to the out directory
        - uri_targeted_ressources: A list of uri targeted ressource. As the association graph provides links between two ressources, it can be defined as a LinkSet. The targeted ressources for which the graph is providing associations are displayed is the metadata graph.
        """
        path_out_1 = out_dir + self.ressource_version.ressource + "/" + self.ressource_version.version + "/"
        path_out_2 = out_dir + self.ressource_version_endpoint.ressource + "/" + self.ressource_version_endpoint.version + "/"
        # On ajoute les infos pour la première ressource:
        self.ressource_version.add_version_attribute(RDF["type"], VOID["Linkset"])
        for uri_targeted_ressource in uri_targeted_ressources:
            self.ressource_version.add_version_attribute(VOID["target"], uri_targeted_ressource)
        self.ressource_version.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains RDF triples providind link between Entrez Ids from the NCBI database " + self.dbfrom + " to the " + self.db + " database"))
        self.ressource_version.add_version_attribute(DCTERMS["title"], rdflib.Literal(self.dbfrom + " to " + self.db + " RDF triples"))
        # On ajoute les infos pour la seconde ressource, les endpoint:
        self.ressource_version_endpoint.add_version_attribute(DCTERMS["description"], rdflib.Literal("This subset contains additionnal informations describing relations between Entrez Ids from the NCBI database " + self.dbfrom + " to the " + self.db + " database"))
        self.ressource_version_endpoint.add_version_attribute(DCTERMS["title"], rdflib.Literal(self.dbfrom + " to " + self.db + " endpoint RDF triples"))
        # On exporte le graph des metadata :
        print(" Export version graph with metadata ...\n", end = '')
        self.ressource_version.add_version_attribute(VOID["triples"], rdflib.Literal(self.n_triples_g_linked_id, datatype=XSD.long ))
        self.ressource_version.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(self.n_subjects_g_linked_id, datatype=XSD.long ))
        self.ressource_version_endpoint.add_version_attribute(VOID["triples"], rdflib.Literal(self.n_triples_g_linked_id_endpoint, datatype=XSD.long ))
        self.ressource_version_endpoint.add_version_attribute(VOID["distinctSubjects"], rdflib.Literal(self.n_subjects_g_linked_id_endpoint, datatype=XSD.long ))
        self.ressource_version.version_graph.serialize(destination= path_out_1 + "void.ttl", format='turtle')
        self.ressource_version_endpoint.version_graph.serialize(destination= path_out_2 + "void.ttl", format='turtle')
    
    def create_ressource(self, out_dir, id_list, pack_size, query_builder, max_size, add_f_out_path, ftp):
        """
        This function is used to create a new version of the CID_PMID and CID_PMID_enpoint ressources, by creating all the ressource and data graph associated to from information contained in the object.
        - out_dir: a path to an directory to write output files.
        - id_list: a list of input Entrez identifiers that will be used as linking ids
        - pack_size: the size of the cids pack that have to be send as request, refer to https://eutils.ncbi.nlm.nih.gov/entrez/query/static/entrezlinks.html
        - query_builder: a eutils.QueryService object parameterized with cache, retmax, retmode, usehistory and especially the api_key
        - max_size : the maximal number of pmids by files
        - ftp: ftp server adress on which data will be uploaded. A valid adress is not mandatory as data will not be automatically upload to the ftp server, an empty string can thus be used.  
        """
        # Intialyze .log file :
        with open(add_f_out_path + "elink.log", "w") as f_log:
            pass
        # Création des fichiers de sorties :
        add_files_path = add_f_out_path + "additional_files/" + self.ressource_version.version + "/"
        if not os.path.exists(add_files_path):
            os.makedirs(add_files_path)
        # On prépare les répertoire : 
        path_out_1 = out_dir + self.ressource_version.ressource + "/" + self.ressource_version.version + "/"
        path_out_2 = out_dir + self.ressource_version_endpoint.ressource + "/" + self.ressource_version_endpoint.version + "/"
        if not os.path.exists(path_out_1):
            os.makedirs(path_out_1)
        if not os.path.exists(path_out_2):
            os.makedirs(path_out_2)
        id_packed_list = [id_list[i * pack_size:(i + 1) * pack_size] for i in range((len(id_list) + pack_size - 1) // pack_size )]
        print("There are %d packed lists" %(len(id_packed_list)))
        # On réinitialise le fichier request failure et l'attribut (après avoir init packed_list au cas où on est sur un run à partir de self.request_failure):
        with open(add_files_path + "linking_ids_request_failed.txt", 'w') as f:
            pass
        self.request_failure = list()
        # On initialize les deux premières instances des graphs g_linked_id & g_linked_id_endpoint : 
        g_linked_id_name, g_linked_id_endpoint_name = self.ressource_version.ressource + "_" + str(self.file_index), self.ressource_version_endpoint.ressource + "_" + str(self.file_index)
        for index_list in range(0, len(id_packed_list)):
            print("-- Start getting pmids of list %d !\nTry to append compounds ..." %(index_list + 1))
            # On append les linked_ids: Si false est return c'est qu'il y a eu une erreur dans la requête, sinon on continue
            test_append = self.append_linked_ids(id_packed_list, index_list, query_builder, pack_size, add_f_out_path)
            if not test_append:
                print(" <!!!> Fail <!!!> \n There was an issue while querying NCBI server, check parameters. Try to continue to the next packed list. All ids are exported to request failure file.")
                self.request_failure.extend(id_packed_list[index_list])
                with open(add_files_path + "linking_ids_request_failed.txt", 'a') as f_request_failure:
                    for id_fail in id_packed_list[index_list]:
                        f_request_failure.write("%s\n" %(id_fail))
                continue
            print(" Ok\n", end = '')
            if self.available_linked_ids > max_size or (index_list == len(id_packed_list) - 1):
                if index_list == len(id_packed_list) - 1:
                    print("\t\tEnd was reached with %d new linking_id - linked_id association, start to export graph\n" %(self.available_linked_ids))
                else:
                    print("\t\tMaximal size (%d) was reached with %d new linking_id - linked_id association, start to export graph\n" %(max_size, self.available_linked_ids))
                print(" Ok\n\t\tTry to write and compress graph as .trig in %s and %s ..." %(path_out_1, path_out_2), end = '')
                # On export les graphs :
                try:
                    self.g_linked_id.serialize(destination=path_out_1 + g_linked_id_name + ".trig", format='trig')
                    self.ressource_version.add_DataDump(g_linked_id_name + ".trig.gz", ftp)
                except Exception as e:
                    print("Error while trying to serialize linked id graph at " + path_out_1 + g_linked_id_name + " : " +str(e))
                    sys.exit(3)
                try:
                    self.g_linked_id_endpoint.serialize(destination=path_out_2 + g_linked_id_endpoint_name + ".trig", format='trig')
                    self.ressource_version_endpoint.add_DataDump(g_linked_id_endpoint_name + ".trig.gz", ftp)
                except Exception as e:
                    print("Error while trying to serialize linked id graph endpoint at " + path_out_2 + g_linked_id_endpoint_name + " : " + str(e))
                    sys.exit(3)
                # On zip :
                try:
                    subprocess.run("gzip -f " + path_out_1 + g_linked_id_name + ".trig" + " " + path_out_2 + g_linked_id_endpoint_name + ".trig", shell = True, check=True, stderr = subprocess.PIPE)
                except subprocess.CalledProcessError as e:
                    print("Eroor while trying to compress files at " + path_out_1 + g_linked_id_name + " and " + path_out_2 + g_linked_id_endpoint_name + " : " + str(e))
                    sys.exit(3)
                # On incrémente les nombres de sujets et de triples :
                print("Ok\n\t\tIncrement numbers of triples and subjects from added triples ...", end = '')
                self.n_triples_g_linked_id += len(self.g_linked_id)
                self.n_triples_g_linked_id_endpoint += len(self.g_linked_id_endpoint)
                self.n_subjects_g_linked_id += len(self.get_all_linking_ids())
                self.n_subjects_g_linked_id_endpoint += len(self.get_all_linked_id_endpoints())
                with open(add_files_path + "s_metdata.txt", "w") as s_metadata_f:
                    s_metadata_f.write("%d\n" %(self.n_triples_g_linked_id))
                    s_metadata_f.write("%d\n" %(self.n_triples_g_linked_id_endpoint))
                    s_metadata_f.write("%d\n" %(self.n_subjects_g_linked_id))
                    s_metadata_f.write("%d\n" %(self.n_subjects_g_linked_id_endpoint))
                # On export les cid successful :
                print(" Ok\n\t\tTry tp export successful linking ids in " + add_files_path + "successful_linking_ids.txt ...", end = '')
                with open(add_files_path + "successful_linking_ids.txt", 'a') as f_success:
                    for success_id in self.get_all_linking_ids():
                        f_success.write("%s\n" %(success_id))
                print(" Ok\n\t\tTry tp export linking ids without linked_ids in " + add_files_path + "/linking_ids_without_linked_ids.txt ...", end = '')
                # On export les append failures :
                with open(add_files_path + "linking_ids_without_linked_ids.txt", 'a') as f_append_failure:
                    for append_failure_id in self.append_failure:
                        f_append_failure.write("%s\n" %(append_failure_id))
                print(" Ok\n\t\tTry to append new linked ids to the global set ...", end = '')
                self.all_linked_ids = self.all_linked_ids.union(self.get_all_linked_ids())
                print(" Ok\n\t\tExport all linked ids ...", end = '')
                # Use write instead of append ('a') to overwrite the file at each new call of the function because only union of linked_ids shouls be mapped, and with append it may have duplicates if there are supplementary trys for request failures
                with open(add_files_path + "all_linked_ids.txt", 'w') as f_all_linked_ids:
                    for linked_id in self.all_linked_ids:
                        f_all_linked_ids.write("%s\n" %(linked_id))
                print(" Ok\n\t\tTry to clear objects for next iteration ...", end = '')
                # On vide les graphs et les objects : 
                self.clean()
                # On incrémente le fichier :
                self.file_index += 1
                if index_list != len(id_packed_list) - 1:
                    print(" Ok\n\t\tTry to create new graphs ...")
                    # On créée deux nouveaux graphs :
                    g_linked_id_name, g_linked_id_endpoint_name = self.ressource_version.ressource + "_" + str(self.file_index), self.ressource_version_endpoint.ressource + "_" + str(self.file_index)
        print(" Ok\n End !\n", end = '')