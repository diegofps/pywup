from pywup.services.general import lookup_cluster, lookup_env, get_image_name, get_container_name, parse_env
from pywup.services.system import error, abort, run
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

        if not docker.exists_img(self.img_name):
            error("You must COMMIT the image first")

        if self.cluster_nodes:
            error("A cluster with this name already exists, remove it first")

        nodes = [get_container_name(self.name, clustername, i) for i in range(qtt)]

        for cont_name in nodes:
            docker.new(self.img_name, cont_name, self.bashrc, self.templates, self.variables)
        
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
    

    def rm(self):
        self.require(cluster=True)
        docker.rm(self.cluster_nodes)
    

    def start(self):
        self.require(env=True, cluster=True)
        docker.start(self.cluster_nodes, self.bashrc, self.templates)


    def stop(self):
        self.require(cluster=True)
        docker.stop(self.cluster_nodes)


    def ip(self):
        self.require(cluster=True)
        return docker.ip(self.cluster_nodes)


    def open(self, node_number):
        self.require(env=True, cluster=True)
        cont_name = get_container_name(self.name, self.cluster, node_number)
        docker.open_and_init(cont_name, self.bashrc)
    

    def ls(self, cluster=None):
        if cluster is None:
            docker.ls_clusters()
        else:
            docker.ls_cluster_nodes(cluster)
