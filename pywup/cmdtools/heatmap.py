#!/usr/bin/env python3

from collections import defaultdict

from pywup.services.general import find_column
from pywup.services.system import read_csv

import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import argparse
import math


def get_arguments(args):

    parser = argparse.ArgumentParser(description='Heatmap')

    # INITIAL PARAMETERS

    parser.add_argument('--data', type=str, required=True, metavar='FILEPATH',
                        help='data source (csv file)')

    parser.add_argument('--x', type=str, required=True, metavar='X_COLUMN',
                        help='x column in the data source')

    parser.add_argument('--y', type=str, required=True, metavar='Y_COLUMN',
                        help='y column in the data source')

    parser.add_argument('--z', type=str, required=True, metavar='Z_COLUMN',
                        help='z column in the data source')

    parser.add_argument('--tx', type=str, default=None, metavar='TRANSFORMATION',
                        help='use this to transform the z column. Variables are: data(matrix created from the data source, after aggregation), i(current row), x(column of x). Example: --tx "math.log2(data[i,x])"')

    parser.add_argument('--ty', type=str, default=None, metavar='TRANSFORMATION',
                        help='use this to transform the z column. Variables are: data(matrix created from the data source, after aggregation), i(current row), y(column of y). Example: --ty "math.log2(data[i,y])"')

    parser.add_argument('--tz', type=str, default=None, metavar='TRANSFORMATION',
                        help='use this to transform the z column. Variables are: data(matrix created from the data source, after aggregation), i(current row), z(column of z). Example: --tz "data[0,0] / data[i,z]"')

    parser.add_argument('--tzz', type=str, default=None, metavar='TRANSFORMATION',
                        help='use this to transform the z column when displaying. Variables are: data(matrix created and transformed, ready to be displayed), i(current row), j(current column). Example: --tzz "\"%d\" % int(float(data[i,x]))"')

    parser.add_argument('--o', type=str, default=None, metavar='FILEPATH',
                        help='save the output as a file. If not present, the result will be displayed in a gui')

    parser.add_argument('--size', type=float, default=None, nargs=2, metavar='W H',
                        help='size of output image')

    parser.add_argument('--title', type=str, default=None, metavar='FILEPATH',
                        help='save the output as a file. If not present, the result will be displayed in a gui')

    parser.add_argument('--xlabel', type=str, default=None, metavar='L',
                        help='label for the x axis')

    parser.add_argument('--ylabel', type=str, default=None, metavar='L',
                        help='label for the y axis')

    parser.add_argument('--verbose', type=bool, default=False,
                        help='print debug info')

    return parser.parse_args(args.all())


def map_labels(column):
    labels = []
    tmp = {}

    for i in range(column.shape[0]):
        l = column[i]
        if not l in tmp:
            tmp[l] = len(tmp)
            labels.append(l)

    return tmp, labels

def main(cmd, arg):
    # Parse arguments
    args = get_arguments(arg)

    # Read the data
    src = read_csv(args.data)
    headers = src[0,:]
    data = src[1:,:]

    if args.verbose:
        print("HEADERS")
        print(headers)
        
        print("DATA")
        print(data)

    # Locate headers
    x = find_column(headers, args.x)
    y = find_column(headers, args.y)
    z = find_column(headers, args.z)

    if args.verbose:
        print("COLUMNS: x={}, y={}, z={}".format(x, y, z))

    # Convert the z column to float
    for i in range(data.shape[0]):
        data[i,z] = float(data[i,z])

    # Select columns of interest
    data2 = data[:,[x, y, z]]

    if args.verbose:
        print("SELECTED COLUMNS (x, y, z)")
        print(data2)
    
    # Apply transformations
    if args.tx:
        for i in range(data.shape[0]):
            data2[i,0] = eval(args.tx)

    if args.ty:
        for i in range(data.shape[0]):
            data2[i,1] = eval(args.ty)

    if args.tz:
        for i in range(data.shape[0]):
            data2[i,2] = eval(args.tz)


    # Aggregate the results
    s = defaultdict(list)
    for i in range(data2.shape[0]):
        s[(data2[i, 0], data2[i, 1])].append(data2[i,2])

    xmap, xlabels = map_labels(data2[:,0])
    ymap, ylabels = map_labels(data2[:,1])

    # Create the heatmap data (data3)

    data = np.zeros((len(ymap), len(xmap)), np.float32)
    for key in s:
        values = s[key]
        xx, yy = key

        xxx = xmap[xx]
        yyy = ymap[yy]

        data[yyy, xxx] = np.mean(values)

    # Create the heatmap
    if args.size:
        w, h = args.size
        fig, ax = plt.subplots(figsize=(w, h))
    else:
        fig, ax = plt.subplots(figsize=(10,7))

    im = ax.imshow(data)

    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Intensity", rotation=-90, va="bottom")

    ax.set_xticks(np.arange(len(xmap)))
    ax.set_yticks(np.arange(len(ymap)))

    ax.set_xticklabels(xlabels)
    ax.set_yticklabels(ylabels)

    if args.ylabel:
        ax.set_ylabel(args.ylabel)
    
    if args.xlabel:
        ax.set_xlabel(args.xlabel)

    # Draw labels for each cell
    if args.tzz:
        for i in range(len(ymap)):
            for j in range(len(xmap)):
                value = eval(args.tzz)
                text = ax.text(j, i, value, ha="center", va="center", color="w")

    # Draw labels for x and y axis
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right",
             rotation_mode="anchor")

    plt.setp(ax.get_yticklabels(), rotation=30, ha="right",
             rotation_mode="anchor")

    # Set title
    if args.title:
        ax.set_title(args.title)

    fig.tight_layout()

    if args.o:
        plt.savefig(args.o)
    else:
        plt.show()
