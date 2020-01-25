from pywup.services.system import error, rprint, WupError
from pywup.services.envfile import EnvFile
from pywup.services.system import run

import copy
import yaml
import re

class Machine:

    def __init__(self):
        self.tags = []
        self.procs = None
        self.user = None
    
    def add_tag(self, name):
        self.tags.append(name)

    @property
    def dict(self):
        return copy.copy(self.__dict__)


class Arch:

    def __init__(self, data=None):
        self.machines = {}
    
    def create_machine(self, key):
        if not key in self.machines:
            self.machines[key] = Machine()
        return self.machines[key]

    @property
    def dict(self):
        data = copy.copy(self.__dict__)
        
        items = data["machines"]
        data["machines"] = { key:items[key].dict for key in items }

        return data

class ClusterFile:

    def __init__(self, filepath=None):
        self.init_default(filepath)

        if filepath is not None:
            self.init_from_file(filepath)


    def container_name(self, node):
        return "wclus__{}__{}__{}".format(self.name, self.env_name, node)


    def init_default(self, filepath):
        self.name = ""
        self.docker_based = False
        self.filepath = filepath
        self.env_filepath = ""
        self.env_name = ""
        self.archs = {}
        self.__env = None


    @property
    def env(self):
        if self.__env is None:
            self.__env = EnvFile(self.env_name, self.env_filepath)
        return self.__env

    @env.setter
    def env(self, env):
        self.env_filepath = env.filepath
        self.env_name = env.name
        self.__env = env


    @property
    def dict(self):
        data = copy.copy(self.__dict__)
        del data["_ClusterFile__env"]

        items = data["archs"]
        data["archs"] = { key:items[key].dict for key in items }

        return data

    def init_from_file(self, filepath):
        with open(filepath, "r") as fin:
            data = yaml.load(fin, Loader=yaml.FullLoader)
        
        self.name = data["name"]
        self.docker_based = data["docker_based"]
        self.filepath = filepath
        self.env_filepath = data["env_filepath"]
        self.env_name = data["env_name"]

        archs = data["archs"]

        for key in archs:
            self.archs[key] = Arch(archs[key])


    def export(self, filepath):
        with open(filepath, "w") as fout:
            yaml.dump(self.dict, fout, default_flow_style=False)
    

    def create_arch(self, key):
        if not key in self.archs:
            self.archs[key] = Arch()
        return self.archs[key]


    @property
    def docker_nodes(self):
        if not self.docker_based:
            error("This is not a docker cluster")
        
        _, rows = run("docker ps -a", read=True)
        r = re.compile("wclus__" + self.name + "__[a-zA-Z0-9]+__[0-9]+$")
        result = []
        
        for row in rows:
            m = r.search(row)
            if m:
                name = m.group(0)
                result.append(name)

        return result

