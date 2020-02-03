from pywup.services.system import error, run, abort, WupError, expand_path, colors, filename
from pywup.services.clusterfile import ClusterFile
from pywup.services.envfile import EnvFile
from pywup.services.io import Preferences

import re
import os


class Context:

    def __init__(self):
        self.pref = Preferences()
        self.__clusterfile = None
        self.__envfile = None


    def envfile(self):
        if self.__envfile is None:
            env_name = self.pref.env_name
            env_filepath = self.pref.env_filepath

            if env_name is None or env_filepath is None:
                error("You must select an env file first: wup use --e <ENV_NAME_OR_PATH>")
            
            self.__envfile = EnvFile(env_name, env_filepath)
        
        return self.__envfile


    def docker_clusterfile(self):
        return self.clusterfile(docker=True)
    
    
    def clusterfile(self, docker=False):
        if self.__clusterfile is None:
            filepath = self.pref.cluster_filepath

            if filepath is None:
                error("You must select a cluster file first: wup use --c <CLUSTER_NAME_OR_PATH>")
            
            self.__clusterfile = ClusterFile(filepath)

            if docker and not self.__clusterfile.docker_based:
                error("This is not a docker cluster")
            
        return self.__clusterfile
    
