from pywup.services.system import error, colors
from collections import defaultdict

from hashlib import md5

import copy
import os
import re


def crop_edge_lines(lines):
    size = len(lines)

    i = 0
    while i < size and lines[i].strip() == "":
        i += 1
    
    first = i

    i = size - 1
    while i >= 0 and lines[i].strip() == "":
        i -= 1
    
    return lines[first:i+1]


class Commit:

    def __init__(self, idd, env, name, lines, hashstr):
        self.idd = idd
        self.env = env
        self.name = name
        self.lines = lines
        self.hashstr = md5(hashstr.encode('utf-8')).hexdigest()
        self.commit_name = "{}__{}__{}__{}".format(env, idd, name, self.hashstr)


class EnvNode:

    def __init__(self, name=None, lvl=0, lines=[]):
        self.name = name
        self.lvl = lvl
        self.lines = lines
        self.children = []
        self.children_map = {}


    def lines_recursive(self):
        tmp = copy.copy(self.lines)

        for x in self.children:
            tmp += x.lines_recursive()
        
        return tmp


    def add(self, node):
        if node.name in self.children_map:
            error("Tag defined more than once:", node.name)
        
        self.children.append(node)
        self.children_map[node.name] = node
    

    def __contains__(self, item):
        return item in self.children_map
    

    def __getitem__(self, key):
        return self.children_map[key]


class EnvFile:

    def __init__(self, name=None, filepath=None):
        self.init_default(name, filepath)
        
        if filepath is not None and name is not None:
            self.init_from_envfile(name, filepath)
    

    @property
    def image_name(self):
        return "wimg:" + self.name


    @property
    def container_name(self):
        return "wcont__" + self.name


    def export_filepath(self, version=None, arch=None):
        if version is None:
            from datetime import datetime
            n = datetime.now()
            version = "%04d%02d%02d-%02d%02d" % (n.year, n.month, n.day, n.hour, n.minute)
        
        if arch is None:
            arch = "generic"

        return ".".join([self.name, arch, version, "gz"])


    def init_default(self, name, filepath):
        self.name = name
        self.filepath = filepath

        self.start = []
        self.open = []
        self.build = []
        self.launch = []
        self.deploy = []
        self.new = []

        self.bashrc = []

        self.base = "ubuntu:bionic"
        self.get_bash = None
        self.flags = set()
        self.workdir = "/"
        self.run = "ls"
        self.map_ports = []
        self.build_volumes = []
        self.deploy_volumes = []
        self.expose = []
        self.commits = []


    def init_from_envfile(self, env, env_filepath):
        root = self.read_envfile(env_filepath)

        # VARIABLES
        variables = {}
        if "VARS" in root:
            for row in root["VARS"].lines:
                row = row.strip()
                
                if not row:
                    continue

                cells = row.split("=", maxsplit=1)

                key, value = cells
                variables[key.strip()] = value.strip()
        

        if "BASE" in variables:
            self.base = variables["BASE"]
        
        if "GETBASH" in variables:
            self.get_bash = variables["GETBASH"]
        
        if "FLAGS" in variables:
            self.flags = set(variables["FLAGS"].split(","))
        
        if "WORKDIR" in variables:
            self.workdir = variables["WORKDIR"]

        if "EXPOSE" in variables:
            self.expose = variables["EXPOSE"].split(",")

        if "MAP_PORTS" in variables:
            self.map_ports = variables["MAP_PORTS"].split(",")

        if "RUN" in variables:
            self.run = variables["RUN"]
        
        # BASHRC
        self.bashrc = [k + "=\"" + variables[k] + "\"\n" for k in variables]
        self.bashrc += ["mkdir -p %s\n" % self.workdir, "cd %s\n" % self.workdir]

        # TEMPLATES
        if "BUILD_VOLUMES" in root:
            lines = root["BUILD_VOLUMES"].lines
            self.build_volumes = lines
            #self.volumes += lines
        
        if "DEPLOY_VOLUMES" in root:
            lines = root["DEPLOY_VOLUMES"].lines
            self.deploy_volumes = lines
            #self.volumes += lines
        
        if "LAUNCH" in root:
            self.launch = root["LAUNCH"].lines
        
        if "START" in root:
            self.start = root["START"].lines
        
        if "DEPLOY" in root:
            self.deploy = root["DEPLOY"].lines
        
        if "OPEN" in root:
            self.open = root["OPEN"].lines
        
        if "BUILD" in root:
            build = root["BUILD"]

            self.full_build = build.lines_recursive()
            self.commit_prefix = "wcommit:" + env

            hashstr = "".join(self.bashrc)
            lines = crop_edge_lines(build.lines)

            if lines:
                hashstr += "ROOT" + "".join(lines)
                commit = Commit(0, self.commit_prefix, "ROOT", lines, hashstr)
                self.commits.append(commit)
            
            for node in build.children:
                if node.name == "ROOT":
                    error("A commit named ROOT is not allowed")
                
                lines = crop_edge_lines(node.lines)

                if lines:
                    hashstr += node.name + "".join(lines)
                    commit = Commit(len(self.commits), self.commit_prefix, node.name, lines, hashstr)
                    self.commits.append(commit)


    def read_envfile(self, filepath):
        
        r = re.compile(r'(#+)\s*([a-zA-Z0-9_]+)\s*(#+)\s*')
        order = []
        rows = []

        with open(filepath, "r") as fin:
            for i, line in enumerate(fin):
                m = r.match(line)
                if m:
                    l = len(m.group(1))
                    name = m.group(2)
                    order.append((name, i, l))
                rows.append(line)
            order.append(("__eof__", i+1, 0))
        
        root = EnvNode()
        node_queue = [root]

        for i in range(1, len(order)):
            name, first, lvl = order[i-1]
            _, last, _ = order[i]
            selection = rows[first+1:last]

            node = EnvNode(name, lvl, selection)
            head = node_queue[-1]

            if node.lvl == head.lvl:
                node_queue.pop()
                node_queue[-1].add(node)
                node_queue.append(node)
            
            elif node.lvl == head.lvl + 1:
                head.add(node)
                node_queue.append(node)
            
            elif node.lvl > head.lvl:
                error("Invalid node depth, should be", str(head.lvl + 1))
            
            else:
                while node_queue[-1].lvl >= node.lvl:
                    node_queue.pop()
                
                node_queue[-1].add(node)
        
        return root

