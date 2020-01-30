#!/usr/bin/python3

from pywup.services.system import colors, yprint, wprint, rprint
from collections import defaultdict
from subprocess import Popen

import hashlib
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


def aand(arr):
    for x in arr:
        if not x:
            return False
    return True


def parse(master, outputs, secret_n):
    o = os.read(master, 10240)

    os.write(sys.stdout.fileno(), o)

    if not o:
        return True
    
    last = 0
    i = 0

    linebreak = ord('\r')
    result = []

    while i != len(o):
        if o[i] == linebreak:
            result.append(o[last:i+1])
            last = i + 1
        
        i += 1
    
    result.append(o[last:i])

    if outputs:
        outputs[-1] = outputs[-1] + result[0]
        outputs.extend(result[1:])
    
    else:
        outputs.extend(result)

    for row in result:
        if secret_n in row:
            return False
    
    return True


class Wrapper:

    def __init__(self, num):
        import readline

        self.command = "bash"
        self.wup_env_open = b"/home/diego/Sources/pywup/pywup/wup.py env open\n"
        self.masters = []
        self.slaves = []
        self.popens = []
        
        self.start_secret = b"f897473fkjree78wefkfw89743jurewjlkhwufwe89343f"
        self.print_start_secret_cmd = b"echo '%s'\n" % self.start_secret
        self.start_secret_n = self.start_secret + b"\r"

        self.stop_secret  = b"odssd894gfmd9023milewjclkwmjiweofjweodwsdji324"
        self.print_stop_secret_cmd = b"echo '%s'\n" % self.stop_secret
        self.stop_secret_n = self.stop_secret + b"\r"

        for _ in range(num):
            master_fd, slave_fd = pty.openpty()
            popen = Popen(shlex.shlex(self.command),
                    preexec_fn=os.setsid,
                    stdin=slave_fd,
                    stdout=slave_fd,
                    stderr=slave_fd,
                    universal_newlines=True)
            
            self.popens.append(popen)
            self.masters.append(master_fd)
            self.slaves.append(slave_fd)
        
        for master in self.masters:
            os.write(master, self.wup_env_open)
    
    def loop(self):
        while True:
            try:
                sys.stdout.write(colors.WHITE)
                cmd = input(">> ").strip()
                sys.stdout.write(colors.RESET)

                if cmd == "":
                    continue

                elif cmd == "exit":
                    break
                    
                else:
                    self.print_start_secret()
                    self.execute(cmd)
                    self.print_stop_secret()
                    self.collect_outputs()
                    self.display_outputs_3()
            except EOFError:
                print()
                break
    
    def print_start_secret(self):
        for master in self.masters:
            os.write(master, self.print_start_secret_cmd)

    def execute(self, cmd):
        for master in self.masters:
            os.write(master, cmd.encode() + b"\n")

    def print_stop_secret(self):
        for master in self.masters:
            os.write(master, self.print_stop_secret_cmd)

    def collect_outputs(self):
        self.outputs = [[] for _ in self.masters]

        starts = [1 for _ in self.masters]
        stops  = [1 for _ in self.masters]

        while sum(starts) != 0 or sum(stops) != 0:
            r, w, e = select.select(self.masters, [], [])
        
            for i, master in enumerate(self.masters):
                if master in r:
                    found_start, found_stop = self.parse(master, self.outputs[i])

                    if found_start:
                        starts[i] = 0
                    
                    if found_stop:
                        stops[i] = 0
                    
                    break

    def display_outputs_0(self):
        for i, data in enumerate(self.outputs):

            print()
            yprint("--- OUTPUT FOR %d ---" % i)

            for j, row in enumerate(data):
                os.write(sys.stdout.fileno(), b"\n[%d]\n" % j)
                os.write(sys.stdout.fileno(), row)
    
    def display_outputs_1(self):
        for i, data in enumerate(self.outputs):

            print()
            yprint("--- OUTPUT FOR %d WAS ---" % i)
            state = 0

            for j, row in enumerate(data):
                if state == 0:
                    if self.start_secret_n in row:
                        state = 1
                
                elif state == 1:
                    if self.stop_secret in row:
                        break
                    else:
                        os.write(sys.stdout.fileno(), b"\n[%d]\n" % j)
                        os.write(sys.stdout.fileno(), row)
                
                else:
                    break
        
    def display_outputs_2(self, verbose=False):
        for i, data in enumerate(self.outputs):

            print()
            yprint("--- OUTPUT FOR %d WAS ---" % i)
            
            start = None
            stop = None

            for j, row in enumerate(data):
                if self.start_secret in row:
                    start = j + 2
                
                if stop is None and self.stop_secret in row:
                    stop = j

            if start is None or stop is None:
                for j, row in enumerate(data):
                    if verbose:
                        os.write(sys.stdout.fileno(), b"\n[%d]\n" % j)
                        os.write(sys.stdout.fileno(), row)
                    else:
                        os.write(sys.stdout.fileno(), row)
            
            else:
                for j in range(start, stop):
                    row = data[j]

                    if verbose:
                        os.write(sys.stdout.fileno(), b"\n[%d]\n" % j)
                        os.write(sys.stdout.fileno(), row)
                    else:
                        os.write(sys.stdout.fileno(), row)
    
    def display_outputs_3(self, verbose=False):
        hash_to_names = defaultdict(list)
        hash_to_outputs = {}

        for i, data in enumerate(self.outputs):

            #print()
            #yprint("--- ORIGINAL OUTPUT FOR %s WAS ---" % str(i))

            #for j, row in enumerate(data):
            #    os.write(sys.stdout.fileno(), b"\n[%d]\n" % j)
            #    os.write(sys.stdout.fileno(), row)
            
            start = None
            stop = None

            for j, row in enumerate(data):
                if self.start_secret in row:
                    start = j + 2
                
                if stop is None and self.stop_secret_n in row:
                    stop = j - 1

            #print("START", start, "STOP", stop)

            if start is not None and stop is not None:
                data = data[start:stop]
            
            m = hashlib.md5()
            
            for row in data:
                m.update(row)
            
            key = m.digest()
            name = str(i)

            hash_to_names[key].append(name)
            if not key in hash_to_outputs:
                hash_to_outputs[key] = data

        #rprint("------------------------------------------------------------")

        for key, data in hash_to_outputs.items():
            names = hash_to_names[key]

            print()
            yprint("--- OUTPUT FOR %s WAS ---" % ", ".join(names))

            for row in data:
                os.write(sys.stdout.fileno(), row)


    def parse(self, master, outputs):
        o = os.read(master, 10240)

        #os.write(sys.stdout.fileno(), o)

        if not o:
            return False, False
        
        last = 0
        i = 0

        linebreak = ord('\n')
        result = []

        while i != len(o):
            if o[i] == linebreak:
                result.append(o[last:i+1])
                last = i + 1
            
            i += 1
        
        result.append(o[last:i])

        if outputs:
            outputs[-1] = outputs[-1] + result[0]
            outputs.extend(result[1:])
        
        else:
            outputs.extend(result)

        found_start = False
        found_stop = False

        for row in result:
            if self.start_secret_n in row:
                found_start = True
            
            if self.stop_secret_n in row:
                found_stop = True
        
        return found_start, found_stop


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

    secret = b"reilvtoapmbjnkkrehfnewuihnsdjhweurynewvktykrt"
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

        outputs = [[], []]
        todos = [True, True]

        while aand(todos):

            r, w, e = select.select([master_fd1, master_fd2], [], [])
        
            if master_fd1 in r:
                todos[0] = parse(master_fd1, outputs[0], secret2) and todos[0]

            elif master_fd2 in r:
                todos[1] = parse(master_fd2, outputs[1], secret2) and todos[1]
        
        for i, data in enumerate(outputs):
            print()
            yprint("--- OUTPUT FOR %d WAS ---" % i)
            for i, row in enumerate(data):
                os.write(sys.stdout.fileno(), b"%d" % i)
                os.write(sys.stdout.fileno(), row)


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


def test4():
    Wrapper(3).loop()

test4()
  
