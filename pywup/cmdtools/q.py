from pywup.services.system import error, Params

import os

def main(cmd, args):
    params = Params(cmd, args)
    params.map("query", 1, None, "SQL to be run")
    params.map("--q", 0, None, "Do not output headers in the output")

    if params.run():
        query = params.get("query")
        quiet = params.has("--q")

        if quiet:
            os.system("q -H -d \";\" \"" + query + "\"")
        else:
            os.system("q -H -d \";\" \"" + query + "\" -O")