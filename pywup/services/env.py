from pywup.services.system import run, error, quote, colors
from pywup.services.context import Context, lookup_env
from pywup.services.io import Preferences
from pywup.services import docker

import os


class Env(Context):

    def __init__(self):
        Context.__init__(self)


    def use(self, name):
        pref = Preferences()

        if name is None:
            print(pref.env_filepath)
            return

        if name == "-":
            pref.env_name = None
            pref.env_filepath = None
        
        else:
            name, filepath = lookup_env(name)

            pref.env_name = name
            pref.env_filepath = filepath
        
        pref.save()


    def ip(self):
        return docker.get_container_ip(self.envfile().container_name)
    

    def is_running(self):
        return docker.is_container_running(self.envfile().container_name)


    def has_img(self, img_name=None):
        return docker.exists_image(self.envfile().image_name)


    def build(self, fromCommit=None, extra_volumes=[], allVolumes=False):
        env = self.envfile()
        docker.build_with_commits(env.container_name, env.image_name, env, fromCommit, extra_volumes, allVolumes)


    def start(self):
        env = self.envfile()
        docker.start_container(env.container_name, env)


    def open(self, cont_name=None):
        env = self.envfile()

        cmds = env.bashrc + env.open
        
        docker.start_container(env.container_name, env)
        docker.init_and_open(env.container_name, cmds)


    def launch(self, attach=False):
        env = self.envfile()
        docker.launch(env.container_name, env, attach)


    def exec(self, cmds, attach=False):
        env = self.envfile()
        docker.start_container(env.container_name, env)
        docker.exec(env.container_name, env.bashrc, cmds + ["\n"], attach)


    def run(self, params, attach=False):
        env = self.envfile()
        cmd = [env.run + " " + params + "\n"]
        self.exec(cmd, attach)


    def commit(self):
        env = self.envfile()
        docker.commit(env.container_name, env.image_name)


    def stop(self):
        env = self.envfile()
        docker.stop(env.container_name)


    def rm_container(self):
        env = self.envfile()
        print(env.container_name)
        docker.rm_container(env.container_name)


    def rm_image(self):
        env = self.envfile()
        docker.rm_image(env.image_name)


    def ls_containers(self):
        docker.ls_containers()


    def ls_images(self):
        docker.ls_images()


    def ls_commits(self):
        for x in docker.ls_commits():
            print(*x)


    def export(self, version=None, arch=None):
        env = self.envfile()
        filepath = env.export_filepath(version=version, arch=arch)
        print("Exporting commit image for " + colors.yellow(env.image_name) + " as " + colors.yellow(filepath))
        docker.export_image(env.image_name, filepath)


    def load(self, filepath):
        print("Importing image...")
        docker.load_image(filepath)


    def deploy(self, extra_volumes=[], allVolumes=False):
        env = self.envfile()
        docker.deploy(env.image_name, env.container_name, env, extra_volumes, allVolumes)


    def get(self, src, dst):
        docker.copy(self.envfile().container_name + ":" + src, dst)


    def send(self, src, dst):
        docker.copy(src, self.envfile().container_name + ":" + dst)
