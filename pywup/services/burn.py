from pywup.services.system import error

import copy

class Experiment:

    def __init__(self):
        self.work_dir = None
        self.variables = {}
        self.commands = []
    

    def add_variable(self, v):
        if v.get_name() in self.variables:
            error("This variable is already defined in this environment")
        else:
            self.variables[v.get_name()] = v


    def add_command(self, c):
        self.commands.append(c)


    def get_variables(self, default_variables):
        variables = copy.copy(default_variables)

        for v in self.variables:
            variables[v.get_name()] = v
        
        return variables

    
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


class RunVariable:
    
    def __init__(self, num):
        self.name = "RUN"
        self.values = [i for i in range(num)]
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values


class ArithmeticVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        
        first = float(args.pop_parameter())
        last  = float(args.pop_parameter())
        step  = float(args.pop_parameter()) if args.has_parameter() else 1
        self.values = self.arange(first, last, step)
    
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


class GeometricVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        
        first = float(args.pop_parameter())
        last  = float(args.pop_parameter())
        step  = float(args.pop_parameter()) if args.has_parameter() else 2.0
        
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

