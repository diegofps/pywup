#!/usr/bin/env python3

from subprocess import Popen, PIPE
from multiprocessing import Pool
from .shared import *

import numpy as np
import shlex
import tqdm
import math
import copy
import csv
import sys
import pdb
import re

logger = None

class NewLine:
    
    def __init__(self, args):
        self.raw = args.pop_parameter()
        self.p = re.compile(self.raw)
    
    def check(self, row):
        return self.p.search(row)


class Pattern:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        self.raw = args.pop_parameter()
        self.p = re.compile(self.raw)
        self.data = None
    
    def clear(self):
        self.data = None
    
    def get_name(self):
        return self.name
    
    def get_value(self):
        if self.data is None:
            sys.stdout.write("!(" + self.name + ")")
        return self.data
    
    def value(self):
        return -1 if self.data is None else float(self.data)
    
    def check(self, row):
        m = self.p.search(row)
        if m:
            self.data = m.groups()[0]


class ListVariable:
    
    def __init__(self, args):
        self.name = args.pop_parameter()
        self.values = []
        
        while args.has_cmd():
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
        step  = float(args.pop_parameter()) if not args.has_cmd() else 1
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
        step  = float(args.pop_parameter()) if args.has_cmd() else 2.0
        
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
    
    # Removing this cause it locks if the buffer gets filled by the lower process
    #if p.wait() != 0:
    #    raise RuntimeError("Command is not working")
    
    rows = "".join([l.decode("utf-8") for l in p.stdout])
    
    #stdout, _ = p.communicate()
    #rows = stdout.decode("utf-8")
    
    logger.debug(rows)
    
    return rows.split("\n")


def perm_variables(variables, output=[], named_output=[]):
    if len(variables) == len(output):
        yield output, named_output
    
    else:
        name = variables[len(output)].get_name()
        
        for v in variables[len(output)].get_values():
            output.append(v)
            named_output.append((name, v))
            for tmp in perm_variables(variables, output):
                yield tmp
            output.pop()
            named_output.pop()


class BasicLog:

    ERROR = '\033[91m'
    WARNING = '\033[93m'
    INFO = '\033[94m'
    DEBUG = '\033[92m'
    NORMAL = '\033[0m'

    def __init__(self, filepath=None, level=2, color=True):
        self.fout = open(filepath, "w") if filepath else None
        self.level = level
        self.color = color
    
    def error(self, *args):
        self.dump(4, BasicLog.ERROR, args)
    
    def warn(self, *args):
        self.dump(3, BasicLog.WARN, args)
    
    def print(self, *args):
        self.dump(2, BasicLog.NORMAL, args)
    
    def info(self, *args):
        self.dump(1, BasicLog.INFO, args)
    
    def debug(self, *args):
        self.dump(0, BasicLog.DEBUG, args)
    
    def write(self, *args):
        sys.stdout.write(*args)
        if self.fout:
            if args:
                self.fout.write(" ".join([str(i) for i in args]))
    
    def dump(self, lvl, color, args):
        if lvl >= self.level:
            if self.color:
                print(color, *args, BasicLog.NORMAL)
            else:
                print(*args)
        
        if self.fout:
            if args:
                self.fout.write(" ".join([str(i) for i in args]))
            self.fout.write("\n")
            self.fout.flush()
    
    def page(self, msg):
        return "\n ------------------------ " + msg + " ------------------------ \n"
    
    def error_pagebreak(self, msg):
        self.error(self.page(msg))
    
    def warn_pagebreak(self, msg):
        self.warn(self.page(msg))

    def print_pagebreak(self, msg):
        self.print(self.page(msg))

    def info_pagebreak(self, msg):
        self.info(self.page(msg))

    def debug_pagebreak(self, msg):
        self.debug(self.page(msg))


def f(data):
    k, idd, sequence, named, prepared_cmd = data
    rows = invoke(prepared_cmd)
    return k, rows


def do_collect(line_breaks, variables, cmdlines, patterns, runs, filepath, logfilepath, jobs):
    
    ########################### CREATE THE LOGGER ###########################
    
    global logger
    logger = BasicLog(logfilepath)
    
    ########################### CHECK PARAMETERS ###########################
    
    if not cmdlines:
        return logger.print("Missing parameter --c")
    
    if len(patterns) == 0:
        return logger.print("Missing pattern --p, nothing would be collected")
    
    if runs <= 0:
        return logger.print("--runs must be >= 1")
    
    variables.append(RunVariable(runs))
    
    ########################### DISPLAY SUMMARY ###########################
    
    logger.print_pagebreak("COLLECT PARAMETERS")
    
    logger.print("Filepath:", filepath)
    logger.print("Logfilepath:", logfilepath)
    logger.print("Runs:", runs)
    logger.print("Jobs:", jobs)
    
    logger.print("Input Variables ({})".format(len(variables)))
    for v in variables:
        vs = v.get_values()
        logger.print("    {} ({}) : {}".format(v.get_name(), len(vs), vs))
    
    logger.print("Output Patterns ({})".format(len(patterns)))
    for v in patterns:
        logger.print("    {} : {}".format(v.name, v.raw))
    
    logger.print("LineBreaks ({})".format(len(line_breaks)))
    for v in line_breaks:
        logger.print("    {}".format(v.raw))
    
    logger.print("Commands ({})".format(len(cmdlines)))
    for v in cmdlines:
        logger.print("    {}".format(v))
    
    ########################### PARALLEL TASKS ###########################
    
    logger.print_pagebreak("RUNNING TASKS")
    
    tasks = []
    idd = -1
    k = 0
    
    for sequence, named in perm_variables(variables):
        idd += 1
        for cmdline in cmdlines:
            prepared_cmd = cmdline.format(*sequence)
            tasks.append([k, idd, copy.copy(sequence), copy.copy(named), prepared_cmd])
            k += 1
    
    with Pool(jobs) as p:
        with open(filepath, "w") as fout:
            header = [v.get_name() for v in variables] + [p.get_name() for p in patterns]
            writer = csv.writer(fout, delimiter=";", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            
            # Line breaks are defined by the patterns we got
            if line_breaks:
                ignore_once = True
                
                for k, rows in tqdm.tqdm(p.imap(f, tasks), total=len(tasks)):
                    _, idd, sequence, named, prepared_cmd = tasks[k]
                    
                    for row in rows:
                        doBreak = False
                        
                        for n in line_breaks:
                            if n.check(row):
                                doBreak = True
                        
                        if doBreak:
                            if ignore_once:
                                ignore_once = False
                            else:
                                writer.writerow(tasks[k-1][2] + [p.get_value() for p in patterns])
                                fout.flush()
                            
                            for p in patterns:
                                p.clear()
                        
                        for p in patterns:
                            p.check(row)
                
                if ignore_once:
                    ignore_once = False
                else:
                    writer.writerow(sequence + [p.get_value() for p in patterns])
                    fout.flush()
            
            # Line breaks are defined by permutations, each combination creates a single line
            else:
                last_idd = tasks[0][1] if tasks else None
                
                for k, rows in tqdm.tqdm(p.imap(f, tasks), total=len(tasks)):
                    _, idd, sequence, named, prepared_cmd = tasks[k]
                    
                    if last_idd != idd:
                        last_idd = idd
                        
                        writer.writerow(tasks[k-1][2] + [p.get_value() for p in patterns])
                        fout.flush()
                        
                        for p in patterns:
                            p.clear()
                    
                    for row in rows:
                        for p in patterns:
                            p.check(row)
                
                writer.writerow(sequence + [p.get_value() for p in patterns])
                fout.flush()


def main(argv):
    
    args = Args(argv)
    filepath = "./collect_output.csv"
    line_breaks = []
    variables = []
    patterns = []
    cmdline = []
    runs = 1
    jobs = 1
    
    while args.has_next():
        cmd = args.pop_cmd()
        #print("parsing ", cmd)

        if cmd == "--n":
            line_breaks.append(NewLine(args))

        elif cmd == "--log":
            logfilepath = args.pop_parameter()
        
        elif cmd == "--p":
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
            cmdline.append(args.pop_parameter())

        elif cmd == "--o":
            filepath = args.pop_parameter()
        
        elif cmd == "--jobs":
            jobs = int(args.pop_parameter())
        
        else:
            print("Unknown command: ", cmd)
        
    do_collect(line_breaks, variables, cmdline, patterns, runs, filepath, logfilepath, jobs)
