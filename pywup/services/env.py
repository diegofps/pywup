from pywup.services.general import parse_env, get_container_name, get_image_name, get_open_cmd, parse_env, get_export_filepath
from pywup.services.system import run, error, quote
from pywup.services.context import Context
from pywup.services import conf

import os


class Env(Context):

    def __init__(self, other=None):
        Context.__init__(self, other)


    def ip(self, cont_name=None):
        if cont_name is None:
            cont_name = self.cont_name
        
        cmd = "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + cont_name
        status, rows = run(cmd, read=True)

        if status != 0 or not rows:
            error("Command error")
        
        return rows[0].strip()
    

    def is_running(self, cont_name=None):
        if cont_name is None:
            cont_name = self.cont_name
        
        cmd = "docker inspect -f '{{.State.Running}}' " + cont_name
        status, rows = run(cmd, read=True)

        if status != 0 or not rows:
            error("Command error")
        
        return rows[0] == "true\n"


    def has_img(self):
        status, rows = run("docker image ls \"{}\"".format(self.img_name), read=True)

        if status != 0:
            error("Command error")
        
        return len(rows) == 2


    def build(self):
        createCmd = "docker run -i --name tmp"
        
        if self.templates["VOLUMES"]:
            createCmd += " -v " + " -v ".join(self.templates["VOLUMES"])
        
        if self.variables["EXPOSE"]:
            createCmd += " --expose=" + " --expose=".join(self.variables["EXPOSE"].split(","))

        if self.variables["MAP_PORTS"]:
            createCmd += " -p " + " -p".join(self.variables["MAP_PORTS"].split(","))

        createCmd += " " + self.variables["BASE"]
        print(createCmd)

        self.rm("tmp")

        cmds = self.bashrc + self.templates["BUILD"]
        run(createCmd, write=cmds)

        self.rm()
        self.rename("tmp", self.cont_name)


    def rename(self, oldname, newname):
        run("docker rename " + oldname + " " + newname)


    def start(self, cont_name=None):
        if cont_name is None:
            cont_name = self.cont_name
        
        if self.is_running(cont_name):
            return
        
        run("docker start " + cont_name)

        cmds = self.bashrc + self.templates["START"] + ["sleep 1\n exit\n"]

        self.exec(cmds, cont_name)


    def open(self, cont_name=None):
        if cont_name is None:
            cont_name = self.cont_name
        
        self.start(cont_name)

        cmds = self.bashrc + self.templates["OPEN"]
        run(get_open_cmd(cont_name, cmds, True))


    def launch(self, cont_name=None):
        if cont_name is None:
            cont_name = self.cont_name
        
        self.exec(self.bashrc + self.templates["LAUNCH"], cont_name)


    def exec(self, cmds, cont_name=None):
        if cont_name is None:
            cont_name = self.cont_name
        
        run(get_open_cmd(cont_name, cmds))


    def run(self, params):
        cmd = [self.variables["RUN"] + " " + params]
        self.exec(cmd)


    def commit(self):
        self.rmi()
        run("docker commit " + self.cont_name + " " + self.img_name)


    def stop(self, cont_name=None):
        if cont_name is None:
            cont_name = self.cont_name
        
        run("docker kill %s 2> /dev/null" % cont_name)


    def rm(self, cont_name=None):
        if cont_name is None:
            cont_name = self.cont_name
        
        self.stop(cont_name)
        run("docker rm %s 2> /dev/null" % cont_name)


    def rmi(self, img_name=None):
        if img_name is None:
            img_name = self.img_name
        
        run("docker rmi " + img_name + " 2> /dev/null")


    def ls(self):
        run("docker ps -a -f \"name=wcont__*\"")


    def lsi(self):
        run("docker image ls \"wimg*\"")


    def export(self):
        filepath = get_export_filepath(self.name)

        print("Exporting image commit for", self.img_name, "as", filepath)
        run("docker save {} | gzip > {}".format(self.img_name, filepath))


    def load(self, filepath):
        print("Importing image...")
        run(["zcat " + filepath, "docker load -q"])


    def new(self):
        if not self.has_img():
            error("Image not found")

        self.rm()

        createCmd = "docker run -i --name " + self.cont_name

        if self.templates["VOLUMES"]:
            createCmd += " -v " + " -v ".join(self.templates["VOLUMES"])
        
        if self.variables["EXPOSE"]:
            createCmd += " --expose=" + " --expose=".join(self.variables["EXPOSE"].split(","))

        if self.variables["MAP_PORTS"]:
            createCmd += " -p " + " -p".join(self.variables["MAP_PORTS"].split(","))

        createCmd += " " + self.img_name
        print(createCmd)

        cmds = self.bashrc + self.templates["NEW"]
        run(createCmd, write=cmds)
