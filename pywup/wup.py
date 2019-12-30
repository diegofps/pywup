#!/usr/bin/env python3

from sys import argv


def wup(debug=False):
    args = argv[1:]
    
    if len(args) == 0:
        return print("Missing wup command")
    
    cmd = args[0]
    
    if cmd == "heatmap":
        if debug:
            from cmdtools.heatmap import main
        else:
            from pywup.cmdtools.heatmap import main
    
    elif cmd == "collect":
        if debug:
            from cmdtools.collect import main
        else:
            from pywup.cmdtools.collect import main
    
    elif cmd == "bars":
        if debug:
            from cmdtools.bars import main
        else:
            from pywup.cmdtools.bars import main
    
    elif cmd == "backup":
        if debug:
            from cmdtools.backup import main
        else:
            from pywup.cmdtools.backup import main
    
    elif cmd == "q":
        if debug:
            from cmdtools.q import main
        else:
            from pywup.cmdtools.q import main
    
    elif cmd == "conf":
        if debug:
            from cmdtools.conf import main
        else:
            from pywup.cmdtools.conf import main

    elif cmd == "env":
        if debug:
            from cmdtools.env import main
        else:
            from pywup.cmdtools.env import main

    elif cmd == "cluster":
        if debug:
            from cmdtools.cluster import main
        else:
            from pywup.cmdtools.cluster import main

    else:
        return print("Unknown wup command:", cmd)
    
    main(args[1:])


if __name__ == "__main__":
    wup(True)
