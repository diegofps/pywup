import os

def main(args):
    query = args.pop_parameter()
    os.system("q -H -d \";\" \"" + query + "\" -O")
