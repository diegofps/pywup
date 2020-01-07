from pywup.services.general import parse_env, get_container_name, get_image_name, get_open_cmd, parse_env, get_export_filepath
from pywup.services.system import run, error, quote
from pywup.services import conf

import os


class Env:

    def __init__(self):
        self.reload()
    

    def reload(self):
        try:
            self.name = conf.get("wup.env_name", scope="global")
            self.filepath = conf.get("wup.env_filepath", scope="global")

            if self.filepath:
                self.variables, self.templates, self.bashrc = parse_env(self.filepath)
                self.cont_name = get_container_name(self.name)
                self.img_name = get_image_name(self.name)
            
        except:
            self.name = ""
            self.filepath = ""
            self.cont_name = None
            self.img_name = None
            self.variables, self.templates, self.bashrc = None, None, None


    def ip(self):
        cmd = "docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' " + self.cont_name
        status, rows = run(cmd, read=True)

        if status != 0 or not rows:
            error("Command error")
        
        return rows[0].strip()
    

    def is_running(self):
        cmd = "docker inspect -f '{{.State.Running}}' " + self.cont_name
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
        cmd = [self.variables["RUN"] + " " + params]
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
