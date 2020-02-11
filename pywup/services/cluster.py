from pywup.services.system import run, error, quote, colors, expand_path, rprint, yprint, wprint, quote_single
from pywup.services.context import Context, lookup_cluster
from pywup.services.clusterfile import ClusterFile
from pywup.services.pbash import PBash, Term
from pywup.services.io import Preferences
from pywup.services.ssh import BasicSSH

from collections import defaultdict

import copy
import sys
import os



class Cluster(Context):


    def __init__(self):
        Context.__init__(self)


    def use(self, name, archs, names, tags, params):
        pref = Preferences()

        if not name and not archs and not names and not tags and not params:
            print(pref.cluster_filepath)
            return

        if name == "-":
            pref.cluster_name = None
            pref.cluster_filepath = None
            pref.cluster_env_name = None
            pref.cluster_env_filepath = None

            pref.filter_params = None
            pref.filter_archs = None
            pref.filter_names = None
            pref.filter_tags = None
        
        elif name:
            name, filepath, cluster = lookup_cluster(name)

            if cluster.docker_based:
                pref.cluster_name = name
                pref.cluster_filepath = filepath
                pref.cluster_env_name = cluster.env_name
                pref.cluster_env_filepath = cluster.env_filepath

            else:
                pref.cluster_name = name
                pref.cluster_filepath = filepath
                pref.cluster_env_name = None
                pref.cluster_env_filepath = None

        if archs:
            if pref.filter_archs is None:
                pref.filter_archs = []
            items = pref.filter_archs

            for x in archs:
                if x == "-":
                    items.clear()
                elif not x in items:
                    items.append(x)
        
        if names:
            if pref.filter_names is None:
                pref.filter_names = []
            items = pref.filter_names
            
            for x in names:
                if x == "-":
                    items.clear()
                elif not x in items:
                    items.append(x)
        
        if tags:
            if pref.filter_tags is None:
                pref.filter_tags = []
            items = pref.filter_tags

            for x in tags:
                if x == "-":
                    items.clear()
                elif not x in items:
                    items.append(x)

        if params:
            if pref.filter_params is None:
                pref.filter_params = []
            items = pref.filter_params

            for x in params:
                if x == "-":
                    items.clear()
                else:
                    cells = x.strip().split("=")
                    if len(cells) != 2:
                        error("--p only accepts parameters in the format KEY=VALUE")
                    items.append(cells)
        
        pref.save()
        

    
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

        cluster = self.clusterfile()

        for m in cluster.all_machines():
            ssh = BasicSSH(m.user, m.ip, m.port)
            
            if not ssh.install_key():
                ssh_copy_failed.append(m)
            
            status, rows = ssh.run("ls", read=True, suppressError=True)

            if status != 0:
                sanity_check.append(m)

            else:
                # Look for docker
                found_docker = False
                for candidate in ["/usr/local/bin/docker", "/usr/bin/docker", "/bin/docker", "/snap/bin/docker"]:

                    status, _ = ssh.run("%s --version" % candidate, read=True, suppressError=True)
                    if status == 0:
                        found_docker = True
                        break

                if not found_docker:
                    missing_docker.append(m)
                
                # Look for rsync
                status, _ = ssh.run("rsync --version", read=True, suppressError=True)
                if status != 0:
                    missing_rsync.append(m)
                
                # Look for wup
                status, _ = ssh.run("wup", read=True, suppressError=True)
                if status != 0:
                    missing_pywup.append(m)
                
                # Look for docker group
                status, rows = ssh.run("groups", read=True, suppressError=True)
                if status != 0 or not rows or not "docker" in rows[0]:
                    missing_docker_group.append(m)
                
                else:
                    # Look for a working docker command
                    status, _ = ssh.run("docker ps", suppressError=True)
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


