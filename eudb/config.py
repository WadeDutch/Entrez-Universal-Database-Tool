import configparser

config = configparser.ConfigParser()

def resetsettings():
    config["settings"] = {  "maxresults":"20",
                            "database":"pubmed",
                            "links":"1",
                            "authors":"1",
                            "date":"1",
                            "source":"1",
                            "title":"1",
                            "journal":"1",
                            "displayorder":"title,authors,date,source,journal,links"}
    with open("settings.ini", "w+") as configfile:
        config.write(configfile)


def loadsettings():
    config.read("settings.ini")
    return config["settings"]

def changesettings(changes): #list of key value pairs in tuples
    config.read("settings.ini")
    for key, value in changes:
        config["settings"][key] = str(value)
    with open("settings.ini", "w+") as configfile:
        config.write(configfile)
