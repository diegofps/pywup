from pywup.services.general import get_image_name, get_container_name, lookup_env, lookup_cluster, update_state, get_export_filepath
from pywup.services.system import error, run, abort, WupError, expand_path, colors, filename
from pywup.services.clusterfile import ClusterFile
from pywup.services.envfile import EnvFile
from pywup.services import conf

import re
import os


class Context:

    def __init__(self, other=None):
        self.reload(other)


    def reload(self, other=None):
        if other is not None:
            self.name = other.name
            self.filepath = other.filepath
            self.cont_name = other.cont_name
            self.img_name = other.img_name
            self.e = other.e

            self.cluster = other.cluster
            self.cluster_filepath = other.cluster_filepath
            self.cluster_nodes = []
            self.cluster_env = None
            self.c = other.c

            return
        
        try:
            self.filepath = conf.get("wup.env_filepath", scope="global")
            self.name = filename(self.filepath)
            self.cont_name = get_container_name(self.name)
            self.img_name = get_image_name(self.name)
            self.e = EnvFile(self.name, self.filepath)

        except (AttributeError, FileNotFoundError):
            self.name = ""
            self.filepath = ""
            self.cont_name = None
            self.img_name = None
            self.e = EnvFile()
        
        try:
            self.cluster_filepath = conf.get("wup.cluster_filepath", scope="global")
            self.cluster = filename(self.cluster_filepath)
            self.c = ClusterFile.import_from(self.cluster_filepath)

            self.cluster_nodes = self.get_containers_in_cluster(self.cluster, False) if self.cluster else []
        
        except (AttributeError, FileNotFoundError):
            self.cluster = ""
            self.cluster_filepath = ""
            self.cluster_nodes = []
            self.cluster_env = None
            self.c = ClusterFile()


    def use(self, env, cluster, arch):
        if env is not None:
            env_name, env_filepath = lookup_env(env)
            print("Using environment", colors.yellow(env_name), "found at", colors.yellow(env_filepath))
            self.set_env(env_filepath)

        if cluster is not None:
            _, cluster_filepath = lookup_cluster(cluster)
            c = ClusterFile(cluster_filepath)
            print("Using cluster", colors.yellow(c.cluster_name), "found at", colors.yellow(cluster_filepath))
            self.set_cluster(cluster_filepath)
            self.set_cluster_env(c.env_filepath)

        if arch is not None:
            print("Using arch", arch)
            self.set_arch(arch)

        update_state()
    

    def set_env(self, env_filepath):
        conf.set("wup.env_filepath", expand_path(env_filepath), scope="global")


    def set_cluster(self, cluster_filepath):
        conf.set("wup.cluster_filepath", expand_path(cluster_filepath), scope="global")
    

    def set_cluster_env(self, cluster_env_filepath):
        conf.set("wup.cluster_env_filepath", cluster_env_filepath, scope="global")
    

    def set_arch(self, arch_name):
        conf.set("wup.arch", arch_name, scope="global")
    

    def require(self, env=False, cluster=False):
        if env and not (self.name and self.name != "-"):
            error("You must set an environment first")
        
        if cluster and not (self.cluster and self.cluster != "-"):
            error("You must set a cluster first")
        
        if env and cluster and self.name != self.cluster_env:
            error("This cluster was created from a different environment, please set the proper one")


    def get_containers_in_cluster(self, clustername, abortOnFail=False):
        _, rows = run("docker ps -a", read=True)
        r = re.compile("wclus__" + clustername + "__[a-zA-Z0-9]+__[0-9]+$")
        result = []
        
        for row in rows:
            m = r.search(row)
            if m:
                name = m.group(0)
                result.append(name)

        if abortOnFail and not result:
            error("Cluster not found")

        return result

