from pywup.services.general import parse_env, get_container_name, get_image_name, parse_env, get_export_filepath
from pywup.services.system import run, error, quote
from pywup.services.context import Context
from pywup.services import docker
from pywup.services import conf

import os


class Env(Context):

    def __init__(self, other=None):
        Context.__init__(self, other)


    def ip(self):
        self.require(env=True)
        return docker.ip(self.cont_name)
    

    def is_running(self):
        self.require(env=True)
        return docker.is_running(self.cont_name)


    def has_img(self, img_name=None):
        self.require(env=True)
        return docker.exists_img(self.img_name)


    def build(self):
        self.require(env=True)
        docker.build(self.cont_name, self.bashrc, self.templates, self.variables)


    def start(self):
        self.require(env=True)
        docker.start(self.cont_name, self.bashrc, self.templates)


    def open(self, cont_name=None):
        self.require(env=True)

        cmds = self.bashrc + self.templates["OPEN"]
        
        docker.start(self.cont_name, self.bashrc, self.templates)
        docker.open_and_init(self.cont_name, cmds, True)


    def launch(self):
        self.require(env=True)
        docker.launch(self.cont_name, self.bashrc, self.templates)


    def exec(self, cmds):
        self.require(env=True)
        docker.exec(self.cont_name, self.bashrc + cmds)


    def run(self, params):
        cmd = [self.variables["RUN"] + " " + params]
        self.exec(cmd)


    def commit(self):
        self.require(env=True)
        docker.commit(self.cont_name, self.img_name)


    def stop(self):
        self.require(env=True)
        docker.stop(self.cont_name)


    def rm(self):
        self.require(env=True)
        docker.rm(self.cont_name)


    def rmi(self):
        self.require(env=True)
        docker.rmi(self.img_name)


    def ls(self):
        docker.ls()


    def lsi(self):
        docker.lsi()


    def export(self):
        filepath = get_export_filepath(self.name)

        print("Exporting image commit for", self.img_name, "as", filepath)
        docker.export(self.img_name, filepath)


    def load(self, filepath):
        print("Importing image...")
        docker.load(filepath)


    def new(self):
        self.require(env=True)
        docker.new(self.img_name, self.cont_name, self.bashrc, self.templates, self.variables)
