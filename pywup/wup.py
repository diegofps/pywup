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
    
    else:
        return print("Unknown wup command:", cmd)
    
    main(args[1:])


if __name__ == "__main__":
    wup(True)
