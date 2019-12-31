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
    system_run(get_open_cmd(cont_name, templates["OPEN"], True))


def do_commit(args):
    project, tag = parse_image_name(args.pop_parameter())
    container_name = get_container_name(project, tag)
    img_name = get_image_name(project, tag)

    print("Removing any existing image with this name")
    system_run("docker rmi {} 2> /dev/null".format(img_name))

    print("Creating the new image")
    system_run("docker commit {} {}".format(container_name, img_name))


def do_launch(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    variables, templates = parse_env(tag, "launch")
    cont_name = get_container_name(projectname, tag)

    run = templates["LAUNCH"] + ["\nexit\n"]

    print("Starting container...")
    system_run("docker start " + cont_name)

    print("Connecting to terminal...")
    cmd = get_open_cmd(cont_name, run)
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
    cmd = get_open_cmd(cont_name, run)
    system_run(cmd)


def do_export(args):
    project, tag = parse_image_name(args.pop_parameter())
    img_name = get_image_name(project, tag)
    filepath = get_export_filepath(project, tag)

    print("Exporting image commit for", img_name, "as", filepath)
    system_run("docker save {} | gzip > {}".format(img_name, filepath))


def do_import(args):
    #import pdb; pdb.set_trace()
    filepath = args.pop_parameter()

    print("Importing image...")
    status, rows = system_run(["zcat {}".format(filepath), "docker load -q"], read=True)

    project, tag = parse_image_name(rows[0].split("__")[1].strip())
    variables, templates = parse_env(tag, "import")
    img_name = get_image_name(project, tag)

    volumes = "-v " + " -v ".join(templates["VOLUMES"]) if "VOLUMES" in templates else ""
    
    init = templates["IMPORT"]

    cont_name = get_container_name(project, tag)

    print("Removing previous container...")
    system_run("docker rm %s 2> /dev/null" % cont_name)

    print("Creating container from imported image...")
    #import pdb; pdb.set_trace()
    system_run("docker run -i --name {} {} {}".format(cont_name, volumes, img_name), write=init)
    #print(rows)


def do_rm(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    cont_name = get_container_name(projectname, tag)

    system_run("docker stop " + cont_name)
    system_run("docker rm " + cont_name)

def do_rmi(args):
    projectname, tag = parse_image_name(args.pop_parameter())
    img_name = get_image_name(projectname, tag)

    system_run("docker rmi " + img_name)


def do_ls(args):
    system_run("docker ps -a -f \"name=wup__*\"")


def do_lsi(args):
    system_run("docker image ls \"wup__*\"")


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

        else:
            abort("Invalid option:", cmd)

    except WupError as e:
        abort(e.message)
