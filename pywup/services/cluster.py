from pywup.services.system import run, error, quote, colors, expand_path
from pywup.services.clusterfile import ClusterFile
from pywup.services.context import Context

import os



class Cluster(Context):

    def __init__(self):
        Context.__init__(self)

    
    def template(self, clustername, outfolder):

        c = ClusterFile()
        c.name = clustername
        c.docker_based = False
        c.filepath = expand_path(os.path.join(outfolder, clustername + ".cluster"))
        i = 1

        for name in ["ryzen1700_0", "ryzen1700_1"]:
            m = c.create_machine("amd64", name)
            m.add_tag("has_gpu")
            m.add_tag("nvidia_1060_3gb_gpu")
            m.add_tag("32gb_ram")
            m.add_tag("ryzen1700")
            m.hostname = "192.168.0." + str(i)
            m.user = "wup"
            m.procs = 16

            i += 1

        for name in ["rasp_0", "rasp_1"]:
            m = c.create_machine("aarch64", name)
            m.add_tag("rasp3")
            m.add_tag("1gb_ram")
            m.hostname = "192.168.0." + str(i)
            m.user = "wup"
            m.procs = 4

            i += 1

        c.export(c.filepath)

        self.pref.cluster_name = clustername
        self.pref.cluster_filepath = c.filepath
        self.pref.cluster_env_name = None
        self.pref.cluster_env_filepath = None
        self.pref.save()


    def ls(self):
        cluster = self.clusterfile()
        archs = ["ARCH"]
        name = ["NAME"]
        credentials = ["CREDENTIAL"]
        procs = ["PROCS"]
        build = ["BUILD"]
        deploy = ["DEPLOY"]

        for arch_name, arch in cluster.archs.items():
            for machine_name, machine in arch.items():
                name.append(machine_name)
                credentials.append(machine.credential)
                archs.append(arch_name)
                procs.append(str(machine.procs))
                build.append(str(machine.build))
                deploy.append(str(machine.deploy))
        
        return [archs, name, credentials, procs, build, deploy]


    def open(self, clustername):
        cluster = self.clusterfile()
        m = cluster.machine(clustername)
        run("ssh " + m.credential)


    def exec(self, cmd_arguments):
        pass


    def send(self, src, dst):
        pass


    def get(self, src, dst):
        pass


    def doctor(self):
        known_hosts = expand_path("~/.ssh/known_hosts")
        id_wup_pub = expand_path("~/.ssh/id_wup.pub")
        id_wup = expand_path("~/.ssh/id_wup")
        cluster = self.clusterfile()

        if not os.path.exists(id_wup) or not os.path.exists(id_wup_pub):
            run("ssh-keygen -t rsa -f \"%s\" -N \"\"" % id_wup, suppressError=True)
            run("chmod 700 %s %s" % (id_wup, id_wup_pub))

        for m in cluster.all_machines():
            credential = m.credential
            ip = m.ip

            print(known_hosts, ip, credential)

            run("ssh-keygen -f \"%s\" -R \"%s\"" % (known_hosts,ip), suppressError=True)
            run("ssh-keyscan \"%s\" >> \"%s\"" % (ip, known_hosts), suppressError=True)
            run("ssh-copy-id -i %s %s" % (id_wup_pub, credential))

