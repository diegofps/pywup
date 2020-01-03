from collections import defaultdict
from subprocess import Popen, PIPE

from pywup.services.system import quote
from pywup.services import conf

import numpy as np
import shlex
import yaml
import csv
import sys
import os
import re


def get_open_cmd(container_name, bash_init, tty=True):
    o = "".join(["source \"$HOME/.bashrc\"\n"] + bash_init)
    k = quote(o)
    b = quote("bash --init-file <(echo " + k + ")")
    tty = "-it " if tty else "-i "
    c = "docker exec " + tty + container_name + " bash -c " + b.replace("$", "\\$")
    return c


def parse_env(tag, cmd):
    variables, templates = parse_templates(tag)

    if not "BASE" in variables:
        variables["BASE"] = "ubuntu:bionic"
    
    if not "WORKDIR" in variables:
        variables["WORKDIR"] = "/"

    if not "WUPCMD" in variables:
        variables["WUPCMD"] = cmd

    bash_init = [k + "=\"" + variables[k] + "\"\n" for k in variables]
    bash_init.append("cd %s\n" % variables["WORKDIR"])

    for name in ["LAUNCH", "POSTDEPLOY", "BUILD", "OPEN", "EXEC", "NEW"]:
        templates[name] = bash_init + templates[name]
    
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

    return variables, templates


def get_export_filepath(project, tag):
    return "wup__{}__{}.gz".format(project, tag)


def get_container_name(projectname, tag, clustername=None, i=None, quantity=None):
    if clustername:
        return "wcl__{}__{}__{}__{}".format(clustername, projectname, tag, i)
    else:
        return "wup__{}_{}".format(projectname, tag)


def get_image_name(projectname, tag):
    return "wup__{}:{}".format(projectname, tag)


def parse_image_name(name):
    tmp = name.split(":")

    if "__" in name:
        error("Names must not contain two consecutive underscores (__)")

    if len(tmp) == 1:
        projectname, tag = conf.get("project.name"), tmp[0]
    
    elif len(tmp) == 2:
        projectname, tag = tmp
    
    else:
        error("Too many \":\" in", name)
    
    if tag == "temp":
        error("You cannot have a container named temp")
    
    return projectname, tag



def parse_templates(tag):
    filepath = "./{}.env".format(tag)
    templates = defaultdict(list)
    variables = {}

    if not os.path.exists(filepath):
        return variables, templates

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
    project = conf.get("wup.project", scope="global", failOnMiss=False)
    tag = conf.get("wup.tag", scope="global", failOnMiss=False)
    cluster = conf.get("wup.cluster_name", scope="global", failOnMiss=False)

    if project and cluster:
        state = project + ":" + tag + "@" + cluster
    
    elif project:
        state = project + ":" + tag + "@-"

    elif cluster:
        state = "-@" + cluster
    
    else:
        state = "-@-"

    folderpath = os.path.expanduser("~/.wup")

    os.makedirs(folderpath, exist_ok=True)
    with open(os.path.join(folderpath, "state"), "w") as fout:
        fout.write(state)
