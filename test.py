#!/usr/bin/python3

from sys import argv, exit

import time

if len(argv) != 4:
    print("Syntax: %s <P1> <P2> <P3>" % argv[0])
    exit(1)

name = argv
p1 = float(argv[1])
p2 = float(argv[2])
p3 = float(argv[3])

#time.sleep(2)

print("Full product:", p1 * p2 * p3)
print("Biggest:", max([p1, p2, p3]))
print("Minimum:", min([p1, p2, p3]))
print("Sum:", p1 + p2 + p3)

exit(0)

