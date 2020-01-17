from pywup.services.system import error

import os

def main(args):
    show_header = True
    query = None

    while args.has_next():
        if args.has_cmd():
            cmd = args.pop_cmd()

            if cmd == "--q":
                show_header = False

            else:
                error("Invalid parameter:", cmd)
            
        elif args.has_parameter():
            query = args.pop_parameter()

        else:
            error("Unexpected input: ", args.pop_next())
    
    if query is None:
        error("Missing query")
    
    if show_header:
        os.system("q -H -d \";\" \"" + query + "\" -O")
    else:
        os.system("q -H -d \";\" \"" + query + "\"")
