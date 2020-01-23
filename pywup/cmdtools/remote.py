from pywup.services.system import Route, Params
from pywup.services.remote import Remote


def sync_build(cmd, args):
    p = Params(cmd, args)

    p.map("--clear", 0, None, "Deletes all volumes associated to this env stored in the build machines prior to sending anything")
    p.map("--v", 1, None, "Sends a custom volume/directory to all build machines")
    p.map("--env", 0, None, "Sends the environment file to the build machines")
    p.map("--all-build", 0, None, "Sends all build volumes defined in the environment file")
    p.map("--all-deploy", 0, None, "Sends all deploy volumes defined in the environment file")

    if p.run():
        Remote().sync_build(p.__clear, p.every__v, p.__env, p.__all_build, p.__all_deploy)


def sync_deploy(cmd, args):
    p = Params(cmd, args)
    p.map("--clear", 0, None, "Deletes all volumes associated to this env stored in the deploy machines")
    p.map("--v", 1, None, "Sends a custom volume/directory to all deploy machines")
    p.map("--env", 0, None, "Sends the environment file to the deploy machines")
    p.map("--all-build", 0, None, "Sends all build volumes defined in the environment file")
    p.map("--all-deploy", 0, None, "Sends all deploy volumes defined in the environment file")
    p.map("--image", 0, None, "Sends trhe build image file to all deploy machines, respecting their archs")

    if p.run():
        Remote().sync_deploy(p.__clear, p.every__dir, p.__env, p.__all, p.__image)


def build(cmd, args):
    p = Params(cmd, args)
    p.map("--sync", 0, None, "Syncs everything before the build")
    p.map("--v", 1, None, "Map a custom volume inside the build machines")

    if p.run():
        Remote().build(p.__sync, p.every__v)


def deploy(cmd, args):
    p = Params(cmd, args)
    p.map("--sync", 0, None, "Syncs everything before the deploy")
    p.map("--v", 1, None, "Map a custom volume inside the deploy machines")

    if p.run():
        Remote().deploy(p.__sync, p.every__v)


def start(cmd, args):
    p = Params(cmd, args)
    p.map("--clean", 0, None, "Stops all other containers in the deploy machines prior to starting this")

    if p.run():
        Remote().start(p.__clean)


def stop(cmd, args):
    p = Params(cmd, args)
    p.map("--clean", 0, None, "Stops the environment and all other containers in the deploy machines")

    if p.run():
        Remote().stop(p.__clean)


def open(cmd, args):
    p = Params(cmd, args)
    p.map("name", 0, None, "Name of the remote machine to open")

    if p.run():
        Remote().open(p.name)


def exec(cmd, args):
    p = Params(cmd, args)
    p.map("command", 0, None, "Command to be executed in all deploy machines")

    if p.run():
        Remote().open(p.command)


def launch(cmd, args):
    p = Params(cmd, args)

    if p.run():
        Remote().launch()


def run(cmd, args):
    p = Params(cmd, args, limit_parameters=False)

    if p.run():
        arguments = ["\"" + x + "\"" for x in p._input_parameters]
        Remote().run(" ".join(arguments))


def main(cmd, args):
    r = Route(args, cmd)

    r.map("sync-build", sync_build, "Syncs directories to build machines")
    r.map("sync-deploy", sync_deploy, "Syncs directories against the deploy machines")
    r.map("start", start, "Starts the container in the remote machines")
    r.map("stop", stop, "Stops containers in the remote machines")
    r.map("open", open, "Opens a remote environment")
    r.map("exec", exec, "Execute a command in all remote environments")
    r.map("launch", launch, "Execute the @LAUNCH@ instructions in all remote environment")
    r.map("run", run, "Execute the @RUN@ command in the remote environment, passing the parameters presented now")
    
    r.run()
