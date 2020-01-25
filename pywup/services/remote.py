from pywup.services.docker import parse_volumes, clean_volumes, expand_volumes, expand_path
from pywup.services.clusterfile import ClusterFile
from pywup.services.context import Context

import os

class Remote(Context):

    def __init__(self):
        Context.__init__(self)
    

    def sync_build(self, clear, extra_volumes, send_env_file, send_all_build_volumes, send_all_deploy_volumes):
        env = self.envfile()
        cluster = self.clusterfile()

        send_volumes = []

        if send_all_build_volumes:
            send_volumes += env.build_volumes
        
        if send_all_deploy_volumes:
            send_volumes += env.deploy_volumes
        
        send_volumes = clean_volumes(send_volumes)
        extra_volumes = clean_volumes(extra_volumes)
        
        expand_volumes(send_volumes, extra_volumes)

        import pdb; pdb.set_trace()
        
        #self.e.build_volumes
        #ssh remote "mkdir -p ~/.wup/projects/"

        pass


    def sync_deploy(self, clear, dirs, sendEnv, sendAll, sendImage):
        env = self.envfile()
        cluster = self.clusterfile()
        pass


    def build(self, doSync, extra_volumes):
        env = self.envfile()
        cluster = self.clusterfile()


    def deploy(self, doSync, extra_volumes):
        env = self.envfile()
        cluster = self.clusterfile()


    def start(self, doClean):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def stop(self, doClean):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def open(self, name):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def launch(self):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def run(self, command):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def template(self, clustername, outfolder):

        c = ClusterFile()
        c.name = clustername
        c.docker_based = False
        c.filepath = expand_path(os.path.join(outfolder, clustername + ".cluster"))

        for name in ["ryzen1700_0", "ryzen1700_1"]:
            m = c.create_machine("amd64", name)
            m.add_tag("has_gpu")
            m.add_tag("nvidia_1060_3gb_gpu")
            m.add_tag("32gb_ram")
            m.add_tag("ryzen1700")
            m.user = "wup"
            m.procs = 16

        for name in ["rasp_0", "rasp_1"]:
            m = c.create_machine("aarch64", name)
            m.add_tag("rasp3")
            m.add_tag("1gb_ram")
            m.user = "wup"
            m.procs = 4

        c.export(c.filepath)

        self.pref.cluster_name = clustername
        self.pref.cluster_filepath = c.filepath
        self.pref.cluster_env_name = None
        self.pref.cluster_env_filepath = None
        self.pref.save()
