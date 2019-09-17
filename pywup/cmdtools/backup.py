#!/usr/bin/env python3

import csv
import pdb
import os

def sync_folder(fin, fout):
    
    fout = os.path.expanduser(fout)
    fin  = os.path.expanduser(fin)

    os.makedirs(os.path.dirname(fout), exist_ok=True)
    os.makedirs(os.path.dirname(fin), exist_ok=True)

    if fout.endswith("/") and fin.endswith("/"):
        fout = fout[:-1]
        fin  = fin[:-1]
    
    elif fout.endswith("/"):
        fout = fout + os.path.basename(fin)

    elif fin.endswith("/"):
        fin = fin + os.path.basename(fout)
    
    cmd = "rsync -rtu %s/* %s/ ; rsync -rtu %s/* %s/" % (fin, fout, fout, fin)
    #print("FOLDER:", cmd)
    os.system(cmd)

def sync_file(fin, fout):
    
    fout = os.path.expanduser(fout)
    fin  = os.path.expanduser(fin)
    
    if fout.endswith("/") and fin.endswith("/"):
        fout = fout[:-1]
        fin  = fin[:-1]
    
    elif fout.endswith("/"):
        fout = fout + os.path.basename(fin)

    elif fin.endswith("/"):
        fin = fin + os.path.basename(fout)
    
    os.makedirs(os.path.dirname(fout), exist_ok=True)
    os.makedirs(os.path.dirname(fin), exist_ok=True)
    
    cmd = "rsync -ut %s %s ; rsync -ut %s %s" % (fin, fout, fout, fin)
    #print("FILE:", cmd)
    os.system(cmd)

def parse_file(filepath):
    
    filepath = os.path.expanduser(filepath)
    filepath = os.path.abspath(filepath)
    root     = os.path.dirname(filepath)
    
    os.chdir(root)
    
    with open(filepath, "r") as fin:
        reader = csv.reader(fin, delimiter=';')
        
        for line, cells in enumerate(reader):
            
            if len(cells) != 3:
                print("error: Wrong number of cells in line. Expected 3, got", len(line))
            
            elif cells[0] == "folder":
                sync_folder(cells[1], cells[2])
            
            elif cells[0] == "file":
                sync_file(cells[1], cells[2])
            
            else:
                print("error: Inline rule in line. Options are [file, folder], got", cells[0])

def main(argv):
    filepath = "~/.wupbackup" if len(argv) == 0 else argv[0]
    parse_file(filepath)
