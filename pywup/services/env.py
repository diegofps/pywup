from pywup.services.general import get_container_name, get_image_name, get_export_filepath
from pywup.services.system import run, error, quote, colors
from pywup.services.context import Context
from pywup.services import docker
from pywup.services import conf

import os


class Env(Context):

    def __init__(self, other=None):
        Context.__init__(self, other)


    def ip(self):
        self.require(env=True)
        return docker.get_container_ip(self.cont_name)
    

    def is_running(self):
        self.require(env=True)
        return docker.is_container_running(self.cont_name)


    def has_img(self, img_name=None):
        self.require(env=True)
        return docker.exists_image(self.img_name)


    def build(self, fromCommit=None):
        self.require(env=True)
        docker.build_with_commits(self.cont_name, self.img_name, self.e, fromCommit)


    def start(self):
        self.require(env=True)
        docker.start_container(self.cont_name, self.e)


    def open(self, cont_name=None):
        self.require(env=True)

        cmds = self.e.bashrc + self.e.open
        
        docker.start_container(self.cont_name, self.e)
        docker.open_and_init(self.cont_name, cmds, True)


    def launch(self):
        self.require(env=True)
        docker.launch(self.cont_name, self.e)


    def exec(self, cmds):
        self.require(env=True)
        docker.exec(self.cont_name, self.e.bashrc + cmds)


    def run(self, params):
        cmd = [self.e.run + " " + params + "\n", "exit\n"]
        self.exec(cmd)


    def commit(self):
        self.require(env=True)
        docker.commit(self.cont_name, self.img_name)


    def stop(self):
        self.require(env=True)
        docker.stop(self.cont_name)


    def rm_container(self):
        self.require(env=True)
        print(self.cont_name)
        docker.rm_container(self.cont_name)


    def rm_image(self):
        self.require(env=True)
        docker.rm_image(self.img_name)


    def ls_containers(self):
        docker.ls_containers()


    def ls_images(self):
        docker.ls_images()


    def ls_commits(self):
        for x in docker.ls_commits():
            print(*x)


    def export(self):
        filepath = get_export_filepath(self.name)

        print("Exporting image commit for " + colors.YELLOW + self.img_name + colors.RESET + " as " + colors.YELLOW + filepath + colors.RESET)
        docker.export_image(self.img_name, filepath)


    def load(self, filepath):
        print("Importing image...")
        docker.load_image(filepath)


    def deploy(self):
        self.require(env=True)
        docker.deploy(self.img_name, self.cont_name, self.e)
