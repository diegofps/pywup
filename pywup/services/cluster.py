from pywup.services.general import lookup_cluster, lookup_env, get_container_name, update_state
from pywup.services.system import error, run, colors
from multiprocessing import Pool, cpu_count
from pywup.services.context import Context
from pywup.services import docker

import yaml
import os


class Cluster(Context):

    def __init__(self):
        Context.__init__(self)


    def new(self, clustername, qtt, outfolder):
        self.require(env=True)

        if not docker.exists_image(self.img_name):
            error("You must COMMIT the image first")

        if self.cluster_nodes:
            error("A cluster with this name already exists, remove it first")

        nodes = [get_container_name(self.name, clustername, i) for i in range(qtt)]

        for container in nodes:
            docker.deploy(self.img_name, container, self.e)
        
        data = {
            "env": self.name,
            "env_filepath": self.filepath,
            "cluster_name": clustername,
            "archs": {
                "local_arch": {
                    container : {
                        "tags": ["fakecluster"],
                        "user": "wup",
                        "procs": 1
                    } for container in nodes
                }
            }
        }

        c = ClusterFile()
        c.env = self.name
        c.env_filepath = self.filepath
        c.cluster = clustername
        c.cluster_filepath = os.path.join(outfolder, clustername + ".cluster")

        arch = c.create_arch("generic")

        for container in nodes:
            m = arch.create_machine(container)
            m.add_tag("fakecluster")
            m.user = "wup"
            m.procs = 1

        with open(c.cluster_filepath, "w") as fout:
            yaml.dump(data, fout)
        
        self.set_cluster(clustername, outfile, self.name, self.filepath)
        print("Cluster file written to", colors.yellow(outfile))

        update_state()
    

    def rm(self):
        self.require(cluster=True)
        docker.rm_container(self.cluster_nodes)

        self.set_cluster("-", "", "-", "")
        update_state()
    

    def start(self):
        self.require(env=True, cluster=True)
        docker.start_container(self.cluster_nodes, self.e, attach=True)


    def stop(self):
        self.require(cluster=True)
        docker.stop(self.cluster_nodes)


    def status(self):
        self.require(cluster=True)

        names = ["NAME"] + self.cluster_nodes
        ips = ["IP"] + [x[1] for x in docker.get_container_ip(self.cluster_nodes)]
        running = ["RUNNING"] + [str(x) for x in docker.is_container_running(self.cluster_nodes)]

        return [names, ips, running]


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
