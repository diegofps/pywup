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
    
    fin = fin + "/"

    cmd = "rsync -r %s %s" % (fin, fout)
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
    
    cmd = "cp %s %s" % (fin, fout)
    #print("FILE:", cmd)
    os.system(cmd)

def parse_file(filepath, create):
    with open(filepath, "r") as fin:
        reader = csv.reader(fin, delimiter=';')
        
        for line, cells in enumerate(reader):
            
            if len(cells) != 3:
                print("error: Wrong number of cells in line. Expected 3, got", line)
            
            elif cells[0] == "folder":
                if create:
                    sync_folder(cells[1], cells[2])
                else:
                    sync_folder(cells[2], cells[1])
            
            elif cells[0] == "file":
                if create:
                    sync_file(cells[1], cells[2])
                else:
                    sync_file(cells[2], cells[1])
            
            else:
                print("error: Inline rule in line. Options are [file, folder], got", cells[0])

def main(argv):
    
    filepath = "./BackupConfig"
    create = True
    
    for t in argv:
        if t == "create":
            create = True
        elif t == "restore":
            create = False
        else:
            filepath = t
    
    parse_file(filepath, create)
