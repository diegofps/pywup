from pywup.services.system import error, abort, WupError, Args
from pywup.services import conf

import os


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
                addr = tmp
    
    return scope, addr, value


def conf_set(args):
    scope, addr, value = conf_parse_cmds(args, scope="local")
    return conf.set(addr, value, scope=scope)


def conf_get(args, scope="any"):
    scope, addr, value = conf_parse_cmds(args, scope=scope)

    if value:
        error("Too many parameters")

    return conf.get(addr, scope=scope, pop=False)


def conf_pop(args):
    scope, addr, value = conf_parse_cmds(args, scope="local")

    if value:
        error("Too many parameters")

    return conf.get(addr, scope=scope)


def main(argv):

    args = Args(argv)
    cmd = args.pop_parameter()

    try:
        if cmd == "get":
            value = conf_get(args)
            if value:
                print(value)
        
        elif cmd == "set":
            conf_set(args)
        
        elif cmd == "pop":
            print(conf_pop(args))
        
        elif cmd == "init":
            conf.init(os.getcwd())
        
        else:
            abort("Unknown config parameter:", cmd)

    except WupError as e:
        abort(e.message)

