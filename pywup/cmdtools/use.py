from pywup.services.preferences import Preferences
from pywup.services.system import Params

import os


def main(cmd, args):
    desc1 = "Name or path of environment file"
    desc2 = "Name or path of cluster file"
    desc3 = "Handle only machines with this remote architecture"

    params = Params(cmd, args)
    params.map("env", 1, None, desc1)
    params.map("cluster", 1, None, desc2)
    params.map("arch", 1, None, desc3)

    params.map("--env", 1, None, desc1)
    params.map("--cluster", 1, None, desc2)
    params.map("--arch", 1, None, desc3)
    
    if params.run():
        env = params.__env if params.has("--env") else params.env
        cluster = params.__cluster if params.has("--cluster") else params.cluster
        arch = params.__arch if params.has("--arch") else params.arch

        pref = Preferences()

        if env:
            pref.lookup_env(env)
        
        if cluster:
            pref.lookup_cluster(cluster)
        
        if arch:
            pref.arch_name = arch
        
        pref.save()
        pref.update_state()
