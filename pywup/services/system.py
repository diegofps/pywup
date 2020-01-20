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


def wprint(*args):
    print(colors.WHITE + " ".join(args) + colors.RESET)


def gprint(*args):
    print(colors.GREEN + " ".join(args) + colors.RESET)


def quote(str):
    return '"' + re.sub(r'([\'\"\\])', r'\\\1', str) + '"'


def quote_single(str):
    return "'" + re.sub(r'([\'\"\\])', r'\\\1', str) + "'"


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
            status = os.system(cmds[0])

            if not suppressError and status != 0:
                error("Failed to execute command", " | ".join(cmds))
            
            return status, None
        
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

    def __init__(self, name, cb, description, parent=None):
        self.parent = parent
        self.name = name
        self.cb = cb
        self.description = description


class Route:

    def __init__(self, arg, parent=None):
        if type(parent) is str:
            parent = RouteCmd(parent, None, None, None)
        
        self.args = arg if type(arg) is Args else Args(arg)
        self.parent = parent
        self.cmds = {}

    def map(self, name, cb, description):
        if name in self.cmds:
            error(name + " is already in use")
        
        self.cmds[name] = RouteCmd(name, cb, description, self.parent)

    def run(self, handleError=False):
        try:
            if not self.args.has_parameter():
                return self.help()
            
            name = self.args.pop_parameter()

            if name in self.cmds:
                r = self.cmds[name]
                return r.cb(r, self.args)

            elif name == "--help":
                return self.help()
            
            else:
                error("Invalid command:", name)

        except WupError as e:
            if handleError:
                abort(colors.RED + "Error: "+ e.message + colors.RESET)
            else:
                raise e
    
    def help(self):
        wprint("Available Commands:\n")

        l = max([len(x) for x in self.cmds])
        for key in self.cmds:
            print("  " + colors.WHITE + key + colors.RESET + " " * (l-len(key)) + " - " + self.cmds[key].description)


class ParamsItem:
    
    def __init__(self, name, length, default, description, mandatory):
        self.name = name
        self.default = default
        self.description = description
        self.mandatory = mandatory
        self.value = default
        self.received_values = []
        self.length = length


    def set(self, value):
        self.received_values.append(value)
    

    def has(self):
        if self.received_values:
            return True
        
        else:
            return False


    def get(self):
        if self.received_values:
            return self.received_values[-1]
        
        elif self.mandatory:
            error("Missing parameter:", self.name)
        
        else:
            return self.default
    

    def get_all(self):
        if self.mandatory and not self.received_values:
            error("Missing parameter:", self.name)
        else:
            return self.received_values


class Params:

    def __init__(self, cmd, args, limit_parameters=True):
        self.parent = cmd
        self.name = args.last
        self.args = args
        self.input_parameters = []
        self.parameters = []
        self.names = {}
        self.limit_parameters = limit_parameters

    def map(self, name, n, default, description, mandatory=False):
        item = ParamsItem(name, n, default, description, mandatory)
        self.names[name] = item

        if not name.startswith("--"):
            self.parameters.append(item)
    

    def help(self):
        options = [self.names[key] for key in self.names if self.names[key].name.startswith("--")]
        arguments = self.parameters

        names = []
        current = self.parent
        while current is not None:
            names.append(current.name)
            current = current.parent
        names.reverse()
        name = " ".join(names)

        if self.parent:
            wprint("DESCRIPTION:")
            print("    " + self.parent.description)
            print()

        wprint("SINTAX:")

        if arguments and options:
            print("    " + name + colors.GREEN + " " + " ".join(["[" + x.name + "]" for x in self.parameters]) + colors.YELLOW + " {OPTIONS}" + colors.RESET)
        
        elif arguments:
            print("    " + name + colors.GREEN + " " + " ".join(["[" + x.name + "]" for x in self.parameters]) + colors.RESET)

        elif options:
            print("    " + name + colors.YELLOW + " {OPTIONS}" + colors.RESET)
        
        else:
            print("    " + name)

        if arguments:
            print()
            wprint("ARGUMENTS:")

            l = max([len(x.name) for x in arguments])
            for x in arguments:
                print("    " + colors.GREEN + x.name + colors.RESET + " " * (l-len(x.name)) + " - " + x.description)
        
        if options:
            print()
            wprint("OPTIONS:")

            l = max([len(x.name) for x in options])
            for x in options:
                print("    " + colors.YELLOW + x.name + colors.RESET + " " * (l-len(x.name)) + " - " + x.description)
        
        print()


    def run(self):
        while self.args.has_next():
            if self.args.has_cmd():
                name = self.args.pop_cmd()

                if name in self.names:
                    item = self.names[name]

                    if item.length == 0:
                        values = True
                    elif item.length == 1:
                        values = self.args.pop_parameter()
                    else:
                        values = [self.args.pop_parameter() for _ in range(item.length)]
                    
                    item.set(values)
                
                elif name == "--help":
                    self.help()
                    return False
                
                else:
                    error("Invalid parameter: ", name)
            
            else:
                index = len(self.input_parameters)
                name = self.args.pop_parameter()

                if index < len(self.parameters):
                    self.input_parameters.append(name)
                    self.parameters[index].set(name)

                elif self.limit_parameters:
                    error("Too many parameters")
        
        return True


    def has(self, name):
        if not name in self.names:
            error("Unknown parameter:", name)
        
        return self.names[name].has()

    def get(self, name):
        if not name in self.names:
            error("Unknown parameter:", name)
        
        return self.names[name].get()
    

    def get_all(self, name):
        if not name in self.names:
            error("Unknown parameter:", name)
        
        return self.names[name].get_all()
    