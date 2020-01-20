from pywup.services.general import lookup_cluster, lookup_env, get_image_name, get_container_name, update_state
from pywup.services.system import error, abort, run, colors
from multiprocessing import Pool, cpu_count
from pywup.services.context import Context
from pywup.services import docker

import tqdm
import yaml
import re
import os


class Cluster(Context):

    def __init__(self):
        Context.__init__(self)


    def new(self, clustername, qtt, outfolder):
        self.require(env=True)

        if not docker.exists_image(self.img_name):
            error("You must COMMIT the image first")

        if self.cluster_nodes:
            error("A cluster with this name already exist, remove it first")

        nodes = [get_container_name(self.name, clustername, i) for i in range(qtt)]

        for cont_name in nodes:
            docker.deploy(self.img_name, cont_name, self.e)
        
        data = {
            "local_arch": {
                cont_name : {
                    "tags": ["fakecluster"],
                    "host": "unknown",
                    "user": "unknown",
                    "procs": 1
                } for cont_name in nodes
            }
        }

        outfile = os.path.join(outfolder, clustername + ".cluster")
        with open(outfile, "w") as fout:
            yaml.dump(data, fout)
        
        self.set_cluster(clustername, outfile)
        print("Cluster file written to " + colors.YELLOW + outfile + colors.RESET)

        update_state()
    

    def rm(self):
        self.require(cluster=True)
        docker.rm_container(self.cluster_nodes)

        self.set_cluster("-", "")
        update_state()
    

    def start(self):
        self.require(env=True, cluster=True)
        docker.start_container(self.cluster_nodes, self.e)


    def stop(self):
        self.require(cluster=True)
        docker.stop(self.cluster_nodes)


    def ip(self):
        self.require(cluster=True)
        return docker.get_container_ip(self.cluster_nodes)


    def open(self, node_number):
        self.require(env=True, cluster=True)
        cont_name = get_container_name(self.name, self.cluster, node_number)
        docker.init_and_open(cont_name, self.e.bashrc)
    

    def ls(self):
        docker.ls_clusters()


    def lsn(self):
        self.require(cluster=True)
        docker.ls_cluster_nodes(self.cluster)
