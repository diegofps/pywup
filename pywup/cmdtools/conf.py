from .shared import Args, abort, WupError, error
import yaml
import os


def config_local_filepath(folderpath):
    return os.path.join(folderpath, ".wup", "config.yml")


def config_global_filepath():
    return os.path.expanduser("~/.local/wup/config.yml")


def config_read(filepath):
    with open(filepath, "r") as fin:
        data = yaml.load(fin)
        return data


def config_write(data, filepath):
    folderpath = os.path.dirname(filepath)
    os.makedirs(folderpath, exist_ok=True)

    with open(filepath, "w") as fout:
        yaml.dump(data, fout, default_flow_style=False)


def config_init(folderpath):
    filepath = config_local_filepath(folderpath)
    config_write({}, filepath)


def config_find_local_filepath():
    folderpath = os.getcwd()

    while True:
        filepath = config_local_filepath(folderpath)

        if os.path.exists(filepath):
            return filepath

        if folderpath == "/":
            return None

        folderpath = os.path.dirname(folderpath)


def config_search(filepath, addr, pop=False):
    if not addr or not filepath:
        return None
    
    try:
        data = config_read(filepath)

        for a in addr[:-1]:
            if a in data:
                data = data[a]
            else:
                return None
        
        key = addr[-1]

        if key in data:
            if pop:
                value = data.pop(key)
                config_write(data, filepath)
                return value
            else:
                return data[key]
        else:
            return None
    except:
        return None


def config_parse_cmds(args, scope="local"):
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
                addr = tmp.split(":")
    
    return scope, addr, value
    

def config_get(args, pop=False, scope="any"):
    scope, addr, value = config_parse_cmds(args, scope=scope)
    
    if value:
        error("Assignment is not valid in this operation")

    if scope in ["any", "local"]:
        filepath = config_find_local_filepath()

        if addr:
            value = config_search(filepath, addr, pop)

            if value:
                return value
        
        else:
            if filepath and os.path.exists(filepath):
                print("-- LOCAL --")
                os.system("cat \"" + filepath + "\"")
            else:
                print("-- LOCAL CONFIG NOT FOUND --")
    
    if scope in ["any", "global"]:
        filepath = config_global_filepath()

        if addr:
            value = config_search(filepath, addr, pop)

            if value:
                return value
        
        else:
            if filepath and os.path.exists(filepath):
                print("-- GLOBAL --")
                os.system("cat \"" + filepath + "\"")
            else:
                print("-- GLOBAL CONFIG NOT FOUND --")
    
    if addr:
        error("Attribute not found")
    else:
        return None


def config_set(args):
    scope, addr, value = config_parse_cmds(args, scope="local")
    
    if scope == "global":
        filepath = config_global_filepath()
    
    elif scope == "local":
        filepath = config_local_filepath(os.getcwd())

    elif scope == "any":
        error("--any is not a valid scope for this operation")

    if not value:
        error("Missing new value")
    
    if not addr:
        error("Missing keys")
    
    try:
        root = config_read(filepath)
    except:
        root = {}
    
    data = root

    for a in addr[:-1]:
        if not a in data or not type(data[a]) is dict:
            data[a] = {}
        
        data = data[a]
    
    data[addr[-1]] = value
    config_write(root, filepath)


def config_pop(args):
    return config_get(args, pop=True, scope="local")


def main(argv):

    args = Args(argv)
    cmd = args.pop_parameter()

    try:
        if cmd == "get":
            value = config_get(args)
            if value:
                print(value)
        
        elif cmd == "set":
            config_set(args)
        
        elif cmd == "pop":
            print(config_pop(args))
        
        elif cmd == "init":
            config_init(os.getcwd())
        
        else:
            abort("Unknown config parameter:", cmd)

    except WupError as e:
        abort(e.message)


