from pywup.services.system import error
from pywup.services import conf

import os


def get_export_filepath(name, tag):
    if tag:
        return "wimg__" + name + "." + tag + ".gz"
    else:
        return "wimg__" + name + ".gz"


def get_container_name(tag, clustername=None, i=None):
    if clustername:
        return "wclus__{}__{}__{}".format(clustername, tag, i)
    else:
        return "wcont__" + tag


def get_image_name(tag):
    return "wimg:" + tag


def lookup_cluster(name):
    if name == "-":
        return "-", ""
    
    if not os.path.exists(name):
        filepath = "./" + name + ".cluster"
        if not os.path.exists(filepath):
            error("Could not find a cluster definition for:", name)
    else:
        filepath = name
        name = os.path.splitext(os.path.basename(name))[0]
    
    if "__" in name:
        error("Cluster names must not contain two consecutive underscores (__)")

    if name == "temp":
        error("You cannot use a cluster named temp")
    
    return name, filepath


def lookup_env(name):
    if name == "-":
        return "-", ""

    if not os.path.exists(name):
        filepath = "./" + name + ".env"
        if not os.path.exists(filepath):
            filepath = "~/.wup/projects/" + name + "/" + name + ".env"
            if not os.path.exists(filepath):
                error("Could not find an env declaration for:", name)
    else:
        filepath = name
        name = os.path.splitext(os.path.basename(name))[0]
    
    if "__" in name:
        error("Names must not contain two consecutive underscores (__)")

    if name == "temp":
        error("You cannot use a container named temp")
    
    return name, filepath


def update_state():
    env_name = conf.get("wup.env_name", scope="global", failOnMiss=False)
    cluster_name = conf.get("wup.cluster_name", scope="global", failOnMiss=False)
    state = (env_name if env_name else "-") + "@" + (cluster_name if cluster_name else "-")
    folderpath = os.path.expanduser("~/.wup")
    
    os.makedirs(folderpath, exist_ok=True)

    with open(os.path.join(folderpath, "state"), "w") as fout:
        fout.write(state)
