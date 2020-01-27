from pywup.services.system import error, run, colors, quote_single
from pywup.services.clusterfile import ClusterFile
from pywup.services.docker import expand_path
from pywup.services.context import Context

import os

def show_output(status, rows, i):
    result = colors.green("SUCCESS") if status == 0 else colors.yellow("ERROR")

    print("[%s] %s" % (colors.blue(str(i)), result))

    for line in rows:
        print(line)

def parse_dirs(volumes):
    v = [x.strip() for x in volumes]
    v = [x.split(":")[0] for x in volumes if x]
    v = [expand_path(x) for x in volumes if x]
    return set(v)

def clear_env(env, machines):
    print("Cleaning envs...")
    for i, m in enumerate(machines):
        env_name = env.name
        basename = os.path.basename(env.filepath)
        credential = m.credential

        cmd = "ssh %s 'rm \"$HOME/.wup/envs/%s/%s\"'" % (credential, env_name, basename)
        status, rows = run(cmd, read=True)
        show_output(status, rows, i)


def clear_images(env, machines):
    error("Not implemented yet")

def clear_dirs(env, machines, dirs):
    error("Not implemented yet")

def send_env(env, machines):
    print("Sending envs...")
    for i, m in enumerate(machines):
        filepath = env.filepath
        credential = m.credential
        env_name = env.name
        basename = os.path.basename(env.filepath)
        
        cmd = "ssh %s \"mkdir -p ~/.wup/envs/%s\"" % (credential, env_name)
        status, _ = run(cmd, read=True)

        cmd = "scp %s %s:~/.wup/envs/%s/%s " % (filepath, credential, env_name, basename)
        status, rows = run(cmd, read=True)
        show_output(status, rows, i)

def send_image(env, machines):
    error("Not implemented yet")

def send_dirs(env, machines, dirs):
    error("Not implemented yet")


class Virtual(Context):

    def __init__(self):
        Context.__init__(self)
    

    def sync(self, build=False, deploy=False, clear=False, env=False, image=False, build_volumes=False, deploy_volumes=False, extra_dirs=[]):
        
        env = self.envfile()
        cluster = self.clusterfile()
        arch = self.pref.arch_name

        dirs = set(extra_dirs)
        if build_volumes:
            dirs = dirs.union(parse_dirs(env.build_volumes))
        if deploy_volumes:
            dirs = dirs.union(parse_dirs(env.deploy_volumes))

        machines = set()
        if build:
            machines = machines.union(set(cluster.build_machines(arch)))
        if deploy:
            machines = machines.union(set(cluster.deploy_machines(arch)))

        if not machines:
            error("This cluster is empty (name=%s, arch=%s)" % cluster.name, arch)
        
        if clear:
            if env:
                clear_env(env, machines)
            
            if image:
                clear_images(env, machines)
            
            if dirs:
                clear_dirs(env, machines, dirs)
        else:
            if env:
                send_env(env, machines)
            
            if image:
                send_image(env, machines)
            
            if dirs:
                send_dirs(env, machines, dirs)


    def build(self, doSync, extra_volumes):
        env = self.envfile()
        cluster = self.clusterfile()


    def deploy(self, doSync, extra_volumes):
        env = self.envfile()
        cluster = self.clusterfile()


    def start(self, doClean):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def stop(self, doClean):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def open(self, name):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def launch(self):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def exec(self, cmd):
        env = self.envfile()
        cluster = self.clusterfile()
    

    def run(self, command):
        env = self.envfile()
        cluster = self.clusterfile()
    
