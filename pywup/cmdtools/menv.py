from pywup.services.system import abort, error, WupError, Args, run, Route, Params, print_table
from pywup.services.menv import Simulation

from multiprocessing import Pool, cpu_count

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
        Simulation().new(p.clustername, int(p.quantity), p.outputfolder)


def do_rm(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Simulation().rm()


def do_start(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Simulation().start()


def do_stop(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Simulation().stop()


def do_open(cmd, args):
    p = Params(cmd, args)
    p.map("nodenumber", 1, None, "Number of node to open", mandatory=True)

    if p.run():
        Simulation().open(p.nodenumber)


def do_ls_clusters(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Simulation().ls_clusters()


def do_ls_nodes(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Simulation().ls_nodes()


def do_ip(cmd, args):
    p = Params(cmd, args)
    if p.run():
        for a, b in Simulation().ip():
            print(a, "=>", b)

def do_ls(cmd, args):
    p = Params(cmd, args)
    if p.run():
        status = Simulation().ls()
        print_table(status)


def main(cmd, args):
    r = Route(args, cmd)

    r.map("new", do_new, "Creates a simulated cluster using the current env on your local machine")
    r.map("rm", do_rm, "Removes the current simulated cluster")
    r.map("start", do_start, "Starts all nodes in the current cluster")
    r.map("stop", do_stop, "Stops all nodes in the current cluster")
    r.map("open", do_open, "Opens one of the cluster nodes")
    r.map("lsc", do_ls_clusters, "Lists all simulated clusters")
    r.map("lsn", do_ls_nodes, "Lists all nodes in this cluster")
    r.map("ls", do_ls, "Display node's info like name, ip, running, etc")
    
    r.run()
