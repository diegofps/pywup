from pywup.services.system import error, abort, WupError, run, Args, Route, quote, Params
from pywup.services.env import Env

import sys
import os

def do_use(cmd, args):
    p = Params(cmd, args)
    p.map("envfile", 1, None, "Name or path of the envfile to use")
    
    if p.run():
        Env().use(p.envfile)


def do_build(cmd, args):
    p = Params(cmd, args)
    p.map("--from", 1, None, "Start build from this snapshot")
    p.map("--v", 1, None, "Manually map a host folderpath to a folderpath inside this new environment")
    p.map("--all-volumes", 0, None, "Deploy using all volumes, BUILD_VOLUMES and DEPLOY_VOLUMES")
    
    if p.run():
        Env().build(fromCommit=p.__from, extra_volumes=p.every__v, allVolumes=p.__all_volumes)


def do_open(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().open()


def do_start(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().start()


def do_stop(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().stop()


def do_commit(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().commit()


def do_launch(cmd, args):
    p = Params(cmd, args)
    p.map("--attach", 0, None, "Connects your terminal to the process inside the container")

    if p.run():
        Env().launch(p.__attach)


def do_exec(cmd, args):
    p = Params(cmd, args)
    p.map("command", 1, None, "Command to be run inside the container", mandatory=True)
    p.map("--attach", 0, None, "Connects your terminal to the process inside the container")
    
    if p.run(): 
        Env().exec([p.command], p.__attach)


def do_export(cmd, args):
    p = Params(cmd, args)
    p.map("--tag", 1, None, "Replaces the tag in the output file. Default is the date")
    p.map("--arch", 1, None, "Replaces the architecture name in the output file. Default name is generic")
    
    if p.run():
        Env().export(version=p.__tag, arch=p.__arch)


def do_import(cmd, args):
    p = Params(cmd, args)
    p.map("filepath", 1, None, "Path to the image to be imported from disk")

    if p.run():
        Env().load(p.filepath)


def do_run(cmd, args):
    p = Params(cmd, args, limit_parameters=False)

    if p.run():
        arguments = ["\"" + x + "\"" for x in p._input_parameters]
        Env().run(" ".join(arguments))


def do_deploy(cmd, args):
    p = Params(cmd, args)
    p.map("--v", 1, [], "Manually map a host folderpath to a folderpath inside this new environment")
    p.map("--all-volumes", 0, None, "Deploy using all volumes, BUILD_VOLUMES and DEPLOY_VOLUMES")
    
    if p.run():
        Env().deploy(p.every__v, p.__all_volumes)


def do_rm(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().rm_container()


def do_rmi(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().rm_image()


def do_ls(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().ls_containers()


def do_lsi(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().ls_images()


def do_lsc(cmd, args):
    p = Params(cmd, args)
    if p.run():
        Env().ls_commits()


def do_ip(cmd, args):
    p = Params(cmd, args)
    if p.run():
        print(Env().ip())


def do_get(cmd, args):
    p = Params(cmd, args)
    p.map("src", 1, None, "Source folder inside the environment", mandatory=True)
    p.map("dst", 1, None, "Destination folder inside the host", mandatory=True)
    
    if p.run():
        print(Env().get(p.src, p.dst))


def do_send(cmd, args):
    p = Params(cmd, args)
    p.map("src", 1, None, "Source folder inside the host", mandatory=True)
    p.map("dst", 1, None, "Destination folder inside the environment", mandatory=True)
    
    if p.run():
        print(Env().send(p.src, p.dst))


def main(cmd, args):
    r = Route(args, cmd)

    r.map("use", do_use, "Sets an envfile to use")
    r.map("build", do_build, "Builds the current environment")
    r.map("open", do_open, "Opens the environment, starting it if necessary")
    r.map("start", do_start, "Starts the environment container")
    r.map("stop", do_stop, "Stops the environment container")
    r.map("launch", do_launch, "Executes the commands in @LAUNCH@ from inside the environment")
    r.map("exec", do_exec, "Executes a custom command inside the environment")
    r.map("run", do_run, "Executes the command define with RUN inside the environment with the parameters given")
    r.map("ls", do_ls, "Lists all environments")
    r.map("lsi", do_lsi, "Lists all environment images")
    r.map("lsc", do_lsc, "Lists all commit images")
    r.map("rm", do_rm, "Remove the environment container")
    r.map("rmi", do_rmi, "Remove the environment image")
    r.map("commit", do_commit, "Create an image from the environment")
    r.map("export", do_export, "Export the current image to a file in the current folder")
    r.map("import", do_import, "Imports an image file into a new image")
    r.map("deploy", do_deploy, "Recreate the image built using the deploy volumes")
    r.map("ip", do_ip, "Get the environment ip address")
    r.map("get", do_get, "Copy a file from the environment to your host")
    r.map("send", do_send, "Send a file from the host to your environment")
    
    r.run()
