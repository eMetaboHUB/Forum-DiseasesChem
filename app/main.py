
import rdflib
import eutils
from Elink_ressource_creator import Elink_ressource_creator
from Database_ressource_version import Database_ressource_version
from parse_pubchem_RDF import parse_pubchem_RDF
from Request_RESTful_PubChem import REST_ful_bulk_download
from download_functions import download_MeSH, download_pubChem
from process_SMBL import extract_ids_from_SMBL_by_URI_prefix, merge_SMBL_and_annot_graphs
# The Api_key can be found on the NCBI account.
# Creating the directory of all namespaces
namespaces = {
    "cito": rdflib.Namespace("http://purl.org/spar/cito/"),
    "compound": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/compound/"),
    "reference": rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/reference/"),
    "endpoint":	rdflib.Namespace("http://rdf.ncbi.nlm.nih.gov/pubchem/endpoint/"),
    "obo": rdflib.Namespace("http://purl.obolibrary.org/obo/"),
    "dcterms": rdflib.Namespace("http://purl.org/dc/terms/"),
    "fabio": rdflib.Namespace("http://purl.org/spar/fabio/"),
    "mesh": rdflib.Namespace("http://id.nlm.nih.gov/mesh/"),
    "void": rdflib.Namespace("http://rdfs.org/ns/void#"),
    "skos": rdflib.Namespace("http://www.w3.org/2004/02/skos/core")
}

# Listes des features Compounds - Descriptors que l'on souhaite récupérées : 
feature_list = ["_Canonical_SMILES",
"_Covalent_Unit_Count",
"_Defined_Atom_Stereo_Count",
"_Defined_Bond_Stereo_Count",
"_Exact_Mass",
"_Hydrogen_Bond_Acceptor_Count",
"_Hydrogen_Bond_Donor_Count",
"_IUPAC_InChI",
"_Isomeric_SMILES",
"_Isotope_Atom_Count",
"_Molecular_Formula",
"_Molecular_Weight",
"_Mono_Isotopic_Weight",
"_Non-hydrogen_Atom_Count",
"_Preferred_IUPAC_Name",
"_Rotatable_Bond_Count",
"_Structure_Complexity",
"_TPSA",
"_Total_Formal_Charge",
"_Undefined_Atom_Stereo_Count",
"_Undefined_Bond_Stereo_Count",
"_XLogP3-AA"]


# TODO: Créer la fonction de parsing de graph pour les PubChem compounds (si besoin) afin de ne récupérer que les propriété qui nous interressent. On pourrait le faire en utilisant une sélection de type CHEMINF que celles-ci doivent avoir.
# TODO: Créer une fonction qui permettrait de filtrer les objets. Par exemple la propriété Stereoisomer a pour objets une ensemble de CID, mais tout ces CID ne sont pas présents dans notre graph, car par exemple tous n'appartiennent pas au réseau. les filtrer ?



apiKey = "0ddb3479f5079f21272578dc6e040278a508"
# Building requests
query_builder = eutils.QueryService(cache = False,
                                    default_args ={'retmax': 10000000, 'retmode': 'xml', 'usehistory': 'y'},
                                    api_key = apiKey)
# On crée le graph SBML mergé :
smbl_graph = merge_SMBL_and_annot_graphs("data/HumanGEM/HumanGEM.ttl", ["synonyms.trig", "infered_uris.trig", "infered_uris_synonyms.trig"], "data/annot_graphs/2020-04-06/")
cid_list = extract_ids_from_SMBL_by_URI_prefix(smbl_graph, "http://identifiers.org/pubchem.compound/")
# Create Graph
sbml_cid_pmid = Elink_ressource_creator(ressource_name = "CID_PMID", 
                                        version = "SMBL_2020-15-04_2", 
                                        dbfrom = "pccompound",
                                        db = "pubmed",
                                        ns_linking_id = ("compound", "CID"),
                                        ns_linked_id = ("reference", "PMID"),
                                        ns_endpoint = ("endpoint", ""),
                                        primary_predicate = ("cito", "isDiscussedBy"),
                                        secondary_predicate = ("cito", "citeAsDataSource"),
                                        namespaces = namespaces)
# Launch fetching
sbml_cid_pmid.create_ressource("data/", cid_list, 10000, query_builder, 5000000, [rdflib.URIRef("http://database/ressources/PubChem/compound/2020-03-06"), rdflib.URIRef("http://database/ressources/PubChem/reference/2020-03-06")])
# get all pmids :
sbml_all_pmids = sbml_cid_pmid.all_linked_ids
smbl_compound_ids_features_list = [id + f for id in cid_list for f in feature_list]


# ====  TEST FROM PMID to CID === #
g = rdflib.Graph()
g.parse("data/PubChem_References/reference/2020-03-06/pc_reference_type.ttl", format='turtle')
pmid_list = [pmid.split("http://rdf.ncbi.nlm.nih.gov/pubchem/reference/PMID")[1] for pmid in g.subjects()]
g = None

pmid_cid = Elink_ressource_creator(ressource_name = "PMID_CID", 
                                        version = None, 
                                        dbfrom = "pubmed",
                                        db = "pccompound",
                                        ns_linking_id = ("reference", "PMID"),
                                        ns_linked_id = ("compound", "CID"),
                                        ns_endpoint = ("endpoint", ""),
                                        primary_predicate = ("cito", "discusses"),
                                        secondary_predicate = ("cito", "isCitedAsDataSourceBy"),
                                        namespaces = namespaces)
pmid_cid.create_ressource("data/", pmid_list, 10000, query_builder, 5000000, [rdflib.URIRef("http://database/ressources/PubChem/reference/2020-03-06"), rdflib.URIRef("http://database/ressources/PubChem/compound/2020-03-06")])

# === End === #


# Download RDF

download_MeSH("data/MeSH/", namespaces)

download_pubChem("reference", "reference", "data/PubChem_References/")

download_pubChem("compound/general/pc_compound_type.ttl.gz", "compound", "data/PubChem_Compound/")
download_pubChem("compound/general", "compound", "/media/mxdelmas/DisqueDur/data_max/PubChem_Compound/")
download_pubChem("descriptor/compound", "descriptor", "/media/mxdelmas/DisqueDur/data_max/PubChem_Compound/")


requests_failed = REST_ful_bulk_download(graph = 'reference', predicate = 'fabio:hasPrimarySubjectTerm', out_name = 'PrimarySubjectTerm',
                                         start_offset = 0, out_dir = "data/PubChem_References/",
                                         ressource_name = "PrimarySubjectTerm", namespaces_list = ["reference", "fabio", "mesh"],
                                         namespaces_dict = namespaces,
                                         version = None)





### ==== WITH SBML FILE ==== ###



parse_pubchem_RDF(input_ressource_directory = "data/PubChem_References/reference/2020-03-06/", 
                  all_ids = sbml_all_pmids,
                  prefix = "reference:PMID", 
                  out_dir = "data/PubChem_References/",
                  input_ressource_file = "data/PubChem_References/reference/ressource_info_reference_2020-03-06.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/reference/2020-03-06"),
                  filtered_ressource_name = "referenceFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/CID_FROM_CHEBI"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = "CID_FROM_CHEBI",
                  separator = '\t')

parse_pubchem_RDF(input_ressource_directory = "data/PubChem_References/PrimarySubjectTerm/2020-03-20/",
                  all_ids = sbml_all_pmids,
                  prefix = "reference:PMID",
                  out_dir = "data/PubChem_References/",
                  input_ressource_file = "data/PubChem_References/PrimarySubjectTerm/ressource_info_PrimarySubjectTerm_2020-03-20.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PrimarySubjectTerm/2020-03-20"),
                  filtered_ressource_name = "PrimarySubjectTermFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/SMBL_2020-04-06"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = "TEST",
                  separator = ' ')

parse_pubchem_RDF(input_ressource_directory = "/media/mxdelmas/DisqueDur/data_max/PubChem_Compound/compound/2020-03-06/",
                  all_ids = cid_list,
                  prefix = "compound:CID",
                  out_dir = "data/PubChem_Compound/",
                  input_ressource_file = "/media/mxdelmas/DisqueDur/data_max/PubChem_Compound/compound/ressource_info_compound_2020-03-06.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/compound/2020-03-06"),
                  filtered_ressource_name = "CompoundFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/SMBL_2020-04-06"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = "SMBL_2020-04-06",
                  separator = '\t')

parse_pubchem_RDF(input_ressource_directory = "/media/mxdelmas/DisqueDur/data_max/PubChem_Descriptor/descriptor/2020-03-06/",
                  all_ids = smbl_compound_ids_features_list,
                  prefix = "descriptor:CID",
                  out_dir = "data/PubChem_Descriptor/",
                  input_ressource_file = "/media/mxdelmas/DisqueDur/data_max/PubChem_Descriptor/descriptor/ressource_info_descriptor_2020-03-06.ttl",
                  input_ressource_uri = rdflib.URIRef("http://database/ressources/PubChem/descriptor/2020-03-06"),
                  filtered_ressource_name = "DescriptorFiltered",
                  input_ids_uri = rdflib.URIRef("http://database/ressources/CID_PMID/SMBL_2020-04-06"),
                  isZipped = True,
                  namespace_dict = namespaces,
                  version = "SMBL_2020-04-06",
                  separator = '\t')