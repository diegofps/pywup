from .shared import Args
import yaml
import os


def config_read(filepath):
    with open(filepath, "r") as fin:
        data = yaml.load(fin)
        return data


def config_write(data, filepath):
    folderpath = os.path.dirname(filepath)
    os.makedirs(folderpath, exist_ok=True)

    with open(filepath, "w") as fout:
        yaml.dump(data, fout, default_flow_style=False)


def config_search(filepath, addr):
    try:
        data = config_read(filepath)
        for a in addr:
            if a in data:
                data = data[a]
            else:
                return None
        return data
    except:
        return None


def config_get(args):
    addr = args.all()

    folderpath = os.getcwd()

    while True:
        filepath = os.path.join(folderpath, ".wup", "config.yml")
        value = config_search(filepath, addr)

        if value:
            return value

        if folderpath == "/":
            break

        folderpath = os.path.dirname(folderpath)
    
    filepath = os.path.expanduser("~/.local/wup/config.yml")
    value = config_search(filepath, addr)

    if value:
        return value
    
    print("Attribute not found")
    exit(1)


def config_set(args):
    if args.has_next() and args.sneak() == "global":
        filepath = os.path.expanduser("~/.local/wup/config.yml")
        args.pop_parameter()
        addr = args.all()

    else:
        filepath = os.path.join(os.getcwd(), ".wup", "config.yml")
        addr = args.all()

    try:
        root = config_read(filepath)
    except:
        root = {}
    
    data = root

    for a in addr[:-2]:
        if not a in data:
            data[a] = {}
        
        try:
            data = data[a]
        except:
            print("Excepted {} to be a dictionary" % a)
    
    data[addr[-2]] = addr[-1]

    config_write(root, filepath)


def config_drop(args):
    if args.has_next() and args.sneak() == "global":
        filepath = os.path.expanduser("~/.local/wup/config.yml")
        args.pop_parameter()
        addr = args.all()

    else:
        filepath = os.path.join(os.getcwd(), ".wup", "config.yml")
        addr = args.all()

    try:
        root = config_read(filepath)
    except:
        root = {}
    
    data = root

    for a in addr[:-1]:
        if not a in data:
            print("Attribute not found,", a)
            exit(1)
        
        try:
            data = data[a]
        except:
            print("Excepted {} to be a dictionary" % a)
    
    key = addr[-1]

    if key in data:
        try:
            data.pop(key)
            config_write(root, filepath)
        except:
            print("Excepted {} to be a dictionary" % key)
    
    else:
        print("Attibute not found:", key)
        exit(1)


def main(argv):
    args = Args(argv)
    cmd = args.pop_parameter()

    if cmd == "get":
        config_get(args)

    elif cmd == "set":
        config_set(args)

    elif cmd == "drop":
        config_drop(args)

    else:
        print("Unknown config parameter:", cmd)
