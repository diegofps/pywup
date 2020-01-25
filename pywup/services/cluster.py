from pywup.services.system import error, colors, expand_path
from pywup.services.clusterfile import ClusterFile
from pywup.services.context import Context
from pywup.services import docker

from multiprocessing import Pool, cpu_count

import yaml
import os
import re


class Cluster(Context):

    def __init__(self):
        Context.__init__(self)


    def new(self, clustername, qtt, outfolder):
        env = self.envfile
        
        c = ClusterFile()
        c.name = clustername
        c.docker_based = True
        c.filepath = expand_path(os.path.join(outfolder, clustername + ".cluster"))
        c.env = env

        if not docker.exists_image(env.image_name):
            error("You must COMMIT the image first")

        nodes = [c.container_name(i) for i in range(qtt)]

        for container in nodes:
            docker.deploy(env.image_name, container, env)
        
        arch = c.create_arch("generic")

        for container in nodes:
            m = arch.create_machine(container)
            m.add_tag("fakecluster")
            m.user = "wup"
            m.procs = 1

        c.export(c.filepath)
        
        self.pref.cluster_name = c.name
        self.pref.cluster_filepath = c.filepath
        self.pref.cluster_env_name = c.env.name
        self.pref.cluster_env_filepath = c.env.filepath
        self.pref.save()

        self.pref.update_state()

        print("Cluster file written to", colors.yellow(c.filepath))
    

    def rm(self):
        cluster = self.clusterfile
        docker.rm_container(cluster.docker_nodes)

        self.pref.cluster_name = None
        self.pref.cluster_filepath = None
        self.pref.cluster_env_name = None
        self.pref.cluster_env_filepath = None
        self.pref.save()

        self.pref.update_state()
    

    def start(self):
        cluster = self.clusterfile
        docker.start_container(cluster.docker_nodes, cluster.env, attach=True)


    def stop(self):
        docker.stop(self.clusterfile.docker_nodes)


    def status(self):
        nodes = self.clusterfile.docker_nodes

        names = ["NAME"] + nodes
        ips = ["IP"] + [x[1] for x in docker.get_container_ip(nodes)]
        running = ["RUNNING"] + [str(x) for x in docker.is_container_running(nodes)]

        return [names, ips, running]


    def ip(self):
        return docker.get_container_ip(self.clusterfile.docker_nodes)


    def open(self, node_number):
        cluster = self.clusterfile
        docker.init_and_open(cluster.container_name(node_number), cluster.env.bashrc)
    

    def ls(self):
        docker.ls_clusters()


    def lsn(self):
        docker.ls_cluster_nodes(self.clusterfile.name)

