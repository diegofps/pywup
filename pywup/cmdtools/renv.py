from pywup.services.system import Args, Route, error, abort
from pywup.services.general import update_state
from pywup.services import conf

import yaml
import os


def renv_set(args):
    try:
        if not args.has_parameter():
            conf.set("wup.cluster_filepath", "", scope="global")
            conf.set("wup.cluster_name", "", scope="global")

        else:
            filepath = os.path.abspath(args.pop_parameter())
            name = os.path.splitext(os.path.basename(filepath))[0]

            with open(filepath, "r") as fin:
                yaml.load(fin)
            
            conf.set("wup.cluster_filepath", filepath, scope="global")
            conf.set("wup.cluster_name", name, scope="global")
        
    except (FileNotFoundError, yaml.scanner.ScannerError):
        error("Missing or invalid file:", filepath)

    update_state()


def renv_deploy(args):
    pass


def renv_start(args):
    pass


def renv_stop(args):
    pass


def renv_open(args):
    pass


def renv_exec(args):
    pass


def renv_launch(args):
    pass


def renv_run(args):
    pass


def main(cmd, args):
    r = Route(args, cmd)

    r.map("set", renv_set, "Sets the current machines set using a .renv file")
    r.map("deploy", renv_deploy, "Deploy an image and its data to remote machines")
    r.map("start", renv_start, "Starts the container in the remote machines")
    r.map("stop", renv_stop, "Stops containers in the remote machines")
    r.map("open", renv_open, "Opens a remote environment")
    r.map("exec", renv_exec, "Execute a command in all remote environments")
    r.map("launch", renv_launch, "Execute the @LAUNCH@ instructions in all remote environment")
    r.map("run", renv_run, "Execute the @RUN@ command in the remote environment, with given parameters")
    
    r.run()
