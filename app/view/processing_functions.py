import requests
import pandas as pd
import io


def send_request(url, prefix, request, g_from, cpd_list = []):
    """
    Send a request to the sparql endpoint
    """
    str_from = "\n".join(["FROM <" + uri + ">" for uri in g_from])
    str_cpd_list = " ".join(["cid:CID" + id for id in cpd_list])
    try:
        query = prefix + request % {"from":str_from, "cid":str_cpd_list}
    except Exception as e:
        print("There was an error while trying to fill the request: " + str(e))
        print("Please, check the fields send to the function correspond to the expected fields in the request")

    # Request params
    header = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "text/csv"
    }
    data = {
        "format": "csv",
    }
    # Format request
    data["query"] = query
    
    print("Query: ")
    print(query)
    # Send
    r = requests.post(url = url, headers = header, data = data)
    if r.status_code != 200:
        print("Error in request: " + r.text)
    return (r.text)


def get_view(url, prefix, request, g_from, out, cpd_list = []):
    print("=============================================")
    r = send_request(url, prefix, request, g_from, cpd_list)
    view = pd.read_csv(io.StringIO(r))
    view.to_csv(out, index = False)