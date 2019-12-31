from .shared import Args, error, abort, WupError, parse_templates, system_run, parse_image_name, get_image_name, get_container_name, get_export_filepath, parse_env, get_open_cmd

import sys
import os


def do_build(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    variables, templates = parse_env(tag, "build")
    
    volumes = "-v " + " -v ".join(templates["VOLUMES"]) if "VOLUMES" in templates else ""

    base = variables["BASE"]
    init = templates["INIT"]

    cont_name = get_container_name(projectname, tag)

    system_run("docker rm %s 2> /dev/null" % cont_name)
    system_run("docker run -i --name {} {} {}".format(cont_name, volumes, base), write=init)


def do_open(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    cont_name = get_container_name(projectname, tag)
    variables, templates = parse_env(tag, "open")

    print("Starting container...")
    system_run("docker start " + cont_name)

    print("Connecting to terminal...")
    system_run(get_open_cmd(templates, cont_name, templates["OPEN"], True))


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
    variables, templates = parse_env(tag, "launch")
    cont_name = get_container_name(projectname, tag)

    run = templates["LAUNCH"] + ["\nexit\n"]

    print("Starting container...")
    system_run("docker start " + cont_name)

    print("Connecting to terminal...")
    cmd = get_open_cmd(templates, cont_name, run)
    system_run(cmd)


def do_exec(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    cmd = args.pop_parameter()
    cont_name = get_container_name(projectname, tag)
    variables, templates = parse_env(tag, "exec")

    run = templates["EXEC"] + [cmd, "\nexit\n"]

    print("Starting container...")
    system_run("docker start " + cont_name)

    print("Connecting to terminal...")
    cmd = get_open_cmd(templates, cont_name, run)
    system_run(cmd)


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
