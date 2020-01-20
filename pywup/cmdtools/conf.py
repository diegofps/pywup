from pywup.services.system import error, abort, WupError, Args, Route
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


def conf_init(cmd, args):
    conf.init(os.getcwd())


def conf_set(cmd, args):
    scope, addr, value = conf_parse_cmds(args, scope="local")
    return conf.set(addr, value, scope=scope)


def conf_get(cmd, args):
    scope, addr, value = conf_parse_cmds(args, scope="any")

    if value:
        error("Too many parameters")

    value = conf.get(addr, scope=scope, pop=False)

    if value:
        print(value)


def conf_pop(cmd, args):
    scope, addr, value = conf_parse_cmds(args, scope="local")

    if value:
        error("Too many parameters")

    return conf.get(addr, scope=scope)


def main(cmd, args):
    r = Route(args, parent=cmd)

    r.map("init", conf_init, "Initialize an empty wup settings in the current directory")
    r.map("get", conf_get, "Get the value associated with an attribute")
    r.map("set", conf_set, "Assign a value to one attribute")
    r.map("rm", conf_pop, "Remove attribute from the settings")
    
    r.run()
