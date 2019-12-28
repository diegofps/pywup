from .shared import Args, error, abort, WupError
from subprocess import Popen, PIPE
from . import conf

import shlex
import sys
import os


def _export_filepath(project, tag):
    return "wup_{}__{}.gz".format(project, tag)


def _container_name(projectname, tag):
    return "wup_{}_{}".format(projectname, tag)


def _image_name(projectname, tag):
    return "wup_{}:{}".format(projectname, tag)


def _parse_cmds(args):
    name = args.pop_parameter()
    tmp = name.split(":")

    if "__" in name:
        error("Names must not contain two consecutive underscores (__)")

    if len(tmp) == 1:
        projectname, tag = conf.get(Args(["project.name"])), tmp[0]
    
    elif len(tmp) == 2:
        projectname, tag = tmp
    
    else:
        error("Too many \":\" in", name)
    
    return projectname, tag


def parse_env(tag):
    filepath = "./{}.env".format(tag)
    base = "ubuntu:bionic"
    deploy = []
    volumes = []
    order = []
    rows = []
    init = []
    run = []

    if not os.path.exists(filepath):
        return base, volumes, init, deploy

    with open(filepath, "r") as fin:
        for i, line in enumerate(fin):
            if line.startswith("@") and line.endswith("@\n"):
                order.append((line[1:-2], i))
            rows.append(line)
        order.append(("eof", i+1))
    
    for i in range(1, len(order)):
        name, first = order[i-1]
        _, last = order[i]
        selection = rows[first+1:last]

        if name == "BASE":
            base = "".join(selection).strip()

        elif name == "VOLUMES":
            volumes = [j.strip() for j in selection]
            volumes = [j for j in volumes if j]
            volumes = [os.path.expanduser(j) for j in volumes]
            volumes = [os.path.abspath(j) for j in volumes]

            for v in volumes:
                src = v.split(":")[0]

                if not os.path.exists(src):
                    error("Missing source directory in host:", src)
                
                if not os.path.isdir(src):
                    error("Source volume in host is not a directory:", src)
        
        elif name == "INIT":
            init = selection
           
        elif name == "DEPLOY":
            deploy = selection
        
        elif name == "RUN":
            run = selection

        else:
            error("Illegal env tag:", name)
    
    return base, volumes, init, deploy, run


def do_build(args):
    projectname, tag = _parse_cmds(args)
    base, volumes, init, deploy, run = parse_env(tag)
    cont_name = _container_name(projectname, tag)

    if volumes:
        volumes = "-v " + " -v ".join(volumes)
    else:
        volumes = ""

    if init:
        dockercmd = "docker run -i --name {} {} {}".format(cont_name, volumes, base)
    else:
        dockercmd = "docker run --name {} {} {}".format(cont_name, volumes, base)
    
    dockerclean = "docker rm %s 2> /dev/null" % cont_name

    os.system(dockerclean)

    if init:
        args = shlex.split(dockercmd)
        p = Popen(args, stdout=PIPE, stdin=PIPE)

        for line in init:
            p.stdin.write(line.encode())
        p.stdin.close()

        for line in p.stdout:
            sys.stdout.write(line.decode("utf-8"))

    else:
        os.system(dockercmd)


def do_open(args):
    projectname, tag = _parse_cmds(args)
    cont_name = _container_name(projectname, tag)

    print("Starting container...")
    os.system("docker start " + cont_name)

    print("Connecting to terminal...")
    os.system("docker exec -it {} bash".format(cont_name))

    print("Stopping container, this may take a few seconds...")
    os.system("docker stop {}".format(cont_name))

    print("Done!")


def do_commit(args):
    project, tag = _parse_cmds(args)
    container_name = _container_name(project, tag)
    img_name = _image_name(project, tag)

    print("Removing any existing image with this name")
    os.system("docker rmi {} 2> /dev/null".format(img_name))

    print("Creating the new image")
    os.system("docker commit {} {}".format(container_name, img_name))

    print("Done!")


def do_run(args):
    projectname, tag = _parse_cmds(args)
    base, volumes, init, deploy, run = parse_env(tag)
    cont_name = _container_name(projectname, tag)

    if not run:
        error("This env does not support run")

    print("Starting container...")
    os.system("docker start " + cont_name)

    print("Connecting to terminal...")
    args = shlex.split("docker exec -i {} bash".format(cont_name))
    p = Popen(args, stdin=PIPE)

    for line in run:
        p.stdin.write(line.encode())
    p.stdin.close()
    p.wait()

    print("Stopping container, this may take a few seconds...")
    os.system("docker stop {}".format(cont_name))

    print("Done!")


def do_export(args):
    project, tag = _parse_cmds(args)
    img_name = _image_name(project, tag)
    filepath = _export_filepath(project, tag)

    print("Exporting image commit for", img_name)
    os.system("docker save {} | gzip > {}".format(img_name, filepath))


def do_import(args):
    filepath = args.pop_parameter()
    os.system("zcat {} | docker load".format(filepath))


def main(argv):
    try:
        args = Args(argv)

        cmd = args.pop_parameter()

        if cmd == "build":
            do_build(args)
        
        elif cmd == "open":
            do_open(args)
        
        elif cmd == "commit":
            do_commit(args)
        
        elif cmd == "run":
            do_run(args)

        elif cmd == "export":
            do_export(args)

        elif cmd == "import":
            do_import(args)

        else:
            abort("Invalid option:", cmd)

    except WupError as e:
        abort(e.message)
