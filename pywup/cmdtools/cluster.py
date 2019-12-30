from .shared import Args, error, abort, WupError, parse_templates, system_run, parse_image_name, get_image_name, parse_env, get_container_name
from multiprocessing import Pool, cpu_count

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
    status, rows = system_run("docker ps -a -f \"name=wcl__" + clustername + "__*\"", read=True)

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
    status, rows = system_run("docker ps -a -f \"name=wcl__" + clustername + "__*\" -q", read=True)
    
    if abortOnFail and not rows:
        abort("Cluster not found")

    return [x.strip() for x in rows]


def parallel_do_create(task):
    system_run("docker rm %s 2> /dev/null" % task.cont_name)
    system_run("docker run -i --name {} {} {}".format(task.cont_name, task.volumes, task.base), ["exit\n"])


def do_create(args):
    clustername = args.pop_parameter()
    image = args.pop_parameter()
    qtt = int(args.pop_parameter())
    outfile = args.pop_parameter() if args.has_parameter() else None

    project, tag = parse_image_name(image)
    variables, templates = parse_env(tag)

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
        for _ in tqdm.tqdm(p.imap(parallel_do_create, tasks), total=len(tasks)):
            pass
    
    if outfile:
        with open(outfile, "w") as fout:
            pass


def do_rm(args):
    clustername = args.pop_parameter()
    ids = " ".join(get_containers_in_cluster(clustername, abortOnFail=True))

    system_run("docker stop " + ids)
    system_run("docker rm " + ids)


def do_start(args):
    clustername = args.pop_parameter()
    ids = " ".join(get_containers_in_cluster(clustername, abortOnFail=True))

    system_run("docker start " + ids)


def do_stop(args):
    clustername = args.pop_parameter()
    ids = " ".join(get_containers_in_cluster(clustername, abortOnFail=True))

    system_run("docker stop " + ids)


def quote(str):
    return '"' + re.sub(r'([\'\"\\])', r'\\\1', str) + '"'


def get_open_cmd(templates, tag, idd):
    o = "\n".join(["source \"$HOME/.bashrc\""] + templates[tag])
    k = quote(o)
    b = quote("bash --init-file <(echo " + k + ")")
    c = "docker exec -it " + idd + " bash -c " + b.replace("$", "\$")
    return c


def do_open(args):
    clustername = args.pop_parameter()
    node_number = args.pop_parameter()

    idd, project, tag = get_container_by_cluster_and_node_number(clustername, node_number)
    variables, templates = parse_env(tag)

    cmd = get_open_cmd(templates, "OPEN", idd)

    system_run("docker start " + idd)
    system_run(cmd, suppressInterruption=True)
    #system_run("docker stop " + idd)

def do_deploy(args):
    error("Not implemented yet")


def main(argv):
    try:
        args = Args(argv)

        cmd = args.pop_parameter()

        if cmd == "create":
            do_create(args)
        
        elif cmd == "rm":
            do_rm(args)
        
        elif cmd == "start":
            do_start(args)
        
        elif cmd == "stop":
            do_stop(args)
        
        elif cmd == "open":
            do_open(args)
        
        elif cmd == "deploy":
            do_deploy(args)

        else:
            abort("Invalid parameter:", cmd)

    except WupError as e:
        abort(e.message)