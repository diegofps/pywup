from pywup.services.system import error, Params

import os

def main(cmd, args):
    p = Params(cmd, args)
    p.map("query", 1, None, "SQL to be run")
    p.map("--q", 0, None, "Quiet mode. Do not output headers in the output")

    if p.run():
        query = p.query
        quiet = p.__q

        if quiet:
            os.system("q -H -d \";\" \"" + query + "\"")
        else:
            os.system("q -H -d \";\" \"" + query + "\" -O")