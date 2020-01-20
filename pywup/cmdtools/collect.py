#!/usr/bin/env python3

from multiprocessing import Pool, cpu_count
from subprocess import Popen, PIPE
from functools import reduce

from pywup.services.system import Args

import shlex
import tqdm
import math
import copy
import csv
import sys
import re

logger = None

def arange(first, last, step):
    current = first
    res = []

    while current <= last:
        res.append(current)
        current += step
    
    return res


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
        self.values = arange(first, last, step)
    
    def get_name(self):
        return self.name
    
    def get_values(self):
        return self.values


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


class Task:

    def __init__(self, row_id, perm_id, run_id, sequence, named, cmd):
        self.row_id = row_id
        self.perm_id = perm_id
        self.run_id = run_id
        self.sequence = sequence
        self.named = named
        self.cmd = cmd

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
        self.dump(3, BasicLog.WARNING, args)
    
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


def f(task):
    return task.row_id, invoke(task.cmd)


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
    
    if jobs <= 0:
        jobs = cpu_count()
    
    #variables.append(RunVariable(runs))
    
    numCombinations = reduce(lambda a,b : a*len(b.get_values()), variables, 1)
    
    ########################### DISPLAY SUMMARY ###########################
    
    logger.print_pagebreak("COLLECT PARAMETERS")
    
    logger.print("Filepath:", filepath)
    logger.print("Logfilepath:", logfilepath)
    logger.print("Combinations:", numCombinations)
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
    
    ########################### CREATE PARALLEL TASKS ###########################
    
    logger.print("\nCreating Tasks...")
    
    tasks = []
    ridd = -1
    pidd = -1
    
    for sequence, named in perm_variables(variables):
        pidd += 1
        for _ in range(runs):
            ridd += 1
            for cmdline in cmdlines:
                task = Task(row_id=len(tasks), perm_id=pidd, run_id=ridd, sequence=copy.copy(sequence), named=copy.copy(named), cmd=cmdline.format(*sequence))
                tasks.append(task)
    
    ########################### EXECUTE PARALLEL TASKS ###########################

    logger.print_pagebreak("RUNNING {} TASK(S)".format(len(tasks)))
    
    with Pool(jobs) as p:
        with open(filepath, "w") as fout:
            header = ["PERMID", "RUNID"] + [v.get_name() for v in variables] + [x.get_name() for x in patterns]
            writer = csv.writer(fout, delimiter=";", quoting=csv.QUOTE_MINIMAL)
            writer.writerow(header)
            
            # Line breaks are defined by the patterns we got
            if line_breaks:
                ignore_once = True
                
                for k, rows in tqdm.tqdm(p.imap(f, tasks), total=len(tasks)):
                    #_, idd, sequence, named, prepared_cmd = tasks[k]
                    task = tasks[k]
                    
                    for row in rows:
                        doBreak = False
                        
                        for n in line_breaks:
                            if n.check(row):
                                doBreak = True
                        
                        if doBreak:
                            if ignore_once:
                                ignore_once = False
                            else:
                                ptask = tasks[k-1]
                                writer.writerow([ptask.perm_id, ptask.run_id] + task.sequence + [x.get_value() for x in patterns])
                                fout.flush()
                            
                            for x in patterns:
                                x.clear()
                        
                        for x in patterns:
                            x.check(row)
                
                if ignore_once:
                    ignore_once = False
                else:
                    writer.writerow([task.perm_id, task.run_id] + task.sequence + [x.get_value() for x in patterns])
                    fout.flush()
            
            # Line breaks are defined by permutations, each combination creates a single line
            else:
                last_idd = tasks[0].run_id if tasks else None
                
                for k, rows in tqdm.tqdm(p.imap(f, tasks), total=len(tasks)):
                    #_, idd, sequence, named, prepared_cmd = tasks[k]
                    task = tasks[k]
                    
                    if last_idd != task.run_id:
                        last_idd = task.run_id
                        
                        ptask = tasks[k-1]
                        writer.writerow([ptask.perm_id, ptask.run_id] + ptask.sequence + [x.get_value() for x in patterns])
                        fout.flush()
                        
                        for x in patterns:
                            x.clear()
                    
                    for row in rows:
                        for x in patterns:
                            x.check(row)
                
                writer.writerow([task.perm_id, task.run_id] + task.sequence + [x.get_value() for x in patterns])
                fout.flush()


def main(cmd, args):
    
    filepath = "./collect_output.csv"
    logfilepath = None
    line_breaks = []
    variables = []
    patterns = []
    cmdline = []
    runs = 1
    jobs = 0
    
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
