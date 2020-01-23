from pywup.services.context import Context


class Remote(Context):

    def __init__(self, other=None):
        Context.__init__(self, other)
    

    def sync_build(self, doClear, dirs, sendEnv, sendAll):
        self.require(env=True, cluster=True)
        pass


    def sync_deploy(self, doClear, dirs, sendEnv, sendAll, sendImage):
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
    
