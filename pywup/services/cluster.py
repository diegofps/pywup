from pywup.services.system import run, error, quote, colors, expand_path, rprint, yprint, wprint, quote_single
from pywup.services.clusterfile import ClusterFile
from pywup.services.pbash import PBash, Term
from pywup.services.context import Context

from collections import defaultdict

import copy
import sys
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
            m.add_param("ID", str(i))
            m.hostname = "192.168.0." + str(i)
            m.user = "wup"
            m.procs = 16

            i += 1

        for name in ["rasp_0", "rasp_1"]:
            m = c.create_machine("aarch64", name)
            m.add_tag("rasp3")
            m.add_tag("1gb_ram")
            m.add_param("ID", str(i))
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


    def exec_single(self, cmd, m, verbose=True, idd=None):

        if type(m) is str:
            m = self.clusterfile().machine(m)

        if type(cmd) is not list:
            cmd = [cmd]
        
        cmds = quote_single("".join(cmd))

        credential = m.credential
        status, rows = run("ssh %s %s\n" % (credential, cmds), read=True)

        if verbose:
            if status == 0:
                result = colors.green("SUCCESS")
            else:
                result = colors.yellow("FAILED")

            if idd is None:
                print(colors.blue("[%s]" % m.hostname) + " => " + result)
            else:
                print(colors.blue("[%s:%s]" % (idd, m.hostname)) + " => " + result)
            
            sys.stdout.writelines(rows)


    def exec_all(self, cmd, verbose=True):

        cluster = self.clusterfile()

        for i, m in enumerate(cluster.all_machines()):
            self.exec_single(cmd, m, idd=str(i))


    def send_single(self, m, src, dst=None):

        if not os.path.exists(src):
            error("Could not find source file:", src)

        if type(m) is str:
            m = self.clusterfile().machine(m)
        
        if dst is None:
            src = expand_path(src)
            base = os.path.dirname(src)
            dst = src

            create_dir = "mkdir -p \"%s\"" % base
            self.exec_single(create_dir, m=m, verbose=False)

        run("rsync -r \"%s\" \"%s:%s\"" % (src, m.credential, dst))

    
    def send_all(self, src, dst=None):

        cluster = self.clusterfile()

        for m in cluster.all_machines():
            self.send_single(m, src, dst)


    def get_single(self, name, src, dst=None, m=None):

        if m is None:
            m = self.clusterfile().machine(name)
        
        dst = os.path.join(dst, name)
        os.makedirs(dst, exist_ok=True)

        run("rsync -r \"%s:%s\" \"%s/\"" % (m.credential, src, dst))


    def get_all(self, src, dst=None):

        cluster = self.clusterfile()

        for name, m in cluster.machines.items():
            self.get_single(name, src, dst, m=m)


    def pbash(self, verbose):
        cluster = self.clusterfile()
        terms = []
        i = 0

        for name, m in cluster.machines.items():
            params = {}

            params["WUP_ID"] = str(i)
            params["WUP_NAME"] = name
            params["WUP_USER"] = m.user
            params["WUP_PORT"] = m.port
            params["WUP_HOSTNAME"] = m.hostname
            params["WUP_BUILD"] = "1" if m.build else "0"
            params["WUP_DEPLOY"] = "1" if m.deploy else "0"

            for key, value in m.params.items():
                params["PARAM_" + key] = value

            for tag in m.tags:
                params["TAG_" + tag] = "1"

            initrc = [("%s=\"%s\"" % d).encode() for d in params.items()]
            initrc.insert(0, b"ssh " + m.credential.encode())
            
            terms.append(Term(name, initrc))
            i += 1

        PBash(terms, verbose).loop()
    

    def doctor(self):

        sanity_check = []
        missing_docker = []
        missing_rsync = []
        missing_pywup = []
        missing_docker_group = []
        ssh_copy_failed = []
        docker_ps_did_not_work = []

        known_hosts = expand_path("~/.ssh/known_hosts")
        id_wup_pub = expand_path("~/.ssh/id_wup.pub")
        id_wup = expand_path("~/.ssh/id_wup")
        cluster = self.clusterfile()

        if not os.path.exists(id_wup) or not os.path.exists(id_wup_pub):
            run("ssh-keygen -t rsa -f \"%s\" -N \"\"" % id_wup, suppressError=True, read=True)
            run("chmod 700 %s %s" % (id_wup, id_wup_pub), read=True, suppressError=True)

        for m in cluster.all_machines():
            credential = m.credential
            ip = m.ip

            print(known_hosts, ip, credential)

            run("ssh-keygen -f \"%s\" -R \"%s\"" % (known_hosts,ip), suppressError=True, read=True)
            run("ssh-keyscan \"%s\" >> \"%s\"" % (ip, known_hosts), suppressError=True)

            status, rows = run("ssh-copy-id -i %s %s" % (id_wup_pub, credential), suppressError=True, read=True)
            if status != 0:
                ssh_copy_failed.append(m)
            
            status, rows = run("ssh %s \"ls\"" % credential, read=True, suppressError=True)
            if status != 0:
                sanity_check.append(m)

            else:
                found_docker = False
                for candidate in ["/usr/local/bin/docker", "/usr/bin/docker"]:
                    status, rows = run("ssh %s \"%s --version\"" % (credential, candidate), read=True, suppressError=True)
                    if status == 0:
                        found_docker = True
                        break
                if not found_docker:
                    missing_docker.append(m)
                
                status, _ = run("ssh %s \"rsync --version\"" % credential, read=True, suppressError=True)
                if status != 0:
                    missing_rsync.append(m)
                
                status, _ = run("ssh %s \"wup\"" % credential, read=True, suppressError=True)
                if status != 0:
                    missing_pywup.append(m)
                
                status, rows = run("ssh %s \"groups\"" % credential, read=True, suppressError=True)
                if status != 0 or not rows or not "docker" in rows[0]:
                    missing_docker_group.append(m)
                
                else:
                    status, rows = run("ssh %s \"docker ps\"" % credential, suppressError=True)
                    if status != 0:
                        docker_ps_did_not_work.append(m)
        
        print()
        
        self.diagnose("Can't execute simple remote command", sanity_check)
        self.diagnose("ssh-copy-id failed", ssh_copy_failed)
        self.diagnose("Missing docker", missing_docker)
        self.diagnose("Missing docker group", missing_docker_group)
        self.diagnose("Docker ps did not work", docker_ps_did_not_work)
        self.diagnose("Missing rsync", missing_rsync)
        self.diagnose("Missing pywup", missing_pywup)
    
    
    def diagnose(self, diagnostic, items):

        if not items:
            return
        
        rprint(diagnostic)

        for m in items:
            print("    " + m.hostname)

        print()


