from .shared import Args, error, abort, WupError, parse_templates, system_run, parse_image_name, get_image_name, get_container_name, get_export_filepath, parse_env

import sys
import os


def do_build(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    variables, templates = parse_env(tag)
    
    volumes = "-v " + " -v ".join(templates["VOLUMES"]) if "VOLUMES" in templates else ""

    base = variables["BASE"]
    init = templates["INIT"]

    cont_name = get_container_name(projectname, tag)

    system_run("docker rm %s 2> /dev/null" % cont_name)
    system_run("docker run -i --name {} {} {}".format(cont_name, volumes, base), write=init)


def do_open(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    cont_name = get_container_name(projectname, tag)

    print("Starting container...")
    system_run("docker start " + cont_name)

    print("Connecting to terminal...")
    system_run("docker exec -it {} bash".format(cont_name))

    print("Stopping container, this may take a few seconds...")
    system_run("docker stop {}".format(cont_name))

    print("Done!")


def do_commit(args):
    project, tag = parse_image_name(args.pop_parameter())
    container_name = get_container_name(project, tag)
    img_name = get_image_name(project, tag)

    print("Removing any existing image with this name")
    system_run("docker rmi {} 2> /dev/null".format(img_name))

    print("Creating the new image")
    system_run("docker commit {} {}".format(container_name, img_name))

    print("Done!")


def do_launch(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    variables, templates = parse_env(tag)
    cont_name = get_container_name(projectname, tag)

    run = templates["LAUNCH"]

    if not run:
        error("This env does not support run")

    print("Starting container...")
    system_run("docker start " + cont_name)

    print("Connecting to terminal...")
    system_run("docker exec -i {} bash".format(cont_name), run)

    print("Stopping container, this may take a few seconds...")
    system_run("docker stop {}".format(cont_name))

    print("Done!")


def do_exec(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    cmd = args.pop_parameter()
    cont_name = get_container_name(projectname, tag)

    run = [cmd]

    if not run:
        error("This env does not support run")

    print("Starting container...")
    system_run("docker start " + cont_name)

    print("Connecting to terminal...")
    system_run("docker exec -i {} bash".format(cont_name), run)

    print("Stopping container, this may take a few seconds...")
    system_run("docker stop {}".format(cont_name))

    print("Done!")


def do_export(args):
    project, tag = parse_image_name(args.pop_parameter())
    img_name = get_image_name(project, tag)
    filepath = get_export_filepath(project, tag)

    print("Exporting image commit for", img_name)
    system_run("docker save {} | gzip > {}".format(img_name, filepath))


def do_import(args):
    filepath = args.pop_parameter()
    system_run("zcat {} | docker load".format(filepath))


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

        else:
            abort("Invalid option:", cmd)

    except WupError as e:
        abort(e.message)
