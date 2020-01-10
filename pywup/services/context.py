from pywup.services.general import get_image_name, get_container_name, lookup_env, lookup_cluster, update_state, get_export_filepath
from pywup.services.system import error, run, abort, WupError, expand_path
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

            return
        
        try:
            self.name = conf.get("wup.env_name", scope="global")
            self.filepath = conf.get("wup.env_filepath", scope="global")
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
            self.cluster = conf.get("wup.cluster_name", scope="global")
            self.cluster_filepath = conf.get("wup.cluster_filepath", scope="global")
            self.cluster_nodes = self.get_containers_in_cluster(self.cluster, False) if self.cluster else []
            self.cluster_env = self.cluster_nodes[0].split("__")[-2] if self.cluster_nodes else None
        
        except (AttributeError, FileNotFoundError):
            self.cluster = ""
            self.cluster_filepath = ""
            self.cluster_nodes = []
            self.cluster_env = None


    def use(self, env, cluster):
        if env is not None:
            env_name, env_filepath = lookup_env(env)
            self.set_env(env_name, env_filepath)

        if cluster is not None:
            cluster_name, cluster_filepath = lookup_cluster(cluster)
            self.set_cluster(cluster_name, cluster_filepath)

        update_state()
    

    def set_env(self, env_name, env_filepath):
        conf.set("wup.env_name", env_name, scope="global")
        conf.set("wup.env_filepath", expand_path(env_filepath), scope="global")


    def set_cluster(self, cluster_name, cluster_filepath):
        conf.set("wup.cluster_name", cluster_name, scope="global")
        conf.set("wup.cluster_filepath", expand_path(cluster_filepath), scope="global")
    

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

