from pywup.services.system import error

import copy
import sys
import re


class Command:

    def __init__(self, cmdline, env=None):
        self.cmdline = cmdline
        self.env_name = env


    def __repr__(self):
        return "Command %s; %s" % (self.cmdline, self.env_name)


class Pattern:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        self.raw = args.pop_parameter()
        self.data = None

        self.raw = self.raw.replace("@float@", "[-0-9\\.e\\+]+")
        self.raw = self.raw.replace("@int@", "[-0-9\\+]+")
        self.raw = self.raw.replace("@slug@", "[-0-9a-zA-Z_]+")
        self.raw = self.raw.replace("@str@", "\"[^\"]+\"")

        self.p = re.compile(self.raw)
    

    def clear(self):
        self.data = None
    

    def get_name(self):
        return self.name
    

    def get_value(self):
        if self.data is None:
            sys.stdout.write("!(" + self.name + ")")
        return self.data
    

    def value(self):
        return self.data
    
    
    def check(self, row):
        m = self.p.search(row)
        if m:
            self.data = m.groups()[0]


class Experiment:

    def __init__(self, name):

        self.work_dir = None
        self.variables = []
        self.commands = []
        self.patterns = []
        self.name = name
    

    def __repr__(self):
        return "Experiment %s; %s; %s" % (self.name, str(self.variables), str(len(self.commands)))


    def add_pattern(self, p):
        self.patterns.append(p)


    def add_variable(self, v):
        if any(v.get_name() == o.get_name() for o in self.variables):
            error("Variable %s is already defined in this environment" % v.get_name())
        else:
            self.variables.append(v)


    def add_command(self, c):
        self.commands.append(Command(c))


    def add_virtual_command(self, e, c):
        self.commands.append(Command(c, e))


    def get_variables(self, default_variables):
        variables = { v.get_name() : v for v in default_variables }
        
        for v in self.variables:
            variables[v.get_name()] = v
        
        return [value for _, value in variables.items()]

    
    def get_work_dir(self, default_workdir):
        if self.work_dir is None:
            return default_workdir
        else:
            return self.work_dir


class ListVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        self.values = []
        
        while args.has_parameter():
            self.values.append(args.pop_parameter())
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values

    def __repr__(self):
        return "ListVariable %s; %s" % (self.name, str(self.values))


class RunVariable:
    
    def __init__(self, num):
        self.name = "RUN"
        self.values = [i for i in range(num)]
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values

    def __repr__(self):
        return "RunVariable %s; %s" % (self.name, str(self.values))


class ArithmeticVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        
        self.first = float(args.pop_parameter())
        self.last  = float(args.pop_parameter())
        self.step  = float(args.pop_parameter()) if args.has_parameter() else 1

        self.values = self.arange(self.first, self.last, self.step)
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values

    def arange(self, first, last, step):
        current = first
        res = []

        while current <= last:
            res.append(current)
            current += step
        
        return res

    def __repr__(self):
        return "ArithmeticVariable %s; %f %f %f; %s" % (self.name, self.first, self.last, self.step, str(self.values))


class GeometricVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        
        self.first = float(args.pop_parameter())
        self.last  = float(args.pop_parameter())
        self.step  = float(args.pop_parameter()) if args.has_parameter() else 2.0
        
        if self.step == 1:
            raise RuntimeError("step cannot be equal to 1")
        
        self.values = list()
        current = self.first
        
        while current < self.last:
            self.values.append(current)
            current = current * self.step
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values

    def __repr__(self):
        return "GeometricVariable %s; %f %f %f; %s" % (self.name, self.first, self.last, self.step, str(self.values))
