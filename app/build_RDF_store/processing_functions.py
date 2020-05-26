import rdflib
import glob
import sys

def test_dl_data(out_path):
    ressource_info_f = glob.glob(out_path + "ressource_info_*.ttl")
    if len(ressource_info_f) == 1:
        ressource_info_f = ressource_info_f[0]
        print("Data already downloaded !\nTry to parse : " + ressource_info_f)
        g = rdflib.Graph()
        g.parse(ressource_info_f, format = "turtle")
        uri_v = [uri.toPython() for uri in g.objects(None, rdflib.URIRef("http://purl.org/dc/terms/hasVersion"))][0]
        return uri_v.split('/')[-1], uri_v
    elif len(ressource_info_f) > 1:
        print("More than on ressource info file in " + out_path + " can't continue, exit.")
        sys.exit(3)
    else:
        return None, None