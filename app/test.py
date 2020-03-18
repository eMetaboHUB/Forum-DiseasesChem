g = create_empty_graph(["reference", "fabio", "mesh"], namespaces)
for l in lines.pop():
    parsed_l = re.split("[\",]", l)
    print(parsed_l)
    g.add((rdflib.URIRef(parsed_l[1]), namespaces["fabio"].hasSubjectTerm, rdflib.URIRef(parsed_l[4])))