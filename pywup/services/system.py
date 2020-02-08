from subprocess import Popen, PIPE

import shlex
import sys
import re
import os


def filename(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]


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


def print_table(columns):
    lengths = [max([len(x) for x in array]) for array in columns]

    for i, tup in enumerate(zip(*columns)):
        cells = [x + " " * (lengths[i]-len(x)) for i, x in enumerate(tup)]
        
        if i == 0:
            wprint("    ".join(cells))
        else:
            print("    ".join(cells))


def yprint(*args):
    print(colors.YELLOW + " ".join([str(v) for v in args]) + colors.RESET)


def wprint(*args):
    print(colors.WHITE + " ".join([str(v) for v in args]) + colors.RESET)


def gprint(*args):
    print(colors.GREEN + " ".join([str(v) for v in args]) + colors.RESET)


def rprint(*args):
    print(colors.RED + " ".join([str(v) for v in args]) + colors.RESET)

def cprint(*args):
    print(colors.CYAN + " ".join([str(v) for v in args]) + colors.RESET)


def quote(str):
    return '"' + re.sub(r'([\'\"\\])', r'\\\1', str) + '"'


def quote_single(str):
    return "'" + re.sub(r'([\'\\])', r'\\\1', str) + "'"


def run(cmds, write=None, read=False, suppressInterruption=False, suppressError=False, verbose=False):
    if type(cmds) is not list:
        cmds = [cmds]
    
    if not cmds:
        return
    
    if verbose:
        print("Executing command:\n" + " | ".join(cmds))

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
                error("Failed to execute command:\n" + " | ".join(cmds))
            
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
                error("Failed to execute command:\n" + " | ".join(cmds))
            
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
                error("Failed to execute command:\n" + " | ".join(cmds))
            
            return status, lines

        elif len(cmds) == 1:
            status = os.system(cmds[0])

            if not suppressError and status != 0:
                error("Failed to execute command:\n" + " | ".join(cmds))
            
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
                error("Failed to execute command:\n" + " | ".join(cmds))
            
            return status, None

    except KeyboardInterrupt as e:
        if not suppressInterruption:
            raise e


def abort(*args):
    if args:
        print(*args, file=sys.stderr)
    exit(1)


def error(*args):
    if args:
        raise WupError(" ".join(args))
    else:
        raise WupError()


def critical(*args):
    rprint("|CRITICAL|", *args)


def warn(*args):
    yprint("|WARNING|", *args)


def info(*args):
    gprint("|INFO|", *args)


def debug(*args):
    cprint("|DEBUG|", *args)



def readlines(master, lines, verbose=False):
    
    o = os.read(master, 10240)

    if verbose:
        os.write(sys.stdout.fileno(), o)

    if not o:
        return 0, 0
    
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

    start_search = max(len(lines) - 1, 0)

    if lines:
        lines[-1] = lines[-1] + result[0]
        lines.extend(result[1:])
    else:
        lines.extend(result)
    
    return start_search, len(lines)


def read_csv(filepath):
    import numpy as np
    import csv

    with open(filepath, "r") as fin:
        reader = csv.reader(fin, delimiter=';')
        data = [cells for cells in reader]
        return np.array(data, dtype=object)


class WupError(Exception):
    def __init__(self, message=None):
        self.message = message


class colors:
    RESET="\033[0m"

    RESET     = "\033[0m"

    BRIGHTER  = "\033[1m"
    DARKER    = "\033[2m"
    ITALIC    = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINKING  = "\033[5m"
    REVERSE   = "\033[7m"
    INVISIBLE = "\033[8m"
    CROSSING  = "\033[9m"

    GRAY    = "\033[90m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    PURPLE  = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"

    BOLD_GRAY   = "\033[1;30m"
    BOLD_RED    = "\033[1;31m"
    BOLD_GREEN  = "\033[1;32m"
    BOLD_YELLOW = "\033[1;33m"
    BOLD_BLUE   = "\033[1;34m"
    BOLD_PURPLE = "\033[1;35m"
    BOLD_CYAN   = "\033[1;36m"
    BOLD_WHITE  = "\033[1;37m"

    BG_GRAY   = "\033[40m"
    BG_RED    = "\033[41m"
    BG_GREEN  = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE   = "\033[44m"
    BG_PURPLE = "\033[45m"
    BG_CYAN   = "\033[46m"
    BG_WHITE  = "\033[46m"

    @staticmethod
    def gray(str):
        return colors.GRAY + str + colors.RESET
    
    @staticmethod
    def red(str):
        return colors.RED + str + colors.RESET
    
    @staticmethod
    def green(str):
        return colors.GREEN + str + colors.RESET

    @staticmethod
    def yellow(str):
        return colors.YELLOW + str + colors.RESET
        
    @staticmethod
    def blue(str):
        return colors.BLUE + str + colors.RESET
    
    @staticmethod
    def purple(str):
        return colors.PURPLE + str + colors.RESET
    
    @staticmethod
    def cyan(str):
        return colors.CYAN + str + colors.RESET
    
    @staticmethod
    def white(str):
        return colors.WHITE + str + colors.RESET

    @staticmethod
    def normal(str):
        return colors.RESET + str + colors.RESET


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

            elif name == "--h":
                return self.help()
            
            else:
                error("Invalid command:", name)

        except WupError as e:
            if handleError:
                abort(colors.red("[Error] "+ e.message))
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
            if self.length == 0:
                return True
            else:
                return self.received_values[-1]
        
        elif self.mandatory:
            error("Missing parameter:", self.name)
        
        else:
            if self.length == 0:
                return False
            else:
                return self.default
    

    def get_all(self):
        if self.mandatory and not self.received_values:
            error("Missing parameter:", self.name)
        else:
            return self.received_values


class Params:

    def __init__(self, cmd, args, limit_parameters=True):
        self._parent = cmd
        self._name = args.last
        self._args = args
        self._input_parameters = []
        self._parameters = []
        self._names = {}
        self._limit_parameters = limit_parameters

    def map(self, name, n, default, description, mandatory=False):
        if name in dir(self):
            error("Can't use " + name + " as name")
        
        item = ParamsItem(name, n, default, description, mandatory)
        self._names[name] = item

        if not name.startswith("--"):
            self._parameters.append(item)
    

    def help(self):
        options = [self._names[key] for key in self._names if self._names[key].name.startswith("--")]
        arguments = self._parameters

        names = []
        current = self._parent
        while current is not None:
            names.append(current.name)
            current = current.parent
        names.reverse()
        name = " ".join(names)

        if self._parent:
            wprint("DESCRIPTION:")
            print("    " + self._parent.description)
            print()

        wprint("SINTAX:")

        if arguments and options:
            print("    " + name + colors.green(" " + " ".join(["[" + x.name + "]" for x in self._parameters])) + colors.yellow(" {OPTIONS}"))
        
        elif arguments:
            print("    " + name + colors.green(" " + " ".join(["[" + x.name + "]" for x in self._parameters])))

        elif options:
            print("    " + name + colors.yellow(" {OPTIONS}"))
        
        else:
            print("    " + name)

        if arguments:
            print()
            wprint("ARGUMENTS:")

            l = max([len(x.name) for x in arguments])
            for x in arguments:
                print("    " + colors.green(x.name) + " " * (l-len(x.name)) + " - " + x.description)
        
        if options:
            print()
            wprint("OPTIONS:")

            l = max([len(x.name) for x in options])
            for x in options:
                print("    " + colors.yellow(x.name) + " " * (l-len(x.name)) + " - " + x.description)
        
        print()


    def run(self):
        while self._args.has_next():
            if self._args.has_cmd():
                name = self._args.pop_cmd()

                if name in self._names:
                    item = self._names[name]

                    if item.length == 0:
                        values = True
                    elif item.length == 1:
                        values = self._args.pop_parameter()
                    elif item.length > 1:
                        values = [self._args.pop_parameter() for _ in range(item.length)]
                    else:
                        values = []
                        while self._args.has_parameter():
                            values.append(self._args.pop_parameter())
                    
                    item.set(values)
                
                elif name == "--h":
                    self.help()
                    return False
                
                else:
                    error("Invalid parameter: ", name)
            
            else:
                index = len(self._input_parameters)
                name = self._args.pop_parameter()

                if index < len(self._parameters):
                    self._input_parameters.append(name)
                    self._parameters[index].set(name)

                elif self._limit_parameters:
                    error("Too many parameters")
                
                else:
                    self._input_parameters.append(name)
        
        return True


    def has(self, name):
        if not name in self._names:
            error("Unknown parameter:", name)
        
        return self._names[name].has()

    def get(self, name):
        if not name in self._names:
            error("Unknown parameter:", name)
        
        return self._names[name].get()
    

    def get_all(self, name):
        if not name in self._names:
            error("Unknown parameter:", name)
        
        return self._names[name].get_all()
    

    def __getattr__(self, name):
        if name.startswith("every__"):
            return Params.get_all(self, name[5:].replace("_", "-"))
        
        elif name.startswith("flatten__"):
            xxx = Params.get_all(self, name[7:].replace("_", "-"))
            return [x for xx in xxx for x in xx]
        
        elif name.startswith("every_"):
            return Params.get_all(self, name[5:].replace("_", "-"))

        elif name.startswith("__"):
            return Params.get(self, name.replace("_", "-"))
        
        else:
            return Params.get(self, name.replace("_", "-"))
    