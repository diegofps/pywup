from pywup.services.general import get_image_name, get_container_name, lookup_env, update_state, get_export_filepath
from pywup.services.system import error, abort, WupError, run, Args, Route, quote, Params
from pywup.services.env import Env
from pywup.services import conf

import sys
import os


def do_build(cmd, args):
    params = Params(cmd, args)
    params.map("--from", 1, None, "Start build from this snapshot")
    params.map("--v", 1, None, "Manually map a host folderpath to a folderpath inside this new environment")
    params.map("--all-volumes", 0, None, "Deploy using all volumes, BUILD_VOLUMES and DEPLOY_VOLUMES")
    
    if params.run():
        fromCommit = params.get("--from")
        volumes = params.get_all("--v")
        useAllVolumes = params.has("--all-volumes")

        Env().build(fromCommit=fromCommit, extra_volumes=volumes, allVolumes=useAllVolumes)


def do_open(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().open()


def do_start(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().start()


def do_stop(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().stop()


def do_commit(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().commit()


def do_launch(cmd, args):
    params = Params(cmd, args)
    params.map("--attach", 0, None, "Connects your terminal to the process inside the container")

    if params.run():
        attach = params.has("--attach")
        Env().launch(attach)


def do_exec(cmd, args):
    params = Params(cmd, args)
    params.map("command", 1, None, "Command to be run inside the container", mandatory=True)
    params.map("--attach", 0, None, "Connects your terminal to the process inside the container")
    
    if params.run():
        cmds = [params.get("command")]
        attach = params.has("--attach")
        Env().exec(cmds, attach)


def do_export(cmd, args):
    params = Params(cmd, args)
    params.map("tag", 1, None, "If tag is provided, the output file will be wimg__<ENVNAME>.<TAG>.gz")
    
    if params.run():
        Env().export(params.get("tag"))


def do_import(cmd, args):
    params = Params(cmd, args)
    params.map("filepath", 1, None, "Path to the image to be imported from disk")

    if params.run():
        Env().load(params.get("filepath"))


def do_run(cmd, args):
    params = Params(cmd, args, limit_parameters=False)

    if params.run():
        Env().run(" ".join(params.input_parameters))


def do_deploy(cmd, args):
    params = Params(cmd, args)
    params.map("--v", 1, [], "Manually map a host folderpath to a folderpath inside this new environment")
    params.map("--all-volumes", 0, None, "Deploy using all volumes, BUILD_VOLUMES and DEPLOY_VOLUMES")
    
    if params.run():
        useAllVolumes = params.has("--all-volumes")
        volumes = params.get_all("--v")
        Env().deploy(volumes, useAllVolumes)


def do_rm(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().rm_container()


def do_rmi(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().rm_image()


def do_ls(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().ls_containers()


def do_lsi(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().ls_images()


def do_lsc(cmd, args):
    params = Params(cmd, args)
    if params.run():
        Env().ls_commits()


def do_ip(cmd, args):
    params = Params(cmd, args)
    if params.run():
        print(Env().ip())


def do_get(cmd, args):
    params = Params(cmd, args)
    params.map("src", 1, None, "Source folder inside the environment", mandatory=True)
    params.map("dst", 1, None, "Destination folder inside the host", mandatory=True)
    
    if params.run():
        print(Env().get(params.get("src"), params.get("dst")))


def do_send(cmd, args):
    params = Params(cmd, args)
    params.map("src", 1, None, "Source folder inside the host", mandatory=True)
    params.map("dst", 1, None, "Destination folder inside the environment", mandatory=True)
    
    if params.run():
        print(Env().send(params.get("src"), params.get("dst")))


def main(cmd, args):
    r = Route(args, cmd)

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
