from pywup.services.system import error, Params, Route, print_table
from pywup.services.cluster import Cluster

import os


def template(cmd, args):
    p = Params(cmd, args)
    p.map("clustername", 1, None, "Name of the new cluster", mandatory=True)
    p.map("outputfolder", 1, ".", "Output folder to save the cluster file descriptor")

    if p.run():
        Cluster().template(p.clustername, p.outputfolder)


def ls(cmd, args):
    p = Params(cmd, args)

    if p.run():
        result = Cluster().ls()
        print_table(result)


def open(cmd, args):
    p = Params(cmd, args)
    p.map("clustername", 1, None, "Name of the new cluster to open", mandatory=True)

    if p.run():
        Cluster().open(p.clustername)


def exec(cmd, args):
    p = Params(cmd, args, limit_parameters=False)
    p.map("command", 1, None, "Command to be executed", mandatory=True)

    if p.run():
        Cluster().exec(p._input_parameters)


def send(cmd, args):
    p = Params(cmd, args)
    p.map("src", 1, None, "Source path to the file inside the host", mandatory=True)
    p.map("dst", 1, None, "Destination path inside the remote machines", mandatory=True)

    if p.run():
        Cluster().send(p.src, p.dst)


def get(cmd, args):
    p = Params(cmd, args)
    p.map("src", 1, None, "Source path to the files inside the remote machines", mandatory=True)
    p.map("dst", 1, None, "Destination path to a folder in the host", mandatory=True)

    if p.run():
        Cluster().get(p.src, p.dst)


def doctor(cmd, args):
    p = Params(cmd, args)

    if p.run():
        Cluster().doctor()


def main(cmd, args):
    r = Route(args, cmd)

    r.map("template", template, "Create an empty cluster file that you can modify to represent a real cluster")
    r.map("ls", ls, "Summarizes all machines in this cluster")
    r.map("open", open, "Opens a remote machine using ssh")
    r.map("exec", exec, "Execute a command in all remote machines")
    r.map("send", send, "Sends a file or directory to all remote machines")
    r.map("get", get, "Retrieve a file or directory from the remote machines")
    r.map("doctor", doctor, "Fixes common SSH validations")
    
    r.run()
