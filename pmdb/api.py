import requests
import json

eURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
searchURL = "esearch.fcgi"
summaryURL = "esummary.fcgi"
fetchURL = "efetch.fcgi"
dblist = json.loads(requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi", params={"retmode":"json"}).text)["einforesult"]["dblist"]
endl = "\n"

#responseJSON = dumps(bf.data(fromstring(r.text)))
def getdblist():
    return dblist

def searchdb(qstring, db):
    if (db not in dblist):
        raise ValueError("Invalid Database")

    payload = {
        #"tool":"nameTBD",
        #"email":"agentheavybear@gmail.com",
        "db":db,
        "term":qstring,
        "usehistory":"y",
        "retmode":"json"
    }

    r = requests.get(eURL+searchURL, params=payload)
    rjson = json.loads(r.text)
    WebEnv = rjson["esearchresult"]["webenv"]
    Key = rjson["esearchresult"]["querykey"]
    count = rjson["esearchresult"]["count"]

    return WebEnv, Key, count

def getsummary(WebEnv, Key, start=0, count=20, db="pubmed"):
    payload = {
        #"tool":"nameTBD",
        #"email":"agentheavybear@gmail.com"
        "db":db,
        "query_key":Key,
        "WebEnv":WebEnv,
        "retstart":start,
        "retmax":count,
        "retmode":"json"
    }

    r = requests.get(eURL+summaryURL, params=payload)
    rjson = json.loads(r.text)
    results = rjson["result"]

    return results

def getresultline(docsum, target, database):
    if (database == "pubmed"):
        if (target == "journal"):
            try:
                return "Journal: "+docsum["fulljournalname"]+endl if not docsum["fulljournalname"]=="" else "Journal: Not Found"+endl
            except:
                return "Journal: Not Found"+endl
        elif (target == "authors"):
            try:
                #generate authors
                authors=[]
                for author in docsum["authors"]:
                    authors.append(author["name"])
                return "Authors: "+", ".join(authors)+endl if not authors==[] else "Authors: Not Found"+endl
            except:
                return "Authors: Not Found"+endl
        elif (target == "date"):
            try:
                return "Date Published: "+docsum["pubdate"]+endl if not docsum["pubdate"]=="" else "Date Published: Not Found"+endl
            except:
                return "Date Published: Not Found"+endl
        elif (target == "source"):
            try:
                return "Source: "+docsum["source"]+endl if not docsum["source"]=="" else "Source: Not Found."+endl
            except:
                return "Source: Not Found."+endl
        elif (target == "title"):
            try:
                return "Title: "+docsum["title"]+endl if not docsum["title"]=="" else "Title: Not Found"+endl
            except:
                return "Title: Not Found"+endl
    #end pubmed return code
    return "Nothing Found"
