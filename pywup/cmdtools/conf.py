from .shared import conf_get, conf_set, conf_pop, conf_init
from .shared import Args, abort, WupError, error

import os


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
            conf_init(os.getcwd())
        
        else:
            abort("Unknown config parameter:", cmd)

    except WupError as e:
        abort(e.message)


