from pywup.services.system import error, Params

import os

def main(cmd, args):
    p = Params(cmd, args)
    p.map("query", 1, None, "SQL to be run")
    p.map("--q", 0, None, "Quiet mode. Do not output headers in the output")
    p.map("--b", 0, None, "Enable beautify")

    if p.run():
        query = p.query
        quiet = p.__q
        beautify = p.__b

        cmd = "q -H -d \";\" \"" + query + "\""

        if not quiet:
            cmd += " -O"
        
        if beautify:
            cmd += " | column -t -s ';'"
        
        os.system(cmd)
