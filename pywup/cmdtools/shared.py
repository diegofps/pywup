from collections import defaultdict
from subprocess import Popen, PIPE

import numpy as np
import shlex
import yaml
import csv
import os
import re


def quote(str):
    return '"' + re.sub(r'([\'\"\\])', r'\\\1', str) + '"'


def get_open_cmd(container_name, bash_init, tty=True):
    o = "".join(["source \"$HOME/.bashrc\"\n"] + bash_init)
    k = quote(o)
    b = quote("bash --init-file <(echo " + k + ")")
    tty = "-it " if tty else "-i "
    c = "docker exec " + tty + container_name + " bash -c " + b.replace("$", "\\$")
    return c


def parse_env(tag, cmd):
    variables, templates = parse_templates(tag)

    if not "BASE" in variables:
        variables["BASE"] = "ubuntu:bionic"
    
    if not "WORKDIR" in variables:
        variables["WORKDIR"] = "/"

    if not "WUPCMD" in variables:
        variables["WUPCMD"] = cmd

    bash_init = [k + "=\"" + variables[k] + "\"\n" for k in variables]
    bash_init.append("cd %s\n" % variables["WORKDIR"])

    for name in ["LAUNCH", "POSTDEPLOY", "BUILD", "OPEN", "EXEC", "NEW"]:
        templates[name] = bash_init + templates[name]
    
    volumes = templates["VOLUMES"]
    if volumes:
        volumes = [j.strip() for j in volumes]
        volumes = [j for j in volumes if j]
        volumes = [os.path.expanduser(j) for j in volumes]
        volumes = [os.path.abspath(j) for j in volumes]

        for v in volumes:
            src = v.split(":")[0]

            if not os.path.exists(src):
                error("Missing source directory in host:", src)
            
            if not os.path.isdir(src):
                error("Source volume in host is not a directory:", src)
        
        templates["VOLUMES"] = volumes

    return variables, templates


def get_export_filepath(project, tag):
    return "wup__{}__{}.gz".format(project, tag)


def get_container_name(projectname, tag, clustername=None, i=None, quantity=None):
    if clustername:
        return "wcl__{}__{}__{}__{}".format(clustername, projectname, tag, i)
    else:
        return "wup__{}_{}".format(projectname, tag)


def get_image_name(projectname, tag):
    return "wup__{}:{}".format(projectname, tag)


def parse_image_name(name):
    tmp = name.split(":")

    if "__" in name:
        error("Names must not contain two consecutive underscores (__)")

    if len(tmp) == 1:
        projectname, tag = conf_get(Args(["project.name"])), tmp[0]
    
    elif len(tmp) == 2:
        projectname, tag = tmp
    
    else:
        error("Too many \":\" in", name)
    
    if tag == "temp":
        error("You cannot have a container named temp")
    
    return projectname, tag


def system_run(cmds, write=None, read=False, suppressInterruption=False):
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


def parse_templates(tag):
    filepath = "./{}.env".format(tag)
    templates = defaultdict(list)
    variables = {}

    if not os.path.exists(filepath):
        return variables, templates

    order = []
    rows = []

    with open(filepath, "r") as fin:
        for i, line in enumerate(fin):
            if line.startswith("@") and line.endswith("@\n"):
                order.append((line[1:-2], i))
            rows.append(line)
        order.append(("eof", i+1))
    
    for i in range(1, len(order)):
        name, first = order[i-1]
        _, last = order[i]
        selection = rows[first+1:last]

        if name == "VARS":
            for row in selection:
                row = row.strip()
                
                if not row:
                    continue

                cells = row.split("=", maxsplit=1)

                if len(cells) != 2:
                    error("Invalid variable declaration:", row)
                
                key, value = cells
                variables[key.strip()] = value.strip()
        
        else:
            templates[name] = selection
    
    return variables, templates


class WupError(Exception):
    def __init__(self, message=None):
        self.message = message


def find_column(headers, header):
    return np.where(headers == header)[0].item()


def read_csv(filepath):
    with open(filepath, "r") as fin:
        reader = csv.reader(fin, delimiter=';')
        data = [cells for cells in reader]
        return np.array(data, dtype=object)


def abort(*args):
    if args:
        print(*args)
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


######################## CONF ######################## 

def conf_local_filepath(folderpath):
    return os.path.join(folderpath, ".wup", "config.yml")


def conf_global_filepath():
    return os.path.expanduser("~/.local/wup/config.yml")


def conf_read(filepath):
    with open(filepath, "r") as fin:
        data = yaml.load(fin)
        return data


def conf_write(data, filepath):
    folderpath = os.path.dirname(filepath)
    os.makedirs(folderpath, exist_ok=True)

    with open(filepath, "w") as fout:
        yaml.dump(data, fout, default_flow_style=False)


def conf_init(folderpath):
    filepath = conf_local_filepath(folderpath)
    conf_write({}, filepath)


def conf_find_local_filepath():
    folderpath = os.getcwd()

    while True:
        filepath = conf_local_filepath(folderpath)

        if os.path.exists(filepath):
            return filepath

        if folderpath == "/":
            return None

        folderpath = os.path.dirname(folderpath)


def conf_search(filepath, addr, pop=False):
    if not addr or not filepath:
        return None
    
    try:
        data = conf_read(filepath)

        for a in addr[:-1]:
            if a in data:
                data = data[a]
            else:
                return None
        
        key = addr[-1]

        if key in data:
            if pop:
                value = data.pop(key)
                conf_write(data, filepath)
                return value
            else:
                return data[key]
        else:
            return None
    except:
        return None


def conf_parse_cmds(args, scope="local"):
    value = None
    addr = None

    while args.has_next():
        if args.has_cmd():
            cmd = args.pop_cmd()

            if cmd == "--global":
                scope = "global"
            
            elif cmd == "--local":
                scope = "local"

            elif cmd == "--any":
                scope = "any"

            else:
                error("Invalid parameter:", cmd)
        
        else:
            tmp = args.pop_parameter()

            if value:
                error("Too many parameters")
            
            elif addr:
                value = tmp
            
            else:
                addr = tmp.split(".")
    
    return scope, addr, value


def print_smallheader(title, desc):
    print("\n\033[1;97m-- {} ({}) --\033[0m".format(title, desc))


def conf_get(args, pop=False, scope="any"):
    scope, addr, value = conf_parse_cmds(args, scope=scope)
    
    if value:
        error("Too many parameters")

    if addr:
        if scope in ["any", "local"]:
            filepath = conf_find_local_filepath()

            value = conf_search(filepath, addr, pop)

            if value:
                return value
        
        if scope in ["any", "global"]:
            filepath = conf_global_filepath()

            value = conf_search(filepath, addr, pop)

            if value:
                return value
    
        error("Attribute not found:", ".".join(addr))

    else:
        if scope in ["any", "local"]:
            filepath = conf_find_local_filepath()

            if filepath and os.path.exists(filepath):
                print_smallheader("LOCAL", filepath)
                os.system("cat \"" + filepath + "\"")
            else:
                print_smallheader("LOCAL", "NOT FOUND")
        
        if scope in ["any", "global"]:
            filepath = conf_global_filepath()

            if filepath and os.path.exists(filepath):
                print_smallheader("GLOBAL", filepath)
                os.system("cat \"" + filepath + "\"")
            else:
                print_smallheader("GLOBAL", "NOT FOUND")
        
        print()
        return None


def conf_set(args):
    scope, addr, value = conf_parse_cmds(args, scope="local")
    
    if scope == "global":
        filepath = conf_global_filepath()
    
    elif scope == "local":
        filepath = conf_local_filepath(os.getcwd())

    elif scope == "any":
        error("--any is not a valid scope for this operation")

    if not value:
        error("Missing new value")
    
    if not addr:
        error("Missing keys")
    
    try:
        root = conf_read(filepath)
    except:
        root = {}
    
    data = root

    for a in addr[:-1]:
        if not a in data or not type(data[a]) is dict:
            data[a] = {}
        
        data = data[a]
    
    data[addr[-1]] = value
    conf_write(root, filepath)


def conf_pop(args):
    return conf_get(args, pop=True, scope="local")
