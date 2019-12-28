from .shared import Args, abort, WupError, error
import yaml
import os


def _local_filepath(folderpath):
    return os.path.join(folderpath, ".wup", "config.yml")


def _global_filepath():
    return os.path.expanduser("~/.local/wup/config.yml")


def read(filepath):
    with open(filepath, "r") as fin:
        data = yaml.load(fin)
        return data


def write(data, filepath):
    folderpath = os.path.dirname(filepath)
    os.makedirs(folderpath, exist_ok=True)

    with open(filepath, "w") as fout:
        yaml.dump(data, fout, default_flow_style=False)


def init(folderpath):
    filepath = _local_filepath(folderpath)
    write({}, filepath)


def find_local_filepath():
    folderpath = os.getcwd()

    while True:
        filepath = _local_filepath(folderpath)

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
    except:
        return None


def _parse_cmds(args, scope="local"):
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


def _smallheader(title, desc):
    print("\n\033[1;97m-- {} ({}) --\033[0m".format(title, desc))


def get(args, pop=False, scope="any"):
    scope, addr, value = _parse_cmds(args, scope=scope)
    
    if value:
        error("Too many parameters")

    if addr:
        if scope in ["any", "local"]:
            filepath = find_local_filepath()

            value = search(filepath, addr, pop)

            if value:
                return value
        
        if scope in ["any", "global"]:
            filepath = _global_filepath()

            value = search(filepath, addr, pop)

            if value:
                return value
    
        error("Attribute not found:", ".".join(addr))

    else:
        if scope in ["any", "local"]:
            filepath = find_local_filepath()

            if filepath and os.path.exists(filepath):
                _smallheader("LOCAL", filepath)
                os.system("cat \"" + filepath + "\"")
            else:
                _smallheader("LOCAL", "NOT FOUND")
        
        if scope in ["any", "global"]:
            filepath = _global_filepath()

            if filepath and os.path.exists(filepath):
                _smallheader("GLOBAL", filepath)
                os.system("cat \"" + filepath + "\"")
            else:
                _smallheader("GLOBAL", "NOT FOUND")
        
        print()
        return None


def assign(args):
    scope, addr, value = _parse_cmds(args, scope="local")
    
    if scope == "global":
        filepath = _global_filepath()
    
    elif scope == "local":
        filepath = _local_filepath(os.getcwd())

    elif scope == "any":
        error("--any is not a valid scope for this operation")

    if not value:
        error("Missing new value")
    
    if not addr:
        error("Missing keys")
    
    try:
        root = read(filepath)
    except:
        root = {}
    
    data = root

    for a in addr[:-1]:
        if not a in data or not type(data[a]) is dict:
            data[a] = {}
        
        data = data[a]
    
    data[addr[-1]] = value
    write(root, filepath)


def pop(args):
    return get(args, pop=True, scope="local")


def main(argv):

    args = Args(argv)
    cmd = args.pop_parameter()

    try:
        if cmd == "get":
            value = get(args)
            if value:
                print(value)
        
        elif cmd == "set":
            assign(args)
        
        elif cmd == "pop":
            print(pop(args))
        
        elif cmd == "init":
            init(os.getcwd())
        
        else:
            abort("Unknown config parameter:", cmd)

    except WupError as e:
        abort(e.message)


