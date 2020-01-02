from pywup.services.system import Args, Route, error, abort


def renv_set(args):
    pass


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


def main(args):
    r = Route(args)

    r.map("set", renv_set, "Sets the current machines set using a .renv file")
    r.map("deploy", renv_deploy, "Deploy an image and its data to remote machines")
    r.map("start", renv_start, "Starts the container in the remote machines")
    r.map("stop", renv_stop, "Stops containers in the remote machines")
    r.map("open", renv_open, "Opens a remote environment")
    r.map("exec", renv_exec, "Execute a command in all remote environments")
    r.map("launch", renv_launch, "Execute the @LAUNCH@ instructions in all remote environment")
    r.map("run", renv_run, "Execute the @RUN@ command in the remote environment, with given parameters")
    
    r.run()
