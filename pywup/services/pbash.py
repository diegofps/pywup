from pywup.services.system import colors, yprint, wprint, rprint
from collections import defaultdict
from subprocess import Popen

import hashlib
import select
import shlex
import sys
import pty
import os


class Term:

    def __init__(self, name, initrc):
        
        self.name = name
        self.initrc = initrc
        self.master = None
        self.slave = None
        self.popen = None
        self.outputs = []


class PBash:

    def __init__(self, terms, verbose=False):

        self.verbose = verbose
        self.terms = terms
        self.command = "bash"
        
        self.start_secret = b"f897473fkjree78wefkfw89743jurewjlkhwufwe89343f"
        self.print_start_secret_cmd = b"echo '%s'" % self.start_secret
        self.start_secret_n = self.start_secret + b"\r"

        self.stop_secret  = b"odssd894gfmd9023milewjclkwmjiweofjweodwsdji324"
        self.print_stop_secret_cmd = b"echo '%s'" % self.stop_secret
        self.stop_secret_n = self.stop_secret + b"\r"

        for term in terms:
            term.master, term.slave = pty.openpty()
            term.popen = Popen(
                    shlex.shlex(self.command),
                    preexec_fn=os.setsid,
                    stdin=term.slave,
                    stdout=term.slave,
                    stderr=term.slave,
                    universal_newlines=True)
            
        for term in self.terms:
            for line in term.initrc:
                os.write(term.master, line + b"\n")
    

    def parse_pcmd(self, pcmd):
        if pcmd.startswith("help"):
            print("Help")
        
        elif pcmd.startswith("v="):
            cells = pcmd.split("=")
            c = cells[1][0]
            self.verbose = c == "t" or c == "1" or c == "y"
            print("Verbose mode:", self.verbose)

        else:
            rprint("Unknown pbash command: " + pcmd)


    def loop(self):

        import readline

        while True:
            try:
                sys.stdout.write(colors.WHITE)

                rows = []
                first = True

                while True:
                    cmd = input(">> " if first else "").strip()
                    first = False

                    if cmd.endswith("\\"):
                        rows.append(cmd[:-1])
                    else:
                        rows.append(cmd)
                        cmd = "".join(rows)
                        break

                sys.stdout.write(colors.RESET)
                sys.stdout.flush()

                p = cmd.find("##")
                if p != -1:
                    self.parse_pcmd(cmd[p+2:].strip())
                    cmd = cmd[:p]

                if cmd == "":
                    continue

                elif cmd == "exit":
                    break

                else:
                    #self.print_start_secret()
                    self.execute(cmd)
                    #self.print_stop_secret()
                    self.collect_outputs()
                    self.display_outputs_3()
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                os.write(sys.stdout.fileno(), colors.RESET.encode())
                for term in self.terms:
                    print()
                    print("----------------" + term.name + "-----------------")
                    for o in term.outputs:
                        os.write(sys.stdout.fileno(), o)
    
    def print_start_secret(self):

        for term in self.terms:
            os.write(term.master, self.print_start_secret_cmd)

    def execute(self, cmd):
        command = self.print_start_secret_cmd + b" ; " + cmd.encode() + b" ; " + self.print_stop_secret_cmd + b"\n"
        for term in self.terms:
            os.write(term.master, command)

    def print_stop_secret(self):

        for term in self.terms:
            os.write(term.master, self.print_stop_secret_cmd)

    def collect_outputs(self):

        for term in self.terms:
            term.outputs = []

        masters = [t.master for t in self.terms]
        starts  = [1 for _ in self.terms]
        stops   = [1 for _ in self.terms]
        masters.append(sys.stdin)

        while sum(starts) != 0 or sum(stops) != 0:
            r, w, e = select.select(masters, [], [])
        
            if sys.stdin in r:
                d = os.read(sys.stdin.fileno(), 10240)
                for term in self.terms:
                    os.write(term.master, d)

            else:
                for i, term in enumerate(self.terms):
                    if term.master in r:
                        found_start, found_stop = self.parse(term, self.verbose and i==0)

                        if found_start:
                            starts[i] = 0
                        
                        if found_stop:
                            stops[i] = 0
                        
                        break
        
            #print("STARTS", sum(starts), "STOPS", sum(stops))

    def display_outputs_0(self):

        for i, term in enumerate(self.terms):

            print()
            yprint("--- OUTPUT FOR %s ---" % term.name)

            for j, row in enumerate(term.outputs):
                os.write(sys.stdout.fileno(), b"\n[%d]\n" % j)
                os.write(sys.stdout.fileno(), row)
    
    def display_outputs_3(self, verbose=False):

        hash_to_names = defaultdict(list)
        hash_to_outputs = {}

        for i, term in enumerate(self.terms):

            start = None
            stop = None

            for j, row in enumerate(term.outputs):
                if self.start_secret in row:
                    start = j + 1
                
                if stop is None and self.stop_secret_n in row:
                    stop = j

            if start is None:
                start = 0
            
            if stop is None:
                stop = len(term.outputs)
            
            data = term.outputs[start:stop]
            
            m = hashlib.md5()
            
            for row in data:
                m.update(row)
            
            key = m.digest()
            #name = str(i)
            name = term.name

            hash_to_names[key].append(name)
            if not key in hash_to_outputs:
                hash_to_outputs[key] = data

        print()
        first = True
        for key, data in hash_to_outputs.items():
            names = hash_to_names[key]

            if first:
                first = False
            else:
                print()
            
            if len(hash_to_outputs) == 1:
                yprint("[ALL]")
            else:
                yprint("[%s]" % ", ".join(names))

            for row in data:
                os.write(sys.stdout.fileno(), row)


    def parse(self, term, verbose):
        
        o = os.read(term.master, 10240)

        if verbose:
            os.write(sys.stdout.fileno(), o)

        if not o:
            return False, False
        
        last = 0
        i = 0

        linebreak = ord('\n')
        result = []

        while i != len(o):
            if o[i] == linebreak:
                result.append(o[last:i+1])
                last = i + 1
            
            i += 1
        
        result.append(o[last:i])

        if term.outputs:
            term.outputs[-1] = term.outputs[-1] + result[0]
            term.outputs.extend(result[1:])
        
        else:
            term.outputs.extend(result)

        found_start = False
        found_stop = False

        for row in result:
            if self.start_secret_n in row:
                found_start = True
            
            if self.stop_secret_n in row:
                found_stop = True
        
        return found_start, found_stop
