#!/usr/bin/env python3

from pywup.services.general import lookup_env, lookup_cluster, update_state
from pywup.services.system import abort, error, WupError, Route, Params
from pywup.consts import version as wup_version
from pywup.services.context import Context
from pywup.services import conf

from pywup import cmdtools

import sys
import os


def use(cmd, args):
    desc1 = "Name or path of environment file"
    desc2 = "Name or path of cluster file"
    desc3 = "Handle only machines with this remote architecture"

    params = Params(cmd, args)
    params.map("env", 1, None, desc1)
    params.map("cluster", 1, None, desc2)
    params.map("arch", 1, None, desc3)

    params.map("--env", 1, None, desc1)
    params.map("--cluster", 1, None, desc2)
    params.map("--arch", 1, None, desc3)
    
    if params.run():
        env = params.__env if params.has("--env") else params.env
        cluster = params.__cluster if params.has("--cluster") else params.cluster
        arch = params.__arch if params.has("--arch") else params.arch
        Context().use(env, cluster, arch)

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

def remote(cmd, args):
    from pywup.cmdtools.remote import main
    main(cmd, args)

def cluster(cmd, args):
    from pywup.cmdtools.cluster import main
    main(cmd, args)

def version(cmd, args):
    print(wup_version)

def wup(*params):
    r = Route(sys.argv[1:], "wup")

    r.map("use", use, "Set env and/or cluster files")
    r.map("collect", collect, "Run an app multiple times, variating its parameters and collecting its output attributes")
    r.map("heatmap", heatmap, "Plot a heatmap image using the data collected (requires matplotlib)")
    r.map("bars", bars, "Plot bars image using the data collected (requires matplotlib)")
    r.map("backup", backup, "Backup system files into a folder synced to a cloud")
    r.map("q", q, "Run SQL in CSV files (Requires python-q-text-as-data)")
    r.map("conf", config, "Set/Get wup configuration parameters")
    r.map("env", env, "Manage docker environments for development and cluster deploy (wup style)")
    r.map("remote", remote, "Manager remote environments basedo on wup environments")
    r.map("cluster", cluster, "Simulate a cluster using docker containers")
    r.map("version", version, "Show current wup version")
    
    r.run(handleError=True)

if __name__ == "__main__":
    wup()
    
