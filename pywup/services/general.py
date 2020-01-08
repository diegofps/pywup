from collections import defaultdict
from subprocess import Popen, PIPE

from pywup.services.system import quote, error, abort
from pywup.services import conf

import numpy as np
import shlex
import yaml
import csv
import sys
import os
import re



def parse_env(tag):
    variables, templates = parse_templates(tag)

    if not "BASE" in variables:
        variables["BASE"] = "ubuntu:bionic"
    
    if not "WORKDIR" in variables:
        variables["WORKDIR"] = "/"

    #if not "RUN" in variables:
    #    variables["RUN"] = cmd

    if not "EXPOSE" in variables:
        variables["EXPOSE"] = ""

    if not "MAP_PORTS" in variables:
        variables["MAP_PORTS"] = ""

    workdir = variables["WORKDIR"]
    bashrc = [k + "=\"" + variables[k] + "\"\n" for k in variables] + ["mkdir -p %s\n" % workdir, "cd %s\n" % workdir]

    #for name in ["LAUNCH", "POSTDEPLOY", "BUILD", "OPEN", "EXEC", "NEW"]:
    #    templates[name] = bash_init + templates[name]
    
    volumes = templates["VOLUMES"]
    if volumes:
        volumes = [j.strip() for j in volumes]
        volumes = [j for j in volumes if j]
        volumes = [os.path.expanduser(j) for j in volumes]
        volumes = [os.path.abspath(j) for j in volumes]

        for v in volumes:
            src = v.split(":")[0]

            if not os.path.exists(src):
                error("Missing source directory in host:", src)
            
            if not os.path.isdir(src):
                error("Source volume in host is not a directory:", src)
        
        templates["VOLUMES"] = volumes

    return variables, templates, bashrc


def get_export_filepath(tag):
    return "wimg__" + tag + ".gz"


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


def parse_templates(filepath):
    templates = defaultdict(list)
    variables = {}

    #if not os.path.exists(filepath):
    #    return variables, templates

    order = []
    rows = []

    with open(filepath, "r") as fin:
        for i, line in enumerate(fin):
            if line.startswith("@") and line.endswith("@\n"):
                order.append((line[1:-2], i))
            rows.append(line)
        order.append(("eof", i+1))
    
    for i in range(1, len(order)):
        name, first = order[i-1]
        _, last = order[i]
        selection = rows[first+1:last]

        if name == "VARS":
            for row in selection:
                row = row.strip()
                
                if not row:
                    continue

                cells = row.split("=", maxsplit=1)

                if len(cells) != 2:
                    error("Invalid variable declaration:", row)
                
                key, value = cells
                variables[key.strip()] = value.strip()
        
        else:
            templates[name] = selection
    
    return variables, templates


def find_column(headers, header):
    return np.where(headers == header)[0].item()


def update_state():
    env_name = conf.get("wup.env_name", scope="global", failOnMiss=False)
    cluster_name = conf.get("wup.cluster_name", scope="global", failOnMiss=False)
    state = (env_name if env_name else "-") + "@" + (cluster_name if cluster_name else "-")
    folderpath = os.path.expanduser("~/.wup")
    
    os.makedirs(folderpath, exist_ok=True)

    with open(os.path.join(folderpath, "state"), "w") as fout:
        fout.write(state)
