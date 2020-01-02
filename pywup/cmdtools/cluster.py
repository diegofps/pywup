from multiprocessing import Pool, cpu_count

from pywup.services.general import parse_image_name, parse_env, get_image_name, get_container_name, get_open_cmd
from pywup.services.system import abort, error, WupError, Args, run, Route

import shlex
import tqdm
import sys
import os
import re


class CreateTask:
    def __init__(self, cont_name, volumes, base):
        self.cont_name = cont_name
        self.volumes = volumes
        self.base = base


def get_container_by_cluster_and_node_number(clustername, node_number):
    status, rows = run("docker ps -a -f \"name=wcl__" + clustername + "__*\"", read=True)

    r = re.compile("wcl__" + clustername + "__([a-zA-Z0-9]+)__([a-zA-Z0-9]+)__([0-9]+)\n$")
    
    for row in rows:
        result = r.search(row)
        if result:
            project, tag, number = result.groups()
            if number == node_number:
                idd = row.split(" ", 1)[0]
                return idd, project, tag
    
    return None


def get_containers_in_cluster(clustername, abortOnFail=False):
    status, rows = run("docker ps -a -f \"name=wcl__" + clustername + "__*\" -q", read=True)
    
    if abortOnFail and not rows:
        abort("Cluster not found")

    return [x.strip() for x in rows]


def parallel_do_new(task):
    run("docker rm %s 2> /dev/null" % task.cont_name)
    run("docker run -i --name {} {} {}".format(task.cont_name, task.volumes, task.base), ["exit\n"])


def do_new(args):
    clustername = args.pop_parameter()
    image = args.pop_parameter()
    qtt = int(args.pop_parameter())
    outfile = args.pop_parameter() if args.has_parameter() else None

    project, tag = parse_image_name(image)
    variables, templates = parse_env(tag, "cluster create")

    volumes = "-v " + " -v ".join(templates["VOLUMES"]) if "VOLUMES" in templates else ""
    base = get_image_name(project, tag)

    containers = get_containers_in_cluster(clustername)
    if containers:
        error("A cluster with this name already exists, remove it first")

    # Build the tasks
    tasks = []
    for i in range(qtt):
        cont_name = get_container_name(project, tag, clustername, i, qtt)
        tasks.append(CreateTask(cont_name, volumes, base))

    # Run in parallel
    print("Creating cluster...")
    jobs = cpu_count()
    with Pool(jobs) as p:
        for _ in tqdm.tqdm(p.imap(parallel_do_new, tasks), total=len(tasks)):
            pass
    
    if outfile:
        with open(outfile, "w") as fout:
            pass


def do_rm(args):
    clustername = args.pop_parameter()
    ids = " ".join(get_containers_in_cluster(clustername, abortOnFail=True))

    run("docker stop " + ids)
    run("docker rm " + ids)


def do_start(args):
    clustername = args.pop_parameter()
    ids = " ".join(get_containers_in_cluster(clustername, abortOnFail=True))

    run("docker start " + ids)


def do_stop(args):
    clustername = args.pop_parameter()
    ids = " ".join(get_containers_in_cluster(clustername, abortOnFail=True))

    run("docker stop " + ids)


def do_open(args):
    clustername = args.pop_parameter()
    node_number = args.pop_parameter()

    idd, project, tag = get_container_by_cluster_and_node_number(clustername, node_number)
    variables, templates = parse_env(tag, "cluster open")

    cmd = get_open_cmd(idd, templates["OPEN"])

    run("docker start " + idd)
    run(cmd, suppressInterruption=True)
    #run("docker stop " + idd)


def do_ls(args):
    if args.has_parameter():
        cluster = args.pop_parameter()
        run("docker ps -a -f \"name=wcl__{}__*\"".format(cluster))

    else:
        status, rows = run("docker ps -a -f \"name=wcl__*\"", read=True)
        r = re.compile(r'wcl__([a-zA-Z0-9]+)__([a-zA-Z0-9]+)__([a-zA-Z0-9]+)__([0-9]+)')
        s = [r.search(row) for row in rows]
        res = {}

        for m in s:
            if m:
                cluster = m.group(1)
                project = m.group(2)
                tag = m.group(3)
                number = m.group(4)

                if not cluster in res:
                    res[cluster] = [1, project + ":" + tag]
                else:
                    res[cluster][0] += 1
        
        for cluster in res:
            print("{} [{}, {}]".format(cluster, *res[cluster]))


def main(args):
    r = Route(args)

    r.map("new", do_new, "Creates a new simulated cluster using an existing image")
    r.map("rm", do_rm, "Removes an existing simulated cluster")
    r.map("start", do_start, "Starts all containers for a given cluster")
    r.map("stop", do_stop, "Stops all containers for a given cluster")
    r.map("open", do_open, "Opens one of the cluster machines")
    r.map("ls", do_ls, "Lists all clusters or containers in cluster")
    
    r.run()
