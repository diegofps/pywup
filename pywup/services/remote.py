from pywup.services.docker import parse_volumes, clean_volumes, expand_volumes
from pywup.services.context import Context


class Remote(Context):

    def __init__(self):
        Context.__init__(self)
    

    def sync_build(self, clear, extra_volumes, send_env_file, send_all_build_volumes, send_all_deploy_volumes):
        env = self.envfile
        cluster = self.clusterfile

        send_volumes = []

        if send_all_build_volumes:
            send_volumes += env.build_volumes
        
        if send_all_deploy_volumes:
            send_volumes += env.deploy_volumes
        
        send_volumes = clean_volumes(send_volumes)
        extra_volumes = clean_volumes(extra_volumes)
        
        expand_volumes(send_volumes, extra_volumes)

        import pdb; pdb.set_trace()
        
        #self.e.build_volumes
        #ssh remote "mkdir -p ~/.wup/projects/"

        pass


    def sync_deploy(self, clear, dirs, sendEnv, sendAll, sendImage):
        env = self.envfile
        cluster = self.clusterfile
        pass


    def build(self, doSync, extra_volumes):
        env = self.envfile
        cluster = self.clusterfile


    def deploy(self, doSync, extra_volumes):
        env = self.envfile
        cluster = self.clusterfile


    def start(self, doClean):
        env = self.envfile
        cluster = self.clusterfile
    

    def stop(self, doClean):
        env = self.envfile
        cluster = self.clusterfile
    

    def open(self, name):
        env = self.envfile
        cluster = self.clusterfile
    

    def launch(self):
        env = self.envfile
        cluster = self.clusterfile
    

    def run(self, command):
        env = self.envfile
        cluster = self.clusterfile
    
