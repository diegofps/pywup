from types import SimpleNamespace
from subprocess import Popen, PIPE
import shlex
import sys

def run(cmd, prefix_filter=None):
    args = shlex.split(cmd)
    p = Popen(args, stdout=PIPE)
    
    p.wait()
    
    stdout, _ = p.communicate()
    rows = stdout.decode("utf-8").split("\n")
    rows = [i for i in rows if i.strip()]
    
    if prefix_filter is not None:
        rows = [i for i in rows if i.startswith(prefix_filter)]
    
    return rows


def error(msg):
    print(msg)
    exit(1)


def find(options, name, find_method, prefix_filter):
    if isinstance(options, list):
        for option in options:
            item = find_method(option, name)
            if item:
                return item
        return None
    else:
        candidates = run("locate *%s" % options, prefix_filter)
        
        if not candidates:
            return None
        
        print("%s found at %s" % (name, candidates[-1]))
        return candidates[-1]

    
def find_or_abort(options, name, find_method, pkg):
    item = find_method(options, name)
    
    if item is None:
        print("%s not found. Did you install %s or similar?" % (name, pkg))
        sys.exit(1)
        
    return item



class TemplateBuilder(SimpleNamespace):
    
    def build(self, filepath, template):
        with open(filepath, "w") as fout:
            fout.write(template.format(**self.__dict__))



def find_program(options, name):
    return find(options, name, find_program, "/usr/bin")

def find_header(options, name):
    return find(options, name, find_header, "/usr/include")

def find_lib(options, name):
    return find(options, name, find_lib, "/usr/lib")

def find_file(options, name):
    return find(options, name, find_file, None)



def find_lib_or_abort(options, name, pkg):
    return find_or_abort(options, name, find_lib, pkg)

def find_program_or_abort(options, name, pkg):
    return find_or_abort(options, name, find_program, pkg)

def find_header_or_abort(options, name, pkg):
    return find_or_abort(options, name, find_header, pkg)

def find_file_or_abort(options, name, pkg):
    return find_or_abort(options, name, find_file, pkg)

