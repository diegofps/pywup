#!/usr/bin/env python3

from pywup.services.general import lookup_env, lookup_cluster, update_state
from pywup.services.system import abort, error, WupError, Route
from pywup.services import conf
from pywup import cmdtools

import sys
import os


def use(args):
    name1 = None
    name2 = None

    while args.has_next():
        if args.has_cmd():
            cmd = args.pop_cmd()

            if cmd == "--env":
                name1 = args.pop_parameter()
            
            elif cmd == "--cluster":
                name2 = args.pop_parameter()
            
            else:
                error("Invalid parameter:", cmd)
            
        else:
            if name1 is None:
                name1 = args.pop_parameter()
            elif name2 is None:
                name2 = args.pop_parameter()
            else:
                error("Too many parameters")
    
    if name1:
        name, filepath = lookup_env(name1)
    else:
        name, filepath = "", ""

    conf.set("wup.env_name", name, scope="global")
    conf.set("wup.env_filepath", filepath, scope="global")

    if name2:
        name, filepath = lookup_cluster(name2)
    else:
        name, filepath = "", ""

    conf.set("wup.cluster_name", name, scope="global")
    conf.set("wup.cluster_filepath", filepath, scope="global")

    update_state()


def collect(args):
    from pywup.cmdtools.collect import main
    main(args)

def heatmap(args):
    from pywup.cmdtools.heatmap import main
    main(args)

def bars(args):
    from pywup.cmdtools.bars import main
    main(args)

def backup(args):
    from pywup.cmdtools.backup import main
    main(args)

def q(args):
    from pywup.cmdtools.q import main
    main(args)

def config(args):
    from pywup.cmdtools.conf import main
    main(args)

def env(args):
    from pywup.cmdtools.env import main
    main(args)

def renv(args):
    from pywup.cmdtools.renv import main
    main(args)

def cluster(args):
    from pywup.cmdtools.cluster import main
    main(args)


def wup(argv):
    r = Route(argv)

    r.map("use", use, "Set env and/or cluster files")
    r.map("collect", collect, "Run an app multiple times, variating its parameters and collecting its output attributes")
    r.map("heatmap", heatmap, "Plot a heatmap image using the data collected")
    r.map("bars", bars, "Plot a bars image using the data collected")
    r.map("backup", backup, "Backup system files into a folder synced to a cloud")
    r.map("q", q, "Run SQL in CSV files (Requires python-q)")
    r.map("conf", config, "Set/Get wup configuration parameters")
    r.map("env", env, "Manage docker environments for development and cluster deploy (wup style)")
    r.map("remote", renv, "Manager remote environments basedo on wup environments")
    r.map("cluster", cluster, "Simulate a cluster using docker containers")
    
    r.run(handleError=True)

if __name__ == "__main__":
    wup(sys.argv[1:])
    
