#!/usr/bin/env python3

from pywup.services.system import abort, error, WupError, Route
from pywup import cmdtools

import sys
import os


def wup():
    r = Route(sys.argv[1:])

    r.map("collect", lambda x: cmdtools.collect.main(x), "Run an app multiple times, variating its parameters and collecting its output attributes")
    r.map("heatmap", lambda x: cmdtools.heatmap.main(x), "Plot a heatmap image using the data collected")
    r.map("bars", lambda x: cmdtools.bars.main(x), "Plot a bars image using the data collected")
    r.map("backup", lambda x: cmdtools.backup.main(x), "Backup system files into a folder synced to a cloud")
    r.map("q", lambda x: cmdtools.q.main(x), "Run SQL in CSV files (Requires python-q)")
    r.map("conf", lambda x: cmdtools.conf.main(x), "Set/Get wup configuration parameters")
    r.map("env", lambda x: cmdtools.env.main(x), "Manage docker environments for development and cluster deploy (wup style)")
    r.map("renv", lambda x: cmdtools.renv.main(x), "Manager remote environments basedo on wup environments")
    r.map("cluster", lambda x: cmdtools.cluster.main(x), "Simulate a cluster using docker containers")
    
    r.run(handleError=True)

if __name__ == "__main__":
    wup()
