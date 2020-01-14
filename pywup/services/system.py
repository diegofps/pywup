from subprocess import Popen, PIPE

import shlex
import sys
import re
import os


class colors:
    RESET="\033[0m"
    RED="\033[1;31m"
    GREEN="\033[1;32m"
    BLUE="\033[1;34m"
    YELLOW="\033[1;33m"
    PURPLE="\033[1;35m"
    CYAN="\033[1;36m"
    WHITE="\033[1;37m"


def expand_path(filepath):
    if not filepath:
        return filepath
    
    if filepath.startswith("/"):
        return filepath
    
    if filepath.startswith("./") or filepath.startswith("../"):
        return os.path.abspath(filepath)
    
    if filepath.startswith("~"):
        return os.path.expanduser(filepath)
    
    return os.path.abspath(os.path.join(".", filepath))


def yprint(*args):
    print(colors.YELLOW + " ".join(args) + colors.RESET)


def quote(str):
    return '"' + re.sub(r'([\'\"\\])', r'\\\1', str) + '"'


def run(cmds, write=None, read=False, suppressInterruption=False, suppressError=False):
    if type(cmds) is not list:
        cmds = [cmds]
    
    if not cmds:
        return
    
    try:
        if write and read:
            args = shlex.split(cmds[0])
            ps = [Popen(args, stdout=PIPE, stdin=PIPE)]

            for i in range(1, len(cmds)):
                args = shlex.split(cmds[i])
                previous = ps[i-1]
                current = Popen(args, stdout=PIPE, stdin=previous.stdout)
                ps.append(current)

            front = ps[0]
            for line in write:
                front.stdin.write(line.encode())
            front.stdin.close()

            back = ps[-1]
            lines = [line.decode("utf-8") for line in back.stdout]
            status = back.wait()

            if not suppressError and status != 0:
                error("Failed to execute command", " | ".join(cmds))
            
            return status,lines

        elif write:
            args = shlex.split(cmds[0])

            if len(cmds) == 1:
                ps = [Popen(args, stdin=PIPE)]
            else:
                ps = [Popen(args, stdout=PIPE, stdin=PIPE)]

            final = len(cmds) - 1
            for i in range(1, final):
                args = shlex.split(cmds[i])
                previous = ps[i-1]

                if i + 1 == final:
                    ps.append(Popen(args, stdin=previous.stdout))
                else:
                    ps.append(Popen(args, stdout=PIPE, stdin=previous.stdout))

            front = ps[0]
            for line in write:
                front.stdin.write(line.encode())
            front.stdin.close()

            status = ps[-1].wait()

            if not suppressError and status != 0:
                error("Failed to execute command", " | ".join(cmds))
            
            return status, None

        elif read:
            args = shlex.split(cmds[0])
            ps = [Popen(args, stdout=PIPE)]

            for i in range(1, len(cmds)):
                args = shlex.split(cmds[i])
                previous = ps[i-1]
                current = Popen(args, stdout=PIPE, stdin=previous.stdout)
                ps.append(current)

            back = ps[-1]
            lines = [line.decode("utf-8") for line in back.stdout]
            status = back.wait()

            if not suppressError and status != 0:
                error("Failed to execute command", " | ".join(cmds))
            
            return status, lines

        elif len(cmds) == 1:
            return os.system(cmds[0]), None
        
        else:
            args = shlex.split(cmds[0])
            ps = [Popen(args, stdout=PIPE)]

            for i in range(1, len(cmds)-1):
                args = shlex.split(cmds[i])
                previous = ps[i-1]
                current = Popen(args, stdout=PIPE, stdin=previous.stdout)
                ps.append(current)

            args = shlex.split(cmds[-1])
            previous = ps[-1]
            current = Popen(args, stdin=previous.stdout)
            ps.append(current)

            status = ps[-1].wait()
            
            if not suppressError and status != 0:
                error("Failed to execute command", " | ".join(cmds))
            
            return status, None

    except KeyboardInterrupt as e:
        if not suppressInterruption:
            raise e


class WupError(Exception):
    def __init__(self, message=None):
        self.message = message


def abort(*args):
    if args:
        print(*args, file=sys.stderr)
    exit(1)


def error(*args):
    if args:
        raise WupError(" ".join(args))
    else:
        raise WupError()


class Args:
    
    def __init__(self, args):
        self.args = args
        self.current = 0
        self.last = None
    
    def all(self):
        return self.args[self.current:]
    
    def has_parameter(self):
        return self.has_next() and not self.args[self.current].startswith("--")
    
    def has_cmd(self):
        return self.has_next() and self.args[self.current].startswith("--")
    
    def has_next(self):
        return self.current < len(self.args)
    
    def sneak(self):
        return None if self.current == len(self.args) else self.args[self.current]
    
    def pop(self):
        if self.current == len(self.args):
            raise RuntimeError("No more arguments to pop")
        
        v = self.args[self.current]
        self.current += 1
        self.last = v
        return v
    
    def pop_parameter(self, cb=None):
        if self.has_parameter():
            return self.pop()
        
        elif cb:
            cb(self.last)
        
        else:
            raise RuntimeError("Wrong argument, expecting a parameter")
    
    def pop_cmd(self):
        if not self.has_cmd():
            raise RuntimeError("Wrong argument, expecting a command: ", self.sneak())
        return self.pop()


def read_csv(filepath):
    import numpy as np
    import csv

    with open(filepath, "r") as fin:
        reader = csv.reader(fin, delimiter=';')
        data = [cells for cells in reader]
        return np.array(data, dtype=object)


class RouteCmd:

    def __init__(self, cmd, cb, description):
        self.cmd = cmd
        self.cb = cb
        self.description = description


class Route:

    def __init__(self, arg):
        self.args = arg if type(arg) is Args else Args(arg)
        self.cmds = {}

    def map(self, cmd, cb, description):
        if cmd in self.cmds:
            error(cmd + " is already in use")
        
        self.cmds[cmd] = RouteCmd(cmd, cb, description)

    def run(self, handleError=False):
        try:
            if not self.args.has_parameter():
                print("Available commands:\n")
                return self.help()
            
            cmd = self.args.pop_parameter()

            if cmd == "help":
                return self.help()
            
            elif cmd in self.cmds:
                return self.cmds[cmd].cb(self.args)

            else:
                error("Invalid command:", cmd)

        except WupError as e:
            if handleError:
                abort(colors.RED + "Error: "+ e.message + colors.RESET)
            else:
                raise e
    
    def help(self):
        l = max([len(x) for x in self.cmds])
        for key in self.cmds:
            print("  " + key + " " * (l-len(key)) + " - " + self.cmds[key].description)
