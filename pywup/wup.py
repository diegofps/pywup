#!/usr/bin/env python3

from pywup.services.system import abort, error, WupError

import sys
import os


def wup():
    try:
        args = sys.argv[1:]
        
        if len(args) == 0:
            return print("Missing wup command")

        cmd = args[0]
        
        if cmd == "heatmap":
            from pywup.cmdtools.heatmap import main
        
        elif cmd == "collect":
            from pywup.cmdtools.collect import main
        
        elif cmd == "bars":
            from pywup.cmdtools.bars import main
        
        elif cmd == "backup":
            from pywup.cmdtools.backup import main
        
        elif cmd == "q":
            from pywup.cmdtools.q import main
        
        elif cmd == "conf":
            from pywup.cmdtools.conf import main

        elif cmd == "env":
            from pywup.cmdtools.env import main

        elif cmd == "cluster":
            from pywup.cmdtools.cluster import main

        else:
            error("Unknown wup command:", cmd)

        main(args[1:])
    
    except WupError as e:
        abort(e.message)


if __name__ == "__main__":
    wup()
