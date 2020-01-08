from pywup.services.general import lookup_cluster, lookup_env, get_image_name, get_container_name, parse_env, get_open_cmd
from pywup.services.system import error, abort, run
from multiprocessing import Pool, cpu_count
from pywup.services.context import Context
from pywup.services.env import Env

import tqdm
import yaml
import re
import os


class CreateTask:
    def __init__(self, cont_name, volumes, base):
        self.cont_name = cont_name
        self.volumes = volumes
        self.base = base


def get_container_by_cluster_and_node_number(clustername, node_number):
    _, rows = run("docker ps -a -f \"name=wclus__" + clustername + "__*\"", read=True)

    r = re.compile("wclus__" + clustername + "__([a-zA-Z0-9]+)__([0-9]+)\n$")
    
    for row in rows:
        result = r.search(row)
        if result:
            env, number = result.groups()
            if number == node_number:
                idd = row.split(" ", 1)[0]
                return idd, env
    
    return None
 

def parallel_do_new(task):
    cmd1 = "docker rm %s 2> /dev/null" % task.cont_name
    run(cmd1)

    cmd2 = "docker run -i --name {} {} {}".format(task.cont_name, task.volumes, task.base)
    status, _ = run(cmd2, ["exit\n"])

    return status


class Cluster(Context):

    def __init__(self):
        Context.__init__(self)


    def new(self, clustername, qtt, outfolder):
        self.require(env=True)

        if not Env(self).has_img():
            error("You must COMMIT the image first")

        volumes = "-v " + " -v ".join(self.templates["VOLUMES"]) if self.templates["VOLUMES"] else ""

        containers = self.get_containers_in_cluster(clustername)
        if containers:
            error("A cluster with this name already exists, remove it first")

        # Build the tasks
        tasks = []
        for i in range(qtt):
            cont_name = get_container_name(self.name, clustername, i)
            tasks.append(CreateTask(cont_name, volumes, self.img_name))

        # Run in parallel
        print("Creating cluster...")
        jobs = cpu_count()
        result = []

        with Pool(jobs) as p:
            for status in tqdm.tqdm(p.imap(parallel_do_new, tasks), total=len(tasks)):
                result.append(status)
        
        if sum(result) != 0:
            error("Cluster creation has failed, check the output for details")
        
        data = {
            "local_arch": {
                "m" + str(i) : {
                    "tags": ["fakecluster"],
                    "host": "unknown",
                    "user": "unknown",
                    "procs": 1
                } for i in range(qtt)
            }
        }

        outfile = os.path.join(outfolder, clustername + ".cluster")
        with open(outfile, "w") as fout:
            yaml.dump(data, fout)
        
        self.set_cluster(clustername, outfile)
    

    def rm(self):
        self.require(cluster=True)

        ids = " ".join(self.cluster_nodes)

        run("docker kill " + ids)
        run("docker rm " + ids)
    

    def start(self):
        self.require(env=True, cluster=True)

        e = Env(self)
        for n in self.cluster_nodes:
            e.start(n)


    def stop(self):
        self.require(cluster=True)
        run("docker kill " + " ".join(self.cluster_nodes))


    def ip(self):
        self.require(cluster=True)
        
        e = Env(self)
        return [(x, e.ip(x)) for x in self.cluster_nodes]


    def open(self, node_number):
        self.require(env=True, cluster=True)
        cont_name = get_container_name(self.name, self.cluster, node_number)
        Env().open(cont_name)
    

    def ls(self, cluster=None):
        if cluster is not None:
            run("docker ps -a -f \"name=wclus__{}__*\"".format(cluster))

        else:
            _, rows = run("docker ps -a -f \"name=wclus__*\"", read=True)
            r = re.compile(r'wclus__([a-zA-Z0-9]+)__([a-zA-Z0-9]+)__([0-9]+)')
            s = [r.search(row) for row in rows]
            res = {}

            for m in s:
                if m:
                    cluster = m.group(1)
                    env = m.group(2)
                    #number = m.group(3)

                    if not cluster in res:
                        res[cluster] = [1, env]
                    else:
                        res[cluster][0] += 1
            
            for cluster in res:
                print("{} [{}, {}]".format(cluster, *res[cluster]))
