from pywup.services.system import error, rprint, WupError
from pywup.services.envfile import EnvFile
from pywup.services.system import run

import copy
import yaml
import re

class Machine:

    def __init__(self, y=None):
        self.tags = []
        self.procs = None
        self.user = None

        if y is not None:
            self.tags = y["tags"]
            self.procs = y["procs"]
            self.user = y["user"]
    
    def add_tag(self, name):
        self.tags.append(name)

    @property
    def dict(self):
        return copy.copy(self.__dict__)


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

        archs = data["archs"]

        for arch_name in archs:
            arch = archs[arch_name]
            for machine_name in arch:
                arch[machine_name] = arch[machine_name].dict

        return data

    def init_from_file(self, filepath):
        with open(filepath, "r") as fin:
            y = yaml.load(fin, Loader=yaml.FullLoader)
        
        self.name = y["name"]
        self.docker_based = y["docker_based"]
        self.filepath = filepath
        self.env_filepath = y["env_filepath"]
        self.env_name = y["env_name"]

        y_archs = y["archs"]

        for arch_name in y_archs:
            arch = {}
            self.archs[arch_name] = arch
            y_machines = y_archs[arch_name]

            for machine_name in y_machines:
                y_machine = y_machines[machine_name]
                arch[machine_name] = Machine(y_machine)


    def export(self, filepath):
        with open(filepath, "w") as fout:
            yaml.dump(self.dict, fout, default_flow_style=False)
    

    def create_machine(self, arch_name, machine_name):
        if not arch_name in self.archs:
            self.archs[arch_name] = {}
        
        arch = self.archs[arch_name]

        if not machine_name in arch:
            arch[machine_name] = Machine()
        
        return arch[machine_name]


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

