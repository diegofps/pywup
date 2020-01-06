from pywup.services.general import parse_env, get_container_name, get_image_name, get_open_cmd, parse_env, parse_image_name
from pywup.services.system import run, error, quote
from pywup.services import conf

import os


class Env:

    def __init__(self, filepath=None):
        if filepath:
            self.set(filepath)
        self.reload()
    

    def reload(self):
        self.name = conf.get("wup.env_name", scope="global")
        self.filepath = conf.get("wup.env_filepath", scope="global")
        self.cont_name = get_container_name(self.name)
        self.img_name = get_image_name(self.name)
        self.variables, self.templates, self.bashrc = parse_env(self.filepath)


    def set(self, filepath):
        if not filepath:
            error("Invalid filepath")
        else:
            name, filepath = parse_image_name(filepath)

        conf.set("wup.env_name", name, scope="global")
        conf.set("wup.env_filepath", filepath, scope="global")


    def is_running(self):
        cmd = "docker inspect -f '{{.State.Running}}' " + self.cont_name
        status, rows = run(cmd, read=True)

        #import pdb; pdb.set_trace()

        if status != 0 or not rows:
            error("Command error")
        
        return rows[0] == "true\n"


    def build(self):
        self.rm()

        createCmd = "docker run -i --name " + self.cont_name
        
        if self.templates["VOLUMES"]:
            createCmd += " -v " + " -v ".join(self.templates["VOLUMES"])
        
        if self.variables["EXPOSE"]:
            createCmd += " --expose=" + " --expose=".join(self.variables["EXPOSE"].split(","))

        if self.variables["MAP_PORTS"]:
            createCmd += " -p " + " -p".join(self.variables["MAP_PORTS"].split(","))

        createCmd += " " + self.variables["BASE"]
        print(createCmd)

        cmds = self.bashrc + self.templates["BUILD"]
        run(createCmd, write=cmds)


    def start(self):
        if self.is_running():
            return
        
        run("docker start " + self.cont_name)

        cmds = self.bashrc + self.templates["START"] + ["sleep 1\n exit\n"]

        self.exec(cmds)


    def open(self):
        self.start()

        cmds = self.bashrc + self.templates["OPEN"]
        run(get_open_cmd(self.cont_name, cmds, True))


    def launch(self):
        self.exec(self.bashrc + self.templates["LAUNCH"])


    def exec(self, cmds):
        run(get_open_cmd(self.cont_name, cmds))


    def run(self, params):
        cmd = [self.variables["RUN"] + params]
        self.exec(cmd)


    def commit(self):
        self.rmi()
        run("docker commit " + self.cont_name + " " + self.img_name)


    def stop(self):
        run("docker kill %s 2> /dev/null" % self.cont_name)


    def rm(self):
        self.stop()
        run("docker rm %s 2> /dev/null" % self.cont_name)


    def rmi(self):
        run("docker rmi " + self.img_name + " 2> /dev/null")


    def ls(self):
        run("docker ps -a -f \"name=wcont__*\"")


    def lsi(self):
        run("docker image ls \"wimg*\"")
