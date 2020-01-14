from pywup.services.general import get_image_name, get_container_name, lookup_env, update_state, get_export_filepath
from pywup.services.system import error, abort, WupError, run, Args, Route, quote
from pywup.services.env import Env
from pywup.services import conf

import sys
import os


def do_build(args):
    fromCommit = None

    while args.has_cmd():
        cmd = args.pop_cmd()

        if cmd == "--from":
            fromCommit = args.pop_parameter()
        
        else:
            error("Invalid parameter:", cmd)
    
    Env().build(fromCommit=fromCommit)


def do_open(args):
    Env().open()


def do_start(args):
    Env().start()


def do_stop(args):
    Env().stop()


def do_commit(args):
    Env().commit()


def do_launch(args):
    Env().launch()


def do_exec(args):
    Env().exec([args.pop_parameter])


def do_export(args):
    Env().export()


def do_import(args):
    Env().load(args.pop_parameter())


def do_run(args):
    Env().run(" ".join(args.all()))


def do_deploy(args):
    Env().deploy()


def do_rm(args):
    Env().rm_container()


def do_rmi(args):
    Env().rm_image()


def do_ls(args):
    Env().ls_containers()


def do_lsi(args):
    Env().ls_images()


def do_lsc(args):
    Env().ls_commits()


def do_ip(args):
    print(Env().ip())


def main(args):
    r = Route(args)

    r.map("build", do_build, "Builds the current environment")
    r.map("open", do_open, "Opens the environment, starting it if necessary")
    r.map("start", do_start, "Starts this container")
    r.map("stop", do_stop, "Stops this container")
    r.map("launch", do_launch, "Executes the commands in @LAUNCH@ from inside the environment")
    r.map("exec", do_exec, "Executes a custom command inside the environment")
    r.map("run", do_run, "Executes the command define with RUN inside the environment with the parameters given")
    r.map("ls", do_ls, "Lists all environments")
    r.map("lsi", do_lsi, "Lists all environment images")
    r.map("lsc", do_lsc, "Lists all commit images")
    r.map("rm", do_rm, "Remove an environment")
    r.map("rmi", do_rmi, "Remove an environment image")
    r.map("commit", do_commit, "Create an image from the environment")
    r.map("export", do_export, "Export the current image to a file in the current folder")
    r.map("import", do_import, "Imports an image file into a new image")
    r.map("deploy", do_deploy, "Recreate the image built using the deploy volumes")
    r.map("ip", do_ip, "Recreate the current environment using the existing image")
    
    r.run()