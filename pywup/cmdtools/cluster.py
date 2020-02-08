from pywup.services.system import error, Params, Route, print_table, colors
from pywup.services.cluster import Cluster

import sys
import os


def use(cmd, args):

    p = Params(cmd, args)
    p.map("name", 1, None, "Name or path of the clusterfile to use")
    p.map("--a", -1, [], "Filter cluster machines by one or more architecture")
    p.map("--n", -1, [], "Filter cluster machines by one or more machine name")
    p.map("--t", -1, [], "Filter cluster machines by one or more tag name")
    p.map("--p", -1, [], "Filter cluster machines by one or more pair KEY=VALUE")

    if p.run():
        Cluster().use(p.name, p.flatten__a, p.flatten__n, p.flatten__t, p.flatten__p)


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
    p.map("--m", 1, None, "Execute command on a single machine")

    if p.run():
        if p.__m:
            Cluster().exec_single(p.command, p.__m)
        else:
            Cluster().exec_all(p.command)


def send(cmd, args):

    p = Params(cmd, args)
    p.map("src", 1, None, "Source path to the file inside the host", mandatory=True)
    p.map("dst", 1, None, "Destination path inside the remote machines")
    p.map("--m", 1, None, "Sends the file to a single machine")

    if p.run():
        if p.__m:
            Cluster().send_single(p.__m, p.src, p.dst)
        else:
            Cluster().send_all(p.src, p.dst)


def get(cmd, args):

    p = Params(cmd, args)
    p.map("src", 1, None, "Path to the source files inside the remote machines", mandatory=True)
    p.map("dst", 1, None, "Destination folder inside the host to store the received files, each machine will have its own folder")
    p.map("--m", 1, None, "Gets the file from a single machine")

    if p.run():
        if p.__m:
            Cluster().get_single(p.__m, p.src, p.dst)
        else:
            Cluster().get_all(p.src, p.dst)


def doctor(cmd, args):

    p = Params(cmd, args)

    if p.run():
        Cluster().doctor()


def pbash(cmd, args):

    p = Params(cmd, args)
    p.map("--v", 0, None, "Prints sdtout from the first machine. Usefull when issuing interactive commands")

    if p.run():
        Cluster().pbash(p.__v)


def main(cmd, args):

    r = Route(args, cmd)

    r.map("use", use, "Specify which clusterfile to use and which filters to apply")
    r.map("template", template, "Create an empty cluster file that you can modify to represent a real cluster")
    r.map("ls", ls, "Summarizes all machines in this cluster")
    r.map("open", open, "Opens a remote machine using ssh")
    r.map("exec", exec, "Execute a command in all remote machines")
    r.map("send", send, "Sends a file or directory to all remote machines")
    r.map("get", get, "Retrieve a file or directory from the remote machines")
    r.map("doctor", doctor, "Fixes common SSH validations")
    r.map("pbash", pbash, "A really basic parallel bash")
    
    r.run()
