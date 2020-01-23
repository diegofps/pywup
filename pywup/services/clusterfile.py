from pywup.services.system import error, rprint, WupError

import yaml


class Machine:

    def __init__(self):
        pass


class Arch:

    def __init__(self, data):
        self.machines = []
        pass


class ClusterFile:

    def __init__(self, data=None):
        self.cluster_name = ""
        self.env_filepath = ""
        self.env_name = ""
        self.archs = {}

        try:
            if data is not None:
                if data["version"] == 1:
                    self.importV1(data)
                else:
                    error("Invalid cluster format")
            
        except WupError as e:
            rprint(e.message)


    @staticmethod
    def import_from(filepath):
        with open(filepath, "r") as fin:
            data = yaml.load(fin, Loader=yaml.FullLoader)
            return ClusterFile(data)
        

    def importV1(self, data):
        self.cluster_name = data["cluster_name"]
        self.env_filepath = data["env_filepath"]
        self.env_name = data["env_name"]
        self.archs = { key : Arch(data["archs"]["key"]) for key in data["archs"] }
        

    def exportV1(self, filepath):
        pass

