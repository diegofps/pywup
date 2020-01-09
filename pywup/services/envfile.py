from pywup.services.system import error, colors
from collections import defaultdict

import copy
import os
import re


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

    def __init__(self, filepath=None):
        self.init_default()
        if filepath is not None:
            self.init_from_envfile(filepath)
    

    def init_default(self):
        self.start = []
        self.open = []
        self.build = []
        self.launch = []
        self.new = []

        self.bashrc = []

        self.base = "ubuntu:bionic"
        self.workdir = "/"
        self.map_ports = []
        self.volumes = []
        self.expose = []
        self.run = "ls"


    def init_from_envfile(self, filepath):
        root = self.read_envfile(filepath)

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
        if "VOLUMES" in root:
            self.volumes = root["VOLUMES"]
        
        if self.volumes:
            self.volumes = [j.strip() for j in self.volumes]
            self.volumes = [j for j in self.volumes if j]
            self.volumes = [os.path.expanduser(j) for j in self.volumes]
            self.volumes = [os.path.abspath(j) for j in self.volumes]

            for v in self.volumes:
                src = v.split(":")[0]

                if not os.path.exists(src):
                    error("Missing source directory in host:", src)
                
                if not os.path.isdir(src):
                    error("Source volume in host is not a directory:", src)
        
        if "LAUNCH" in root:
            self.launch = root["LAUNCH"].lines
        
        if "START" in root:
            self.start = root["START"].lines
        
        if "NEW" in root:
            self.new = root["NEW"].lines
        
        if "OPEN" in root:
            self.open = root["OPEN"].lines
        
        if "BUILD" in root:
            self.full_build = root["BUILD"].lines_recursive()


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
        
        #import pdb; pdb.set_trace()

        return root

