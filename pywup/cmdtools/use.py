from pywup.services.preferences import Preferences
from pywup.services.system import Params, colors

import os


def main(cmd, args):
    desc1 = "Name or path of environment file"
    desc2 = "Name or path of cluster file"
    desc3 = "Configure only machines belonging to this remote architecture"

    params = Params(cmd, args)
    params.map("env", 1, None, desc1)
    params.map("cluster", 1, None, desc2)
    params.map("arch", 1, None, desc3)

    params.map("--e", 1, None, desc1)
    params.map("--c", 1, None, desc2)
    params.map("--a", 1, None, desc3)
    params.map("--show", 0, None, "Show what is being used")
    
    if params.run():
        env = params.__e if params.has("--e") else params.env
        cluster = params.__c if params.has("--c") else params.cluster
        arch = params.__a if params.has("--a") else params.arch

        pref = Preferences()

        if env:
            pref.lookup_env(env)
        
        if cluster:
            pref.lookup_cluster(cluster)
        
        if arch:
            pref.arch_name = arch
        
        pref.save()

        if params.__show:
            show = lambda a,b: print(colors.white(a), colors.green(b) if b else colors.red("None"))

            show("env_name:", pref.env_name)
            show("env_filepath:", pref.env_filepath)

            show("cluster_name:", pref.cluster_name)
            show("cluster_filepath:", pref.cluster_filepath)
            
            show("cluster_env_name:", pref.cluster_env_name)
            show("cluster_env_filepath:", pref.cluster_env_filepath)
            
            show("arch_name:", pref.arch_name)
            
