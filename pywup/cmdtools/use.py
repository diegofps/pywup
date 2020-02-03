from pywup.services.io import Preferences, lookup_env, lookup_cluster
from pywup.services.system import Params, colors, expand_path

import sys
import os


def show(pref):
    print()

    show = lambda a,b: print(colors.white(a), colors.green(b) if b else colors.red("None"))

    show("env_name:", pref.env_name)
    show("env_filepath:", pref.env_filepath)
    print()

    show("cluster_name:", pref.cluster_name)
    show("cluster_env_name:", pref.cluster_env_name)

    show("cluster_filepath:", pref.cluster_filepath)
    show("cluster_env_filepath:", pref.cluster_env_filepath)
    print()

    show("arch_name:", pref.arch_name)

    sys.stdout.write(colors.white("State: "))
    try:
        with open(expand_path("~/.wup/state"), "r") as fin:
            print(colors.green(fin.readline()))
    except FileNotFoundError:
        print(colors.red("None"))

    print()


def update_arch(arch, pref):

    if arch == "-":
        pref.arch_name = None
    else:
        pref.arch_name = arch


def update_env(env, pref):

    if env == "-":
        pref.env_name = None
        pref.env_filepath = None
    
    else:
        name, filepath = lookup_env(env)

        pref.env_name = name
        pref.env_filepath = filepath


def update_cluster(cluster, pref):

    if cluster == "-":
        pref.cluster_name = None
        pref.cluster_filepath = None
        pref.cluster_env_name = None
        pref.cluster_env_filepath = None
    
    else:
        name, filepath, cluster = lookup_cluster(cluster)

        if cluster.docker_based:
            pref.cluster_name = name
            pref.cluster_filepath = filepath
            pref.cluster_env_name = cluster.env_name
            pref.cluster_env_filepath = cluster.env_filepath

        else:
            pref.cluster_name = name
            pref.cluster_filepath = filepath
            pref.cluster_env_name = None
            pref.cluster_env_filepath = None


def main(cmd, args):
    desc1 = "Name or path of environment file"
    desc2 = "Name or path of cluster file"
    desc3 = "Configure only machines belonging to this remote architecture"

    params = Params(cmd, args)
    params.map("env", 1, None, desc1)
    params.map("cluster", 1, None, desc2)
    params.map("arch", 1, None, desc3)

    params.map("--e", 1, None, desc1)
    params.map("--c", 1, None, desc2)
    params.map("--a", 1, None, desc3)
    params.map("--show", 0, None, "Show what is being used")
    
    if params.run():
        env = params.__e if params.has("--e") else params.env
        cluster = params.__c if params.has("--c") else params.cluster
        arch = params.__a if params.has("--a") else params.arch

        pref = Preferences()

        if env:
            update_env(env, pref)
        
        if cluster:
            update_cluster(cluster, pref)

        if arch:
            update_arch(arch, pref)
        
        pref.save()

        if params.__show:
            show(pref)
