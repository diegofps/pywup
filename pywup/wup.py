#!/usr/bin/env python3

from pywup.services.system import abort, error, WupError, Route, Params
from pywup.consts import version as wup_version
from pywup.services.context import Context

from pywup import cmdtools

import sys
import os


def use(cmd, args):
    from pywup.cmdtools.use import main
    main(cmd, args)

def collect(cmd, args):
    from pywup.cmdtools.collect import main
    main(cmd, args)

def heatmap(cmd, args):
    from pywup.cmdtools.heatmap import main
    main(cmd, args)

def bars(cmd, args):
    from pywup.cmdtools.bars import main
    main(cmd, args)

def backup(cmd, args):
    from pywup.cmdtools.backup import main
    main(cmd, args)

def q(cmd, args):
    from pywup.cmdtools.q import main
    main(cmd, args)

def env(cmd, args):
    from pywup.cmdtools.env import main
    main(cmd, args)

def menv(cmd, args):
    from pywup.cmdtools.menv import main
    main(cmd, args)

def cluster(cmd, args):
    from pywup.cmdtools.cluster import main
    main(cmd, args)

def virtual(cmd, args):
    from pywup.cmdtools.virtual import main
    main(cmd, args)

def about(cmd, args):
    print(wup_version)

def wup(*params):
    r = Route(sys.argv[1:], "wup")

    r.map("use", use, "Set current env, cluster or architecture files")
    r.map("collect", collect, "Run an app multiple times, variating its parameters and collecting its output attributes")
    r.map("heatmap", heatmap, "Plot a heatmap image using the data collected (requires matplotlib)")
    r.map("bars", bars, "Plot bars image using the data collected (requires matplotlib)")
    r.map("backup", backup, "Backup system files into a folder synced to a cloud")
    r.map("q", q, "Run SQL in CSV files (Requires python-q-text-as-data)")
    r.map("env", env, "Manage docker environments for development and cluster deploy (wup style)")
    r.map("menv", menv, "Simulate a cluster on your local machine using docker containers and wup environments")
    r.map("cluster", cluster, "Interact with the current cluster")
    r.map("virtual", virtual, "Manage wup environments as a virtual cluster deployed on top of a real cluster")
    r.map("about", about, "Display wup info")
    
    r.run(handleError=True)


if __name__ == "__main__":
    wup()
