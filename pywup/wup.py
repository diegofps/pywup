#!/usr/bin/env python3

from pywup.services.system import abort, error, WupError, Route
from pywup import cmdtools

import sys
import os


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

def conf(args):
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

    r.map("collect", collect, "Run an app multiple times, variating its parameters and collecting its output attributes")
    r.map("heatmap", heatmap, "Plot a heatmap image using the data collected")
    r.map("bars", bars, "Plot a bars image using the data collected")
    r.map("backup", backup, "Backup system files into a folder synced to a cloud")
    r.map("q", q, "Run SQL in CSV files (Requires python-q)")
    r.map("c", conf, "Set/Get wup configuration parameters")
    r.map("e", env, "Manage docker environments for development and cluster deploy (wup style)")
    r.map("r", renv, "Manager remote environments basedo on wup environments")
    r.map("cluster", cluster, "Simulate a cluster using docker containers")
    
    r.run(handleError=True)

if __name__ == "__main__":
    wup(sys.argv[1:])
    
