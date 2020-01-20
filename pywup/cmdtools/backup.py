#!/usr/bin/env python3

import csv
import os

def sync_folder(fin, fout, to_left, to_right):
    
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
    
    if to_right:
        cmd = "rsync -rtu %s/* %s/" % (fin, fout)
        #print("FOLDER:", cmd)
        os.system(cmd)
    
    if to_left:
        cmd = "rsync -rtu %s/* %s/" % (fout, fin)
        #print("FOLDER:", cmd)
        os.system(cmd)

def sync_file(fin, fout, to_left, to_right):
    
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
    
    if to_right:
        cmd = "rsync -ut %s %s" % (fin, fout)
        #print("FILE:", cmd)
        os.system(cmd)
    
    if to_left:
        cmd = "rsync -ut %s %s" % (fout, fin)
        #print("FILE:", cmd)
        os.system(cmd)

def parse_file(filepath, to_left, to_right):
    
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
                sync_folder(cells[1], cells[2], to_left, to_right)
            
            elif cells[0] == "file":
                sync_file(cells[1], cells[2], to_left, to_right)
            
            else:
                print("error: Inline rule in line. Options are [file, folder], got", cells[0])

def main(cmd, args):
    cmd = args.pop_parameter()
    filepath = args.pop_parameter() if args.has_parameter() else "~/.wupbackup"
    
    if cmd == "create":
        parse_file(filepath, False, True)
    
    elif cmd == "restore":
        parse_file(filepath, True, False)
    
    elif cmd == "sync":
        parse_file(filepath, True, True)
    
    else:
        print("Unknown command: ", cmd);
