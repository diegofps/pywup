from multiprocessing import Pool, cpu_count

from pywup.services.general import lookup_env, get_image_name, get_container_name
from pywup.services.system import abort, error, WupError, Args, run, Route
from pywup.services.cluster import Cluster

import shlex
import tqdm
import yaml
import sys
import os
import re


def do_new(args):
    clustername = args.pop_parameter()
    qtt = int(args.pop_parameter())
    outfolder = args.pop_parameter() if args.has_next() else "."

    Cluster().new(clustername, qtt, outfolder)


def do_rm(args):
    Cluster().rm()


def do_start(args):
    Cluster().start()


def do_stop(args):
    Cluster().stop()


def do_open(args):
    node_number = args.pop_parameter()
    Cluster().open(node_number)


def do_ls(args):
    Cluster().ls()


def do_lsn(args):
    Cluster().lsn()


def do_ip(args):
    for a, b in Cluster().ip():
        print(a, "=>", b)

def main(args):
    r = Route(args)

    r.map("new", do_new, "Creates a new simulated cluster using an existing image")
    r.map("rm", do_rm, "Removes an existing simulated cluster")
    r.map("start", do_start, "Starts all containers for a given cluster")
    r.map("stop", do_stop, "Stops all containers for a given cluster")
    r.map("open", do_open, "Opens one of the cluster machines")
    r.map("ls", do_ls, "Lists all clusters")
    r.map("lsn", do_lsn, "Lists all nodes in the cluster")
    r.map("ip", do_ip, "Show the IP address of each node in the cluster")
    
    r.run()
