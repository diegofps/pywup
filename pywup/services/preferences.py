from pywup.services.system import error, expand_path
from pywup.services.clusterfile import ClusterFile

import yaml
import os


class Preferences:

    FILEPATH = "~/.wup/preferences.yaml"

    ENV_NAME = "ENV_NAME"
    CLUSTER_NAME = "CLUSTER_NAME"
    CLUSTER_ENV_NAME = "CLUSTER_ENV_NAME"
    ARCH_NAME = "ARCH_NAME"

    ENV_FILEPATH = "ENV_FILEPATH"
    CLUSTER_FILEPATH = "CLUSTER_FILEPATH"
    CLUSTER_ENV_FILEPATH = "CLUSTER_ENV_FILEPATH"


    def __init__(self):
        self.reload()


    def reload(self, filepath=None):
        try:
            if filepath is None:
                filepath = Preferences.FILEPATH
                
            with open(filepath, "r") as fin:
                self.data = yaml.load(fin, Loader=yaml.FullLoader)
        except FileNotFoundError:
            self.data = {}


    def save(self, filepath=None):
        if filepath is None:
            filepath = Preferences.FILEPATH
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as fout:
            yaml.dump(self.data, fout, default_flow_style=False)


    def lookup_cluster(self, name):
        if name == "-":
            self.cluster_name = None
            self.cluster_filepath = None
            return
        
        candidate = expand_path(name)

        if not os.path.exists(candidate):
            candidate = expand_path("./" + name + ".cluster")
            if not os.path.exists(candidate):
                error("Could not find a cluster definition for:", name)
        else:
            name = os.path.splitext(os.path.basename(name))[0]
        
        if "__" in name:
            error("Cluster names must not contain two consecutive underscores (__)")

        if name == "temp":
            error("You cannot use a cluster named temp")
        
        cluster = ClusterFile(candidate)

        if cluster.docker_based:
            self.cluster_name = name
            self.cluster_filepath = candidate
            self.cluster_env_name = cluster.env_name
            self.cluster_env_filepath = cluster.env_filepath

        else:
            self.cluster_name = name
            self.cluster_filepath = candidate
            self.cluster_env_name = None
            self.cluster_env_filepath = None

        


    def lookup_env(self, name):
        if name == "-":
            self.env_name = None
            self.env_filepath = None
            return

        candidate = expand_path(name)

        if not os.path.exists(candidate):
            candidate = expand_path("./" + name + ".env")
            if not os.path.exists(candidate):
                candidate = expand_path("~/.wup/envs/" + name + "/" + name + ".env")
                if not os.path.exists(candidate):
                    error("Could not find an env declaration for:", name)
        else:
            name = os.path.splitext(os.path.basename(name))[0]
        
        if "__" in name:
            error("Names must not contain two consecutive underscores (__)")

        if name == "temp":
            error("You cannot use an env named temp")
        
        self.env_name = name
        self.env_filepath = candidate

        
    def update_state(self):
        env_name = self.env_name
        cluster_name = self.cluster_name
        cluster_env = self.cluster_env_name
        arch = self.arch_name

        env_name = env_name if env_name else "-"
        arch = arch if arch else "-"

        if cluster_name:
            if cluster_env:
                remote = cluster_env + "@" + cluster_name
            else:
                remote = cluster_name
        else:
            remote = "-"
        
        state = env_name + "|" + remote + "|" + arch
        
        folderpath = os.path.expanduser("~/.wup")
        os.makedirs(folderpath, exist_ok=True)

        with open(os.path.join(folderpath, "state"), "w") as fout:
            fout.write(state)


class Getter:

    def __init__(self, name, default=None):
        self.default = default
        self.name = name
    
    def __call__(self, other):
        if self.name in other.data:
            return other.data[self.name]
        else:
            return self.default


class Setter:

    def __init__(self, name):
        self.name = name
    
    def __call__(self, other, value):
        other.data[self.name] = value


def __propertify(key):
    return property(Getter(key), Setter(key))


Preferences.env_name = __propertify(Preferences.ENV_NAME)
Preferences.cluster_name = __propertify(Preferences.CLUSTER_NAME)
Preferences.cluster_env_name = __propertify(Preferences.CLUSTER_ENV_NAME)
Preferences.arch_name = __propertify(Preferences.ARCH_NAME)

Preferences.env_filepath = __propertify(Preferences.ENV_FILEPATH)
Preferences.cluster_filepath = __propertify(Preferences.CLUSTER_FILEPATH)
Preferences.cluster_env_filepath = __propertify(Preferences.CLUSTER_ENV_FILEPATH)
