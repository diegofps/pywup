from pywup.services.general import parse_env, get_image_name, get_container_name, get_open_cmd, parse_image_name, update_state, get_export_filepath
from pywup.services.system import error, abort, WupError, run, Args, Route, quote
from pywup.services import conf

import sys
import os


def do_set(args):
    if args.has_parameter():
        name, filepath = parse_image_name(args.pop_parameter())
    else:
        name, filepath = "", ""
    
    conf.set("wup.env_name", name, scope="global")
    conf.set("wup.env_filepath", filepath, scope="global")
    update_state()


def do_build(args):
    name = conf.get("wup.env_name", scope="global")
    filepath = conf.get("wup.env_filepath", scope="global")

    variables, templates, bashrc = parse_env(filepath, "build")
    cont_name = get_container_name(name)
    
    volumes = " -v " + " -v ".join(templates["VOLUMES"]) if templates["VOLUMES"] else None
    expose = " --expose=" + " --expose=".join(variables["EXPOSE"].split(",")) if variables["EXPOSE"] else None
    mapPorts = " -p " + " -p".join(variables["MAP_PORTS"].split(",")) if variables["MAP_PORTS"] else None
    create_start = ["echo " + quote("".join(templates["START"] + ["bash\n", "exit\n"])) + " > /start.sh\n", "chmod +x /start.sh\n"]

    cmds = bashrc + create_start + templates["BUILD"]
    base = variables["BASE"]

    rmCmd = "docker rm %s 2> /dev/null" % cont_name
    print(rmCmd)
    run(rmCmd)

    createCmd = "docker run -i --entrypoint /bin/bash --name " + cont_name

    if volumes:
        createCmd += volumes
    
    if expose:
        createCmd += expose
        
    if mapPorts:
        createCmd += mapPorts
    
    #a = quote("nohup /start.sh & bash ; exit")
    b = quote("bash --init-file <(cat /start.sh 2> /dev/null || echo \"bash ; exit\")")
    createCmd += " " + base + " -c " + b
    
    print(createCmd)
    run(createCmd, write=cmds)


def do_open(args):
    name = conf.get("wup.env_name", scope="global")
    filepath = conf.get("wup.env_filepath", scope="global")

    variables, templates, bashrc = parse_env(filepath)
    cont_name = get_container_name(name)
    cmds = bashrc + templates["OPEN"]

    print("Starting container...")
    run("docker start " + cont_name)

    print("Connecting to terminal...")
    run(get_open_cmd(cont_name, cmds, True))


def do_commit(args):
    name = conf.get("wup.env_name", scope="global")

    container_name = get_container_name(name)
    img_name = get_image_name(name)

    print("Removing any existing image with this name")
    run("docker rmi {} 2> /dev/null".format(img_name))

    print("Creating the new image")
    run("docker commit {} {}".format(container_name, img_name))


def do_launch(args):
    name = conf.get("wup.env_name", scope="global")
    filepath = conf.get("wup.env_filepath", scope="global")

    variables, templates, bashrc = parse_env(filepath, "launch")
    cont_name = get_container_name(name)
    cmds = bashrc + templates["LAUNCH"] + ["\nexit\n"]

    print("Starting container...")
    run("docker start " + cont_name)

    print("Connecting to terminal...")
    run(get_open_cmd(cont_name, cmds))


def do_exec(args):
    name = conf.get("wup.env_name", scope="global")
    filepath = conf.get("wup.env_filepath", scope="global")

    cmd = args.pop_parameter()
    cont_name = get_container_name(name)
    variables, templates, bashrc = parse_env(filepath, "exec")

    cmds = bashrc + templates["EXEC"] + [cmd, "\nexit\n"]

    print("Starting container...")
    run("docker start " + cont_name)

    print("Connecting to terminal...")
    run(get_open_cmd(cont_name, cmds))


def do_export(args):
    name = conf.get("wup.env_name", scope="global")
    filepath = conf.get("wup.env_filepath", scope="global")

    img_name = get_image_name(name)
    filepath = get_export_filepath(name)

    print("Exporting image commit for", img_name, "as", filepath)
    run("docker save {} | gzip > {}".format(img_name, filepath))


def do_import(args):
    filepath = args.pop_parameter()

    print("Importing image...")
    run(["zcat {}".format(filepath), "docker load -q"])


def do_new(args):
    name = conf.get("wup.env_name", scope="global")
    filepath = conf.get("wup.env_filepath", scope="global")

    variables, templates, bashrc = parse_env(filepath, "new")
    img_name = get_image_name(name)
    cont_name = get_container_name(name)
    volumes = "-v " + " -v ".join(templates["VOLUMES"]) if templates["VOLUMES"] else ""
    cmds = bashrc + templates["NEW"]
    
    print("Removing previous container...")
    run("docker rm %s 2> /dev/null" % cont_name)

    print("Creating container from image...")
    run("docker run -i --name {} {} {}".format(cont_name, volumes, img_name), write=cmds)


def do_rm(args):
    name = conf.get("wup.env_name", scope="global")
    cont_name = get_container_name(name)

    run("docker kill " + cont_name)
    run("docker rm " + cont_name)

def do_rmi(args):
    name = conf.get("wup.env_name", scope="global")
    img_name = get_image_name(name)

    run("docker rmi " + img_name)


def do_ls(args):
    run("docker ps -a -f \"name=wcont__*\"")


def do_lsi(args):
    run("docker image ls \"wimg*\"")


def main(args):
    r = Route(args)

    r.map("set", do_set, "Set the current env to use")
    r.map("build", do_build, "Builds the current environment")
    r.map("open", do_open, "Opens the environment")
    r.map("launch", do_launch, "Executes the commands in @LAUNCH@ from inside the environment")
    r.map("exec", do_exec, "Executes a custom command inside the environment")
    r.map("ls", do_ls, "Lists all environments")
    r.map("lsi", do_lsi, "Lists all environment images")
    r.map("rm", do_rm, "Remove an environment")
    r.map("rmi", do_rmi, "Remove an environment image")
    r.map("commit", do_commit, "Create an image from the environment")
    r.map("export", do_export, "Export the current image to a file in the current folder")
    r.map("import", do_import, "Imports an image file into a new image")
    r.map("new", do_new, "Recreate the current environment using the existing image")
    
    r.run()