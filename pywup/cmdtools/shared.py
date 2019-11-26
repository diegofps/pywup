import numpy as np
import csv


def find_column(headers, header):
    return np.where(headers == header)[0].item()


def read_csv(filepath):
    with open(filepath, "r") as fin:
        reader = csv.reader(fin, delimiter=';')
        data = [cells for cells in reader]
        return np.array(data, dtype=object)


class Args:
    
    def __init__(self, args):
        self.args = args
        self.current = 0
    
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
            raise RuntimeError("Unexpected argument, expecting a command parameter")
        return self.pop()
    
    def pop_cmd(self):
        if not self.has_cmd():
            raise RuntimeError("Unexpected argument, expecting a command: ", self.sneak())
        return self.pop()

