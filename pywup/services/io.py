from pywup.services.system import error, expand_path, colors

import yaml
import os


class Preferences:

    FILEPATH = expand_path("~/.wup/preferences.yaml")

    ENV_NAME = "ENV_NAME"
    CLUSTER_NAME = "CLUSTER_NAME"
    CLUSTER_ENV_NAME = "CLUSTER_ENV_NAME"
    ARCH_NAME = "ARCH_NAME"

    ENV_FILEPATH = "ENV_FILEPATH"
    CLUSTER_FILEPATH = "CLUSTER_FILEPATH"
    CLUSTER_ENV_FILEPATH = "CLUSTER_ENV_FILEPATH"

    FILTER_ARCHS = "FILTER_ARCHS"
    FILTER_NAMES = "FILTER_NAMES"
    FILTER_TAGS = "FILTER_TAGS"
    FILTER_PARAMS = "FILTER_PARAMS"


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
        
        self.update_state()

        
    def update_state(self):
        env_name = self.env_name
        cluster_name = self.cluster_name
        cluster_env = self.cluster_env_name

        filter_params = self.filter_params
        filter_archs = self.filter_archs
        filter_names = self.filter_names
        filter_tags = self.filter_tags

        env_name = env_name if env_name else "-"

        if cluster_name:
            if cluster_env:
                remote = cluster_env + "@" + cluster_name
            else:
                remote = cluster_name
            
            if filter_archs:
                remote += ".a[%s]" % ",".join(filter_archs)
            
            if filter_tags:
                remote += ".t[%s]" % ",".join(filter_tags)

            if filter_params:
                remote += ".p[%s]" % ",".join([key + "=" + value for key, value in filter_params])
            
            if filter_names:
                remote += ".n[%s]" % ",".join(filter_names)
            
        else:
            remote = "-"
        
        state = env_name + "|" + remote
        
        folderpath = os.path.expanduser("~/.wup")
        os.makedirs(folderpath, exist_ok=True)

        with open(os.path.join(folderpath, "state"), "w") as fout:
            if not cluster_name:
                fout.write(colors.purple(state))

            elif cluster_env:
                fout.write(colors.purple(state))

            else:
                fout.write(colors.cyan(state))


class Getter:

    def __init__(self, name, default=None):
        self.default = default
        self.name = name
    
    def __call__(self, other):
        if not self.name in other.data:
            other.data[self.name] = self.default
        return other.data[self.name]


class Setter:

    def __init__(self, name):
        self.name = name
    
    def __call__(self, other, value):
        other.data[self.name] = value


def __propertify(key, default=None):
    return property(Getter(key, default=default), Setter(key))


Preferences.env_name = __propertify(Preferences.ENV_NAME)
Preferences.cluster_name = __propertify(Preferences.CLUSTER_NAME)
Preferences.cluster_env_name = __propertify(Preferences.CLUSTER_ENV_NAME)
Preferences.arch_name = __propertify(Preferences.ARCH_NAME)

Preferences.env_filepath = __propertify(Preferences.ENV_FILEPATH)
Preferences.cluster_filepath = __propertify(Preferences.CLUSTER_FILEPATH)
Preferences.cluster_env_filepath = __propertify(Preferences.CLUSTER_ENV_FILEPATH)

Preferences.filter_archs = __propertify(Preferences.FILTER_ARCHS, default=[])
Preferences.filter_names = __propertify(Preferences.FILTER_NAMES, default=[])
Preferences.filter_tags = __propertify(Preferences.FILTER_TAGS, default=[])
Preferences.filter_params = __propertify(Preferences.FILTER_PARAMS, default=[])
