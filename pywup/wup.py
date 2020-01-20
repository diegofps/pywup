#!/usr/bin/env python3

from pywup.services.general import lookup_env, lookup_cluster, update_state
from pywup.services.system import abort, error, WupError, Route, Params
from pywup.services.context import Context
from pywup.services import conf

from pywup import cmdtools

import sys
import os


def use(cmd, args):
    params = Params(cmd, args)
    params.map("env", 1, None, "Name or path of environment file")
    params.map("cluster", 1, None, "Name or path of cluster file")
    params.map("--env", 1, None, "Name or path of environment file")
    params.map("--cluster", 1, None, "Name or path of cluster file")
    
    if params.run():
        env = params.get("--env") if params.get("--env") else params.get("env")
        cluster = params.get("--cluster") if params.get("--cluster") else params.get("cluster")
        Context().use(env, cluster)

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

def config(cmd, args):
    from pywup.cmdtools.conf import main
    main(cmd, args)

def env(cmd, args):
    from pywup.cmdtools.env import main
    main(cmd, args)

def renv(cmd, args):
    from pywup.cmdtools.renv import main
    main(cmd, args)

def cluster(cmd, args):
    from pywup.cmdtools.cluster import main
    main(cmd, args)


def wup(*params):
    r = Route(sys.argv[1:], "wup")

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
    wup()
    
