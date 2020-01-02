from subprocess import Popen, PIPE

import numpy as np
import shlex
import sys
import csv
import re
import os


def quote(str):
    return '"' + re.sub(r'([\'\"\\])', r'\\\1', str) + '"'


def run(cmds, write=None, read=False, suppressInterruption=False):
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

            return ps[-1].wait(), None

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

            return ps[-1].wait(), None

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
        return v
    
    def pop_parameter(self):
        if not self.has_parameter():
            raise RuntimeError("Wrong argument, expecting a command parameter")
        return self.pop()
    
    def pop_cmd(self):
        if not self.has_cmd():
            raise RuntimeError("Wrong argument, expecting a command: ", self.sneak())
        return self.pop()


def read_csv(filepath):
    with open(filepath, "r") as fin:
        reader = csv.reader(fin, delimiter=';')
        data = [cells for cells in reader]
        return np.array(data, dtype=object)
