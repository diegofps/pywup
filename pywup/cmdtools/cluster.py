from multiprocessing import Pool, cpu_count

from pywup.services.system import abort, error, WupError, Args, run, Route, Params
from pywup.services.cluster import Cluster

import shlex
import tqdm
import yaml
import sys
import os
import re


def do_new(cmd, args):
    p = Params(cmd, args)
    p.map("clustername", 1, None, "Name of the new cluster", mandatory=True)
    p.map("quantity", 1, None, "Number of nodes in the new cluster", mandatory=True)
    p.map("outputfolder", 1, ".", "Output folder to save the cluster file descriptor")
    
    if p.run():
        Cluster().new(p.clustername, int(p.quantity), p.outputfolder)


def do_rm(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Cluster().rm()


def do_start(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Cluster().start()


def do_stop(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Cluster().stop()


def do_open(cmd, args):
    p = Params(cmd, args)
    p.map("nodenumber", 1, None, "Number of node to open", mandatory=True)

    if p.run():
        Cluster().open(p.nodenumber)


def do_ls(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Cluster().ls()


def do_lsn(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Cluster().lsn()


def do_ip(cmd, args):
    p = Params(cmd, args)
    if p.run():
        for a, b in Cluster().ip():
            print(a, "=>", b)

def do_status(cmd, args):
    p = Params(cmd, args)
    if p.run():
        status = Cluster().status()

        lengths = [max([len(x) for x in array]) for array in status]

        for tup in zip(*status):
            cells = [x + " " * (lengths[i]-len(x)) for i, x in enumerate(tup)]
            print("    ".join(cells))


def main(cmd, args):
    r = Route(args, cmd)

    r.map("new", do_new, "Creates a new simulated cluster using an existing image")
    r.map("rm", do_rm, "Removes an existing simulated cluster")
    r.map("start", do_start, "Starts all nodes in the current cluster")
    r.map("stop", do_stop, "Stops all nodes in the current cluster")
    r.map("open", do_open, "Opens one of the cluster nodes")
    r.map("ls", do_ls, "Lists all clusters")
    r.map("lsn", do_lsn, "Lists all nodes in the cluster")
    #r.map("ip", do_ip, "Show the IP address of each node in the cluster")
    r.map("status", do_status, "Display info about the nodes: name, ip and running")
    
    r.run()
