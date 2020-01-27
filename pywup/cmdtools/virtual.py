from pywup.services.system import Route, Params, error
from pywup.services.virtual import Virtual


def sync(cmd, args):
    p = Params(cmd, args)

    p.map("--build", 0, None, "Indicates that all instructions will performed on the build machines")
    p.map("--deploy", 0, None, "Indicates that all instructions will performed on the deploy machines")
    p.map("--clear", 0, None, "Indicates that data will be removed on the remote machines, not sent")
    p.map("--env", 0, None, "Sync will act upon the env file")
    p.map("--image", 0, None, "Sync will act upon the image file")
    p.map("--bv", 0, None, "Sync will act upon the build volumes")
    p.map("--dv", 0, None, "Sync will act upon the deploy volumes")
    p.map("--dir", 0, None, "Sync will act upon build and this custom directory")
    p.map("--a", 0, None, "Activates --env --bv when using --build. Activates --env --image --dv when using --deploy")

    if p.run():
        build = p.__build
        deploy = p.__deploy
        clear = p.__clear
        extra_dirs = p.every__dir

        if not build and not deploy:
            error("You must set --build or --deploy")

        if build and deploy:
            error("Activating both --build and --deploy is not allowed")

        env = p.__env
        image = p.__image
        bv = p.__bv
        dv = p.__dv

        if p.__a and build:
            env = True
            bv = True
        
        if p.__a and deploy:
            env = True
            image = True
            dv = True
        
        Virtual().sync(build, deploy, clear, env, image, bv, dv, extra_dirs)


def build(cmd, args):
    p = Params(cmd, args)
    p.map("--sync", 0, None, "Syncs everything before the build")
    p.map("--v", 1, None, "Map a custom volume inside the build machines")

    if p.run():
        Virtual().build(p.__sync, p.every__v)


def deploy(cmd, args):
    p = Params(cmd, args)
    p.map("--sync", 0, None, "Syncs everything before the deploy")
    p.map("--v", 1, None, "Map a custom volume inside the deploy machines")

    if p.run():
        Virtual().deploy(p.__sync, p.every__v)


def start(cmd, args):
    p = Params(cmd, args)
    p.map("--clean", 0, None, "Stops all other containers in the deploy machines prior to starting this")

    if p.run():
        Virtual().start(p.__clean)


def stop(cmd, args):
    p = Params(cmd, args)
    p.map("--clean", 0, None, "Stops the environment and all other containers in the deploy machines")

    if p.run():
        Virtual().stop(p.__clean)


def open(cmd, args):
    p = Params(cmd, args)
    p.map("name", 0, None, "Name of the remote machine to open")

    if p.run():
        Virtual().open(p.name)


def exec(cmd, args):
    p = Params(cmd, args)
    p.map("command", 0, None, "Command to be executed in all deploy machines")

    if p.run():
        Virtual().exec(p.command)


def launch(cmd, args):
    p = Params(cmd, args)

    if p.run():
        Virtual().launch()


def run(cmd, args):
    p = Params(cmd, args, limit_parameters=False)

    if p.run():
        arguments = ["\"" + x + "\"" for x in p._input_parameters]
        Virtual().run(" ".join(arguments))


def main(cmd, args):
    r = Route(args, cmd)

    r.map("sync", sync, "Sends volumes, env files and images to remote machines")
    r.map("build", build, "Builds the env image inside the build machines")
    r.map("deploy", deploy, "Deploy the images built inside the deploy machines")
    r.map("start", start, "Starts the container in the remote machines")
    r.map("stop", stop, "Stops containers in the remote machines")
    r.map("open", open, "Opens a remote environment")
    r.map("exec", exec, "Execute a command in all remote environments")
    r.map("launch", launch, "Execute the @LAUNCH@ instructions in all remote environment")
    r.map("run", run, "Execute the @RUN@ command in the remote environment, passing the parameters presented now")
    
    r.run()
