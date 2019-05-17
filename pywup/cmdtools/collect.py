#!/usr/bin/env python3

from subprocess import Popen, PIPE
import numpy as np
import shlex
import math
import csv
import sys
import pdb
import re


class Args:
    
    def __init__(self, args):
        self.args = args
        self.current = 0
    
    def has_cmd_parameter(self):
        return self.has_next() and not self.args[self.current].startswith("-")
    
    def has_cmd(self):
        return self.has_next() and self.args[self.current].startswith("-")
    
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
        if not self.has_cmd_parameter():
            raise RuntimeError("Unexpected argument, expecting a command parameter")
        return self.pop()
    
    def pop_cmd(self):
        if not self.has_cmd():
            raise RuntimeError("Unexpected argument, expecting a command: ", self.sneak())
        return self.pop()


class Pattern:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        self.p = re.compile(args.pop_parameter())
        self.value = -1
    
    def clear(self):
        self.value = -1
    
    def get_name(self):
        return self.name
    
    def get_value(self):
        return self.value
    
    def check(self, row):
        m = self.p.search(row)
        if m:
            self.value = float(m.groups()[0])


class ListVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        self.values = []
        
        while args.has_cmd_parameter():
            self.values.append(args.pop_parameter())
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values


class ArithmeticVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        
        first = float(args.pop_parameter())
        last  = float(args.pop_parameter())
        step  = float(args.pop_parameter()) if args.has_cmd_parameter() else 1
        self.values = np.arange(first, last, step)
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values


class GeometricVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        
        first = float(args.pop_parameter())
        last  = float(args.pop_parameter())
        step  = float(args.pop_parameter()) if args.has_cmd_parameter() else 2.0
        
        if step == 1:
            raise RuntimeError("step cannot be equal to 1")
        
        self.values = list()
        current = first
        
        while current < last:
            self.values.append(current)
            current = current * step
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values


def invoke(cmdline):
    args = shlex.split(cmdline)
    p = Popen(args, stdout=PIPE)
    
    if p.wait() != 0:
        raise RuntimeError("Command is not working")
    
    stdout, _ = p.communicate()
    return stdout.decode("utf-8").split("\n")


def perm_variables(variables, output=[]):
    if len(variables) == len(output):
        yield output
    
    else:
        for v in variables[len(output)].get_values():
            output.append(v)
            for tmp in perm_variables(variables, output):
                yield tmp
            output.pop()


def do_collect(variables, cmdline, patterns, runs, filepath):
    if not cmdline:
        return print("Missing parameter cmdline")

    if len(patterns) == 0:
        return print("No patterns were given, nothing would be collected")

    if runs <= 0:
        return print("Must execute at least 1 run")

    print("Variables:")
    for v in variables:
        vs = v.get_values()
        print("{} ({}) : {}".format(v.get_name(), len(vs), vs))

    with open(filepath, "w") as fout:
        writer = csv.writer(fout, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow([v.get_name() for v in variables] + ["RUN"] + [p.get_name() for p in patterns])
        
        for sequence in perm_variables(variables):
            sys.stdout.write(str(sequence))
            sys.stdout.flush()
            
            prepared_cmd = cmdline.format(*sequence)
            
            for run in range(runs):
                
                for p in patterns:
                    p.clear()
                
                rows = invoke(prepared_cmd)
                
                for row in rows:
                    for p in patterns:
                        p.check(row)
                
                writer.writerow(sequence + [run] + [p.get_value() for p in patterns])
                fout.flush()
                
                sys.stdout.write("*")
                sys.stdout.flush()
            
            print()


def main(argv):

    args = Args(argv)
    filepath = "./collect_output.csv"
    variables = []
    cmdline = None
    patterns = []
    runs = 1

    while args.has_next():
        cmd = args.pop_cmd()

        if cmd == "--p":
            patterns.append(Pattern(args))

        elif cmd == "--runs":
            runs = int(args.pop_parameter())

        elif cmd == "--va":
            variables.append(ArithmeticVariable(args))

        elif cmd == "--vg":
            variables.append(GeometricVariable(args))

        elif cmd == "--v":
            variables.append(ListVariable(args))

        elif cmd == "--c":
            cmdline = args.pop_parameter()

        elif cmd == "--o":
            filepath = args.pop_parameter()

    do_collect(variables, cmdline, patterns, runs, filepath)
