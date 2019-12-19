import os

def main(argv):
    query = argv[0]
    os.system("q -H -d \";\" \"" + query + "\" -O")
