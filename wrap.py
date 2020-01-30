#!/usr/bin/python3

from subprocess import Popen

import os
import sys
import select
import termios
import tty
import pty
import shlex

command = shlex.shlex("wup env open")

old_tty = termios.tcgetattr(sys.stdin)

try:
    tty.setraw(sys.stdin.fileno())

    master_fd1, slave_fd1 = pty.openpty()
    p1 = Popen(shlex.shlex("wup env open"),
              preexec_fn=os.setsid,
              stdin=slave_fd1,
              stdout=slave_fd1,
              stderr=slave_fd1,
              universal_newlines=True)
      
    master_fd2, slave_fd2 = pty.openpty()
    p2 = Popen(shlex.shlex("wup env open"),
              preexec_fn=os.setsid,
              stdin=slave_fd2,
              stdout=slave_fd2,
              stderr=slave_fd2,
              universal_newlines=True)

    buffer1 = []
    buffer2 = []

    #os.write(master_fd1, "ls /\n".encode())
    #os.write(master_fd2, "ls /\n".encode())
    
    os.write(sys.stdout.fileno(), ">> ".encode())
    os.write(sys.stdout.fileno(), (str(ord("\r"))+"\n").encode())
    
    while True:
        #r, w, e = select.select([sys.stdin, master_fd1, master_fd2], [], [])
        r, w, e = select.select([sys.stdin], [], [])
        
        d = os.read(sys.stdin.fileno(), 10240)
        last = 0
        i = 0
        
        os.write(sys.stdout.fileno(), str(len(d)).encode())
        os.write(sys.stdout.fileno(), d)
        
        if d[0] == ord("a"):
            break
        
        continue
        #os.write(sys.stdout.fileno(), (str(d[0])+"\n").encode())
        
        for char in d:
            if char == '\r':
                os.write(sys.stdout.fileno(), d[last:i])
                os.write(sys.stdout.fileno(), ">> ".encode())
                last = i
            
            elif char == 'a':
                sys.exit(0)
            
            i+=1
        
        #os.write(sys.stdout.fileno(), ("%d %d\n" % (last, i)).encode())
        os.write(sys.stdout.fileno(), d[last:i])
        
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

sys.exit(0)


while p1.poll() is None and p2.poll() is None:
    r, w, e = select.select([sys.stdin, master_fd1, master_fd2], [], [])
    
    if sys.stdin in r:
        d = os.read(sys.stdin.fileno(), 10240)
        os.write(master_fd1, d)
        os.write(master_fd2, d)
    
    elif master_fd1 in r:
        o = os.read(master_fd1, 10240)
        if o:
            os.write(sys.stdout.fileno(), o)

    elif master_fd2 in r:
        o = os.read(master_fd2, 10240)
        if o:
            os.write(sys.stdout.fileno(), o)
  
