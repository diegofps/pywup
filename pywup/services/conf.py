from pywup.services.system import error

import yaml
import os


def print_smallheader(title, desc):
    print("\n\033[1;97m-- {} ({}) --\033[0m".format(title, desc))


def get_local_filepath(folderpath):
    return os.path.join(folderpath, ".wup", "config.yml")


def get_global_filepath():
    return os.path.expanduser("~/.local/wup/config.yml")


def read(filepath):
    with open(filepath, "r") as fin:
        if hasattr(yaml, "FullLoader"):
            return yaml.load(fin, Loader=yaml.FullLoader)
        else:
            return yaml.load(fin)


def write(data, filepath):
    folderpath = os.path.dirname(filepath)
    os.makedirs(folderpath, exist_ok=True)

    with open(filepath, "w") as fout:
        yaml.dump(data, fout, default_flow_style=False)


def init(folderpath):
    filepath = get_local_filepath(folderpath)
    write({}, filepath)


def find_local_filepath():
    folderpath = os.getcwd()

    while True:
        filepath = get_local_filepath(folderpath)

        if os.path.exists(filepath):
            return filepath

        if folderpath == "/":
            return None

        folderpath = os.path.dirname(folderpath)


def search(filepath, addr, pop=False):
    if not addr or not filepath:
        return None
    
    try:
        data = read(filepath)

        for a in addr[:-1]:
            if a in data:
                data = data[a]
            else:
                return None
        
        key = addr[-1]

        if key in data:
            if pop:
                value = data.pop(key)
                write(data, filepath)
                return value
            else:
                return data[key]
        else:
            return None
    except FileNotFoundError:
        return None


def set(addr, value, scope="local"):
    if type(addr) is str:
        addr = addr.split(".")
    
    if scope == "local":
        filepath = get_local_filepath(os.getcwd())

    elif scope == "global":
        filepath = get_global_filepath()
    
    elif scope == "any":
        error("--any is not a valid scope for this operation")

    if value is None:
        error("Missing new value")
    
    if not addr:
        error("Missing keys")
    
    try:
        root = read(filepath)
    except FileNotFoundError:
        root = {}
    
    data = root

    for a in addr[:-1]:
        if not a in data or not type(data[a]) is dict:
            data[a] = {}
        
        data = data[a]
    
    data[addr[-1]] = value
    write(root, filepath)


def get(addr, scope="any", pop=False, default=None, failOnMiss=True):

    if type(addr) is str:
        addr = addr.split(".")
    
    if addr:
        if scope in ["any", "local"]:
            filepath = find_local_filepath()

            value = search(filepath, addr, pop)

            if value:
                return value
        
        if scope in ["any", "global"]:
            filepath = get_global_filepath()

            value = search(filepath, addr, pop)

            if value:
                return value
    
        if failOnMiss:
            raise AttributeError("Attribute not found: " + ".".join(addr))
    
        return default
    
    else:
        if scope in ["any", "local"]:
            filepath = find_local_filepath()

            if filepath and os.path.exists(filepath):
                print_smallheader("LOCAL", filepath)
                os.system("cat \"" + filepath + "\"")
            else:
                print_smallheader("LOCAL", "NOT FOUND")
        
        if scope in ["any", "global"]:
            filepath = get_global_filepath()

            if filepath and os.path.exists(filepath):
                print_smallheader("GLOBAL", filepath)
                os.system("cat \"" + filepath + "\"")
            else:
                print_smallheader("GLOBAL", "NOT FOUND")
        
        print()
        return None


def pop(addr, scope="any"):
    return get(addr, scope=scope, pop=True)

