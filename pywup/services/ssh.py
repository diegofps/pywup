from pywup.services.system import run, expand_path, quote_single

import os


known_hosts = expand_path("~/.ssh/known_hosts")
id_wup_pub = expand_path("~/.ssh/id_rsa.pub")
id_wup = expand_path("~/.ssh/id_rsa")


class BasicSSH:

    def __init__(self, user, ip, port=None):

        self.credential = ip
        self.port = port
        self.user = user
        self.ip = ip

        if user:
            self.credential = user + "@" + self.credential
        
        if port:
            self.credential = self.credential + ":" + self.port

        self.assert_key_exists()


    def assert_key_exists(self):

        if not os.path.exists(id_wup) or not os.path.exists(id_wup_pub):
            run("ssh-keygen -t rsa -f \"%s\" -N \"\"" % id_wup, suppressError=True, read=True)
            run("chmod 700 %s %s" % (id_wup, id_wup_pub), read=True, suppressError=True)


    def install_key(self):

        run("ssh-keygen -f \"%s\" -R \"%s\"" % (known_hosts, self.ip), suppressError=True, read=True)
        run("ssh-keyscan \"%s\" >> \"%s\"" % (self.ip, known_hosts), suppressError=True)

        status, _ = run("ssh-copy-id -f -i %s %s" % (id_wup_pub, self.credential), suppressError=True, read=True)

        success = status == 0
        return success


    def command(self, cmd):
        return "ssh -i %s %s %s" % (id_wup, self.credential, quote_single(cmd))


    def run(self, cmd, write=None, read=False, suppressInterruption=False, suppressError=False, verbose=False):

        return run(self.command(cmd), 
                write=write, 
                read=read, 
                suppressInterruption=suppressInterruption, 
                suppressError=suppressError, 
                verbose=verbose)
