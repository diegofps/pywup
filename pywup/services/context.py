from pywup.services.system import error, run, abort, WupError, expand_path, colors, filename
from pywup.services.preferences import Preferences
from pywup.services.clusterfile import ClusterFile
from pywup.services.envfile import EnvFile

import re
import os


class Context:

    def __init__(self):
        self.pref = Preferences()
        self.__clusterfile = None
        self.__envfile = None


    @property
    def envfile(self):
        if self.__envfile is None:
            self.__envfile = EnvFile(self.pref.env_name, self.pref.env_filepath)
        return self.__envfile


    @property
    def clusterfile(self):
        if self.__clusterfile is None:
            self.__clusterfile = ClusterFile(self.pref.cluster_filepath)
        return self.__clusterfile
    
