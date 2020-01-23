from pywup.services.system import error, expand_path
from pywup.services import conf

import os


def get_export_filepath(name, tag=None, arch=None):
    if tag is None:
        from datetime import datetime
        n = datetime.now()
        tag = "%04d%02d%02d-%02d%02d" % (n.year, n.month, n.day, n.hour, n.minute)
    
    if arch is None:
        arch = "generic"

    return ".".join([name, arch, tag, "gz"])


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
    
    candidate = expand_path(name)

    if not os.path.exists(candidate):
        candidate = expand_path("./" + name + ".cluster")
        if not os.path.exists(candidate):
            error("Could not find a cluster definition for:", name)
    else:
        name = os.path.splitext(os.path.basename(name))[0]
    
    if "__" in name:
        error("Cluster names must not contain two consecutive underscores (__)")

    if name == "temp":
        error("You cannot use a cluster named temp")
    
    return name, candidate


def lookup_env(name):
    if name == "-":
        return "-", ""

    candidate = expand_path(name)

    if not os.path.exists(candidate):
        candidate = expand_path("./" + name + ".env")
        if not os.path.exists(candidate):
            candidate = expand_path("~/.wup/projects/" + name + "/" + name + ".env")
            if not os.path.exists(candidate):
                error("Could not find an env declaration for:", name)
    else:
        name = os.path.splitext(os.path.basename(name))[0]
    
    if "__" in name:
        error("Names must not contain two consecutive underscores (__)")

    if name == "temp":
        error("You cannot use an env named temp")
    
    return name, candidate


def update_state():
    env_name = conf.get("wup.env_name", scope="global", failOnMiss=False)
    cluster_name = conf.get("wup.cluster_name", scope="global", failOnMiss=False)
    cluster_env = conf.get("wup.cluster_env", scope="global", failOnMiss=False)
    arch = conf.get("wup.arch", scope="global", failOnMiss=False)

    env_name = env_name if env_name else "-"
    cluster_name = cluster_name if cluster_name else "-"
    cluster_env = cluster_env if cluster_env else "-"
    arch = arch if arch else "-"

    state = env_name + "," + cluster_env + "@" + cluster_name + "." + arch
    
    folderpath = os.path.expanduser("~/.wup")
    os.makedirs(folderpath, exist_ok=True)

    with open(os.path.join(folderpath, "state"), "w") as fout:
        fout.write(state)
