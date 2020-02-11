from pywup.services.system import error, rprint, WupError
from pywup.services.docker import get_container_ip
from pywup.services.envfile import EnvFile
from pywup.services.io import Preferences
from pywup.services.system import run

import copy
import yaml
import re


class Machine:

    def __init__(self):
        self.tags = []
        self.params = {}
        self.hostname = ""
        self.procs = 1
        self.user = None
        self.port = 22
        self._credential = None
        self.build = True
        self.deploy = True

    def init_from(self, y):
        if "hostname" in y:
            self.hostname = y["hostname"]
        else:
            error("Missing mandatory field in Machine definition: hostname")
        
        if "tags" in y:
            self.tags = y["tags"]
        if "params" in y:
            self.params = y["params"]
        if "procs" in y:
            self.procs = y["procs"]
        if "user" in y:
            self.user = y["user"]
        if "port" in y:
            self.port = y["port"]
        if "build" in y:
            self.build = y["build"]
        if "deploy" in y:
            self.deploy = y["deploy"]

    
    def add_tag(self, name):
        self.tags.append(name)


    def add_param(self, key, value):
        self.params[key] = value


    @property
    def dict(self):
        data = copy.copy(self.__dict__)
        del data["_credential"]
        return data

    
    @property
    def credential(self):
        if self._credential is None:
            if self.user is None:
                self._credential = self.ip
            else:
                self._credential = self.user + "@" + self.ip

        return self._credential
    
    @property
    def ip(self):
        if self.hostname.startswith("wclus__"):
            return get_container_ip(self.hostname)
        else:
            return self.hostname
            


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
        self.env_filepath = None
        self.env_name = None
        self.archs = {}
        self.machines = {}
        self.__env = None

    def build_machines(self, arch=None):
        result = []

        if arch:
            archs = dict()
            archs[arch] = self.archs[arch]
        else:
            archs = self.archs

        for arch_name in archs:
            machines = archs[arch_name]
            build_machine = None

            for machine_name in machines:
                m = machines[machine_name]
                if m.build and (build_machine is None or build_machine.procs < m.procs):
                    build_machine = m
            
            if build_machine:
                result.append(build_machine)
            else:
                error("Missing build machine for arch:", arch_name)
        
        return result


    def deploy_machines(self, arch=None):
        result = []

        for arch_name in self.archs:
            if arch is None or arch_name == arch:
                machines = self.archs[arch_name]
                for machine_name in machines:
                    m = machines[machine_name]
                    if m.deploy:
                        result.append(m)
        
        return result


    def all_machines(self, arch=None):
        if arch is None:
            return self.machines.values()
        else:
            return self.archs[arch].values()
    

    def machine(self, name):
        return self.machines[name]


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
        del data["machines"]

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

        for arch_name, y_machines in y["archs"].items():
            for machine_name, y_machine in y_machines.items():
                m = self.create_machine(arch_name, machine_name)
                m.init_from(y_machine)
        
        self.filter_machines()

    
    def filter_machines(self):
        pref = Preferences()

        filter_params = pref.filter_params
        filter_archs = pref.filter_archs
        filter_names = pref.filter_names
        filter_tags = pref.filter_tags

        new_arch = {}
        new_machines = {}
        for arch_name, machines in self.archs.items():
            if filter_archs and not arch_name in filter_archs:
                continue

            for machine_name, machine in machines.items():
                if filter_names and not machine_name in filter_names:
                    continue

                if filter_tags and not any(tag in machine.tags for tag in filter_tags):
                    continue
                
                if filter_params and not any((key in machine.params and machine.params[key] == value) for key, value in filter_params):
                    continue

                if not arch_name in new_arch:
                    new_arch[arch_name] = {}
                
                new_arch[arch_name][machine_name] = machine
                new_machines[machine_name] = machine
        
        self.archs = new_arch
        self.machines = new_machines


    def export(self, filepath):
        with open(filepath, "w") as fout:
            yaml.dump(self.dict, fout, default_flow_style=False)
    

    def create_machine(self, arch_name, machine_name):
        if not arch_name in self.archs:
            self.archs[arch_name] = {}
        
        arch = self.archs[arch_name]

        if not machine_name in arch:
            if machine_name in self.machines:
                error("A machine with this name already exists in another arch")
            
            m = Machine()
            arch[machine_name] = m
            self.machines[machine_name] = m
        
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

