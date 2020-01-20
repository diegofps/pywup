#!/usr/bin/env python3

from collections import defaultdict
from types import SimpleNamespace

from pywup.services.system import read_csv, Args
from pywup.services.general import find_column

#import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import colorcet
import math
import sys


class Line:
    
    def __init__(self, args, src):
        if src is None:
            raise RuntimeError("You must call --data before calling --line")
        
        headers = src[0,:]
        data = src[1:,:]
        
        xheader = args.pop_parameter()
        yheader = args.pop_parameter()
        self.name = args.pop_parameter()
        
        myfilter = args.pop_parameter() if args.has_parameter() else None
        
        x = find_column(headers, xheader)
        y = find_column(headers, yheader)
        
        values = defaultdict(list)
        
        if myfilter:
            for i in range(data.shape[0]):
                if eval(myfilter):
                    key = data[i, x]
                    value = data[i, y]
                    values[key].append(float(value))

        else:
            for i in range(data.shape[0]):
                key = data[i, x]
                value = data[i, y]
                values[key].append(float(value))
        
        if len(values) == 0:
            print("Aborting: Filter for", self.name, "returned no item")
            sys.exit(0)
        
        self.means = {k:np.mean(values[k]) for k in values}
        self.stds = {k:np.std(values[k]) for k in values}
        self.keys = [k for k in values]
    
    def get_value(self, key):
        return self.means[key] if key in self.means else 0.0

    def get_std(self, key):
        return self.stds[key] if key in self.stds else 0.0
    
    def get_keys(self):
        return self.keys


def enhance_color(c):
    return c
    #f = lambda x : x * 0.8 + 0.2
    #r, g, b = mcolors.to_rgb(c)
    #return [f(r), f(g), f(b)]
    

def do_bars(args):
    
    if args.verbose:
        print("verbose:", args.verbose)
        print("barwidth:", args.barwidth)
        print("ylabel:", args.ylabel)
        print("xlabel:", args.xlabel)
        print("nostd:", args.nostd)
        print("title:", args.title)
        print("size:", args.size)
        print("tyy:", args.tyy)
        print("tx:", args.tx)
        print("ts:", args.ts)
        print("ty:", args.ty)
    
    # Detect all values for x (we need this to calculate the data size)
    xvals = {}
    
    for line in args.lines:
        for key in line.get_keys():
            if not key in xvals:
                xvals[key] = len(xvals)
    
    numRows = len(xvals)
    numCols = len(args.lines)
    
    
    ###### Create the original data ######
    
    y = np.zeros((numRows, numCols), np.float32)
    s = np.zeros((numRows, numCols), np.float32)
    x = [None] * numRows
    
    for key in xvals:
        i = xvals[key]
        x[i] = key
        
        for j, line in enumerate(args.lines):
            y[i, j] = line.get_value(key)
            s[i, j] = line.get_std(key)
    
    if args.verbose:
        print("ORIGINAL DATA")
        print("x:")
        print(x)
        print("y:")
        print(y)
        print("s:")
        print(s)
    
    ###### Create the transformed data ######
    
    # Transform x axis
    if args.tx:
        tx = [None] * numRows
        for i in range(numRows):
            tx[i] = eval(args.tx)
    else:
        tx = x
    
    # Transform y axis
    if args.ty:
        ty = np.zeros((numRows, numCols), np.float32)
        for i in range(numRows):
            for j in range(numCols):
                ty[i, j] = eval(args.ty)
    else:
        ty = y
    
    # Transform s axis
    if args.ts:
        ts = np.zeros((numRows, numCols), np.float32)
        for i in range(numRows):
            for j in range(numCols):
                ts[i, j] = eval(args.ts)
    else:
        ts = s
    
    if args.verbose:
        print("TRANSFORMED DATA")
        print("tx:")
        print(tx)
        print("ty:")
        print(ty)
        print("ts:")
        print(ts)
    
    ###### Create labels for the bar top ######
    
    if args.tyy:
        cells = np.zeros((numRows, numCols), object)
        for i in range(numRows):
            for j in range(numCols):
                cells[i,j] = eval(args.tyy)
    
    
    ######### Do the plotting ###########
    
    # Set img size
    fig, ax = plt.subplots(figsize=args.size)
    
    # Set bar width
    width = args.barwidth / len(args.lines)
    
    # Pick the color palette
    colors = eval(args.palette)
    
    # Set bars
    rects = []
    ind = np.arange(numRows)
    for j in range(numCols):
        off = [k + ( -((len(args.lines) - 1) / 2) + j) * width for k in ind]
        c = enhance_color(colors[j * len(colors) // numCols])
        line = args.lines[j]
        err = ts[:,j]
        yy = ty[:,j]
        
        if args.nostd:
            bars = ax.bar(off, yy, width, label=line.name, color=c)
        else:
            bars = ax.bar(off, yy, width, yerr=err, label=line.name, color=c)
        
        for i, rect in enumerate(bars):
            rect.text = cells[i,j]
            rect.label_height = ty[i,j] + ts[i,j]
        
        rects.append(bars)
    
    # Set x label
    if args.xlabel:
        ax.set_xlabel(args.xlabel)
    
    # Set y label
    if args.ylabel:
        ax.set_ylabel(args.ylabel)
    
    # Set the x ticks
    ax.set_xticks(ind)
    ax.set_xticklabels(tx)
    
    # Draw labels
    ax.legend()
    
    # Set title
    if args.title:
        ax.set_title(args.title)
    
    # Draw labels on top of each bar
    if args.tyy:
        for bars in rects:
            for rect in bars:
                text = rect.text
                xx = rect.get_x() + rect.get_width() * .5
                yy = rect.label_height
                ax.text(xx, yy, text, ha='center', va='bottom', fontsize=args.labelsize)
 
    # Finish and display / save
    fig.tight_layout()

    if args.o:
        plt.savefig(args.o)
    else:
        plt.show()


def main(cmd, args):

    b = SimpleNamespace()
    src = None
    
    b.palette = 'colorcet.rainbow_bgyrm_35_85_c69'
    b.verbose = False
    b.barwidth = 0.9
    b.ylabel = None
    b.xlabel = None
    b.nostd = False
    b.labelsize = 8
    b.size = (10,7)
    b.title = None
    b.tyy = None
    b.tx = None
    b.ts = None
    b.ty = None
    b.o = None
    b.lines = []

    while args.has_next():
        cmd = args.pop_cmd()

        if cmd == "--load":
            filepath = args.pop_parameter()
            src = read_csv(filepath)

        elif cmd == "--line":
            b.lines.append(Line(args, src))

        elif cmd == "--size":
            b.size = (float(args.pop_parameter()), float(args.pop_parameter()))

        elif cmd == "--title":
            b.title = args.pop_parameter()

        elif cmd == "--xlabel":
            b.xlabel = args.pop_parameter()

        elif cmd == "--ylabel":
            b.ylabel = args.pop_parameter()

        elif cmd == "--tx":
            b.tx = args.pop_parameter()

        elif cmd == "--ty":
            b.ty = args.pop_parameter()

        elif cmd == "--ts":
            b.ts = args.pop_parameter()

        elif cmd == "--tyy":
            b.tyy = args.pop_parameter()

        elif cmd == "--o":
            b.o = args.pop_parameter()
        
        elif cmd == "--barwidth":
            b.barwidth = float(args.pop_parameter())
        
        elif cmd == "--nostd":
            b.nostd = True
        
        elif cmd == "--verbose":
            b.verbose = True
        
        elif cmd == "--palette":
            b.palette = args.pop_parameter()

        elif cmd == "--labelsize":
            b.labelsize = int(args.pop_parameter())

    do_bars(b)
