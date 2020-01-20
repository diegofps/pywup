from multiprocessing import Pool, cpu_count

from pywup.services.system import abort, error, WupError, Args, run, Route, Params
from pywup.services.general import lookup_env, get_image_name, get_container_name
from pywup.services.cluster import Cluster

import shlex
import tqdm
import yaml
import sys
import os
import re


def do_new(cmd, args):
    params = Params(cmd, args)
    params.map("clustername", 1, None, "Name of the cluster", mandatory=True)
    params.map("quantity", 1, None, "Number of nodes in the cluster", mandatory=True)
    params.map("outputfolder", 1, None, "Output folder to save the cluster file descriptor")
    
    if params.run():
        outfolder = params.get("outputfolder") if params.has("outputfolder") else "."
        clustername = params.get("clustername")
        qtt = int(params.get("quantity"))

        Cluster().new(clustername, qtt, outfolder)


def do_rm(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Cluster().rm()


def do_start(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Cluster().start()


def do_stop(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Cluster().stop()


def do_open(cmd, args):
    params = Params(cmd, args)
    params.map("nodenumber", 1, None, "Number of node to open", mandatory=True)

    if params.run():
        node_number = params.get("nodenumber")
        Cluster().open(node_number)


def do_ls(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Cluster().ls()


def do_lsn(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Cluster().lsn()


def do_ip(cmd, args):
    params = Params(cmd, args)
    if params.run():
        for a, b in Cluster().ip():
            print(a, "=>", b)

def main(cmd, args):
    r = Route(args, cmd)

    r.map("new", do_new, "Creates a new simulated cluster using an existing image")
    r.map("rm", do_rm, "Removes an existing simulated cluster")
    r.map("start", do_start, "Starts all nodes in the current cluster")
    r.map("stop", do_stop, "Stops all nodes in the current cluster")
    r.map("open", do_open, "Opens one of the cluster nodes")
    r.map("ls", do_ls, "Lists all clusters")
    r.map("lsn", do_lsn, "Lists all nodes in the cluster")
    r.map("ip", do_ip, "Show the IP address of each node in the cluster")
    
    r.run()
