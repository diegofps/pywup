from pywup.services.general import parse_env, get_image_name, get_container_name, get_open_cmd, parse_image_name, update_state, get_export_filepath
from pywup.services.system import error, abort, WupError, run, Args
from pywup.services import conf

import sys
import os


def do_build(args):
    projectname = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")

    variables, templates = parse_env(tag, "build")
    cont_name = get_container_name(projectname, tag)
    
    volumes = "-v " + " -v ".join(templates["VOLUMES"]) if "VOLUMES" in templates else ""
    base = variables["BASE"]
    init = templates["BUILD"]

    run("docker rm %s 2> /dev/null" % cont_name)
    run("docker run -i --name {} {} {}".format(cont_name, volumes, base), write=init)


def do_open(args):
    projectname = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")

    cont_name = get_container_name(projectname, tag)
    variables, templates = parse_env(tag, "open")

    print("Starting container...")
    run("docker start " + cont_name)

    print("Connecting to terminal...")
    run(get_open_cmd(cont_name, templates["OPEN"], True))


def do_commit(args):
    project = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")

    container_name = get_container_name(project, tag)
    img_name = get_image_name(project, tag)

    print("Removing any existing image with this name")
    run("docker rmi {} 2> /dev/null".format(img_name))

    print("Creating the new image")
    run("docker commit {} {}".format(container_name, img_name))


def do_launch(args):
    projectname = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")

    variables, templates = parse_env(tag, "launch")
    cont_name = get_container_name(projectname, tag)
    run = templates["LAUNCH"] + ["\nexit\n"]

    print("Starting container...")
    run("docker start " + cont_name)

    print("Connecting to terminal...")
    run(get_open_cmd(cont_name, run))


def do_exec(args):
    projectname = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")

    cmd = args.pop_parameter()
    cont_name = get_container_name(projectname, tag)
    variables, templates = parse_env(tag, "exec")

    run = templates["EXEC"] + [cmd, "\nexit\n"]

    print("Starting container...")
    run("docker start " + cont_name)

    print("Connecting to terminal...")
    run(get_open_cmd(cont_name, run))


def do_export(args):
    project = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")

    img_name = get_image_name(project, tag)
    filepath = get_export_filepath(project, tag)

    print("Exporting image commit for", img_name, "as", filepath)
    run("docker save {} | gzip > {}".format(img_name, filepath))


def do_import(args):
    filepath = args.pop_parameter()

    print("Importing image...")
    run(["zcat {}".format(filepath), "docker load -q"])
    #project, tag = parse_image_name(rows[0].split("__")[1].strip())


def do_new(args):
    project = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")

    variables, templates = parse_env(tag, "new")
    img_name = get_image_name(project, tag)
    cont_name = get_container_name(project, tag)
    volumes = "-v " + " -v ".join(templates["VOLUMES"]) if "VOLUMES" in templates else ""
    init = templates["NEW"]
    
    print("Removing previous container...")
    run("docker rm %s 2> /dev/null" % cont_name)

    print("Creating container from image...")
    run("docker run -i --name {} {} {}".format(cont_name, volumes, img_name), write=init)


def do_rm(args):
    projectname = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")
    cont_name = get_container_name(projectname, tag)

    run("docker stop " + cont_name)
    run("docker rm " + cont_name)

def do_rmi(args):
    projectname = conf.get("wup:project", scope="global")
    tag = conf.get("wup:tag", scope="global")
    img_name = get_image_name(projectname, tag)

    run("docker rmi " + img_name)


def do_ls(args):
    run("docker ps -a -f \"name=wup__*\"")


def do_lsi(args):
    run("docker image ls \"wup__*\"")


def do_set(args):
    if args.has_parameter():
        project, tag = parse_image_name(args.pop_parameter())
    else:
        project, tag = "", ""

    conf.set("wup:project", project, scope="global")
    conf.set("wup:tag", tag, scope="global")
    update_state()


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
        
        elif cmd == "launch":
            do_launch(args)

        elif cmd == "exec":
            do_exec(args)

        elif cmd == "export":
            do_export(args)

        elif cmd == "import":
            do_import(args)

        elif cmd == "rm":
            do_rm(args)

        elif cmd == "rmi":
            do_rmi(args)

        elif cmd == "ls":
            do_ls(args)

        elif cmd == "lsi":
            do_lsi(args)

        elif cmd == "new":
            do_new(args)

        elif cmd == "set":
            do_set(args)

        else:
            abort("Invalid option:", cmd)

    except WupError as e:
        abort(e.message)
