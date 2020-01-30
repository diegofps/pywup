#!/usr/bin/python3

from pywup.services.system import yprint
from subprocess import Popen

import termios
import string
import select
import shlex
import sys
import tty
import pty
import os


def test0():

    command = "python3 /home/diego/Sources/pywup/pywup/wup.py env open"

    master_fd1, slave_fd1 = pty.openpty()
    p1 = Popen(shlex.shlex(command),
            preexec_fn=os.setsid,
            stdin=slave_fd1,
            stdout=slave_fd1,
            stderr=slave_fd1,
            universal_newlines=True)
    
    master_fd2, slave_fd2 = pty.openpty()
    p2 = Popen(shlex.shlex(command),
            preexec_fn=os.setsid,
            stdin=slave_fd2,
            stdout=slave_fd2,
            stderr=slave_fd2,
            universal_newlines=True)

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
  


def test1():
    command = "python3 /home/diego/Sources/pywup/pywup/wup.py env open"

    old_tty = termios.tcgetattr(sys.stdin)

    try:
        tty.setraw(sys.stdin.fileno())

        master_fd1, slave_fd1 = pty.openpty()
        p1 = Popen(shlex.shlex(command),
                preexec_fn=os.setsid,
                stdin=slave_fd1,
                stdout=slave_fd1,
                stderr=slave_fd1,
                universal_newlines=True)
        
        master_fd2, slave_fd2 = pty.openpty()
        p2 = Popen(shlex.shlex(command),
                preexec_fn=os.setsid,
                stdin=slave_fd2,
                stdout=slave_fd2,
                stderr=slave_fd2,
                universal_newlines=True)

        os.write(sys.stdout.fileno(), ">> ".encode())
        printable = string.printable.encode()
        finished = False
        cmd_chars = []
        
        while not finished:
            #r, w, e = select.select([sys.stdin, master_fd1, master_fd2], [], [])
            r, w, e = select.select([sys.stdin], [], [])
            
            d = os.read(sys.stdin.fileno(), 10240)
            
            for x in range(len(d)):
                c = d[x]
                bc = d[x:x+1]

                if bc in printable:
                    cmd_chars.append(c)
                    os.write(sys.stdout.fileno(), bc)

                if c == ord('\r'):
                    cmd = bytes(cmd_chars[:-1])
                    cmd_chars.clear()

                    if cmd == b"exit":
                        os.write(sys.stdout.fileno(), b"\r\n")
                        finished = True
                        break
                    else:
                        os.write(sys.stdout.fileno(), b"\nUnknown command: " + cmd + b"\r")
                    
                    os.write(sys.stdout.fileno(), b"\n>> ")
            
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

    sys.exit(0)


def test2():
    import readline

    command = "bash"
    wup_env_open = b"/home/diego/Sources/pywup/pywup/wup.py env open\n"

    master_fd1, slave_fd1 = pty.openpty()
    p1 = Popen(shlex.shlex(command),
            preexec_fn=os.setsid,
            stdin=slave_fd1,
            stdout=slave_fd1,
            stderr=slave_fd1,
            universal_newlines=True)
    
    master_fd2, slave_fd2 = pty.openpty()
    p2 = Popen(shlex.shlex(command),
            preexec_fn=os.setsid,
            stdin=slave_fd2,
            stdout=slave_fd2,
            stderr=slave_fd2,
            universal_newlines=True)

    secret = b"reilvtoapmbjnkkrehfnewuihnsdjhweurynewvktykrtjsncfjbvterx"
    secret2 = secret + b"\r"
    print_secret = b"echo '%s'\n" % secret

    os.write(master_fd1, wup_env_open)
    os.write(master_fd2, wup_env_open)

    while True:
        try:
            cmd = input(">> ").strip()
        except EOFError:
            print()
            break

        if cmd == "":
            continue

        if cmd == "exit":
            break
        
        os.write(master_fd1, cmd.encode() + b"\n")
        os.write(master_fd2, cmd.encode() + b"\n")

        os.write(master_fd1, print_secret)
        os.write(master_fd2, print_secret)

        outputs = [b"", b""]
        todos = [1, 1]

        while sum(todos) != 0:

            r, w, e = select.select([sys.stdin, master_fd1, master_fd2], [], [])
        
            if sys.stdin in r:
                d = os.read(sys.stdin.fileno(), 10240)
            
            elif master_fd1 in r:
                
                o = os.read(master_fd1, 10240)
                #os.write(sys.stdout.fileno(), o)

                if o:
                    outputs[0] = outputs[0] + o
                    if secret2 in outputs[0]:
                        todos[0] = 0

            elif master_fd2 in r:
                o = os.read(master_fd2, 10240)
                #os.write(sys.stdout.fileno(), o)
                
                if o:
                    outputs[1] = outputs[1] + o
                    if secret2 in outputs[1]:
                        todos[1] = 0
        
        for i, data in enumerate(outputs):
            print()
            yprint("--- OUTPUT FOR %d WAS ---" % i)
            os.write(sys.stdout.fileno(), data)


def test3():
    import cmd, sys

    class TurtleShell(cmd.Cmd):
        intro = 'Welcome to the turtle shell.   Type help or ? to list commands.\n'
        prompt = '(turtle) '
        file = None

        # ----- basic turtle commands -----
        def do_forward(self, arg):
            'Move the turtle forward by the specified distance:  FORWARD 10'
            print('Move the turtle forward by the specified distance:  FORWARD 10')
            
        def do_right(self, arg):
            'Turn turtle right by given number of degrees:  RIGHT 20'
            print('Turn turtle right by given number of degrees:  RIGHT 20')
            
        def do_left(self, arg):
            'Turn turtle left by given number of degrees:  LEFT 90'
            print('Turn turtle left by given number of degrees:  LEFT 90')
            
        def do_goto(self, arg):
            'Move turtle to an absolute position with changing orientation.  GOTO 100 200'
            print('Move turtle to an absolute position with changing orientation.  GOTO 100 200')
            
        def do_home(self, arg):
            'Return turtle to the home position:  HOME'
            print('Return turtle to the home position:  HOME')
            
        def do_circle(self, arg):
            'Draw circle with given radius an options extent and steps:  CIRCLE 50'
            print('Draw circle with given radius an options extent and steps:  CIRCLE 50')
            
        def do_position(self, arg):
            'Print the current turtle position:  POSITION'
            print('Print the current turtle position:  POSITION')
            
        def do_heading(self, arg):
            'Print the current turtle heading in degrees:  HEADING'
            print('Print the current turtle heading in degrees:  HEADING')
            
        def do_color(self, arg):
            'Set the color:  COLOR BLUE'
            print('Set the color:  COLOR BLUE')
            
        def do_undo(self, arg):
            'Undo (repeatedly) the last turtle action(s):  UNDO'
            print('Undo (repeatedly) the last turtle action(s):  UNDO')

        def do_reset(self, arg):
            'Clear the screen and return turtle to center:  RESET'
            print('Clear the screen and return turtle to center:  RESET')

        def do_bye(self, arg):
            'Stop recording, close the turtle window, and exit:  BYE'
            print('Thank you for using Turtle')
            return True

    TurtleShell().cmdloop()


test2()
  
