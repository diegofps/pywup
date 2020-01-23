from pywup.services.docker import parse_volumes, clean_volumes, expand_volumes
from pywup.services.context import Context


class Remote(Context):

    def __init__(self, other=None):
        Context.__init__(self, other)
    

    def sync_build(self, clear, extra_volumes, send_env_file, send_all_build_volumes, send_all_deploy_volumes):
        self.require(env=True, cluster=True)

        send_volumes = []

        if send_all_build_volumes:
            send_volumes += self.e.build_volumes
        
        if send_all_deploy_volumes:
            send_volumes += self.e.deploy_volumes
        
        send_volumes = clean_volumes(send_volumes)
        extra_volumes = clean_volumes(extra_volumes)
        
        expand_volumes(send_volumes, extra_volumes)

        import pdb; pdb.set_trace()
        
        #self.e.build_volumes
        #ssh remote "mkdir -p ~/.wup/projects/"

        pass


    def sync_deploy(self, clear, dirs, sendEnv, sendAll, sendImage):
        self.require(env=True, cluster=True)
        pass


    def build(self, doSync, extra_volumes):
        self.require(env=True, cluster=True)
        pass


    def deploy(self, doSync, extra_volumes):
        self.require(env=True, cluster=True)
        pass


    def start(self, doClean):
        self.require(env=True, cluster=True)
        pass
    

    def stop(self, doClean):
        self.require(env=True, cluster=True)
        pass
    

    def open(self, name):
        self.require(env=True, cluster=True)
        pass
    

    def launch(self):
        self.require(env=True, cluster=True)
        pass
    

    def run(self, command):
        self.require(env=True, cluster=True)
        pass
    
