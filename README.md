# pywup
A small set of tools.

TODO: Expand this [markdown](https://guides.github.com/features/mastering-markdown/)

# How to install / update

```bash
pip3 install --upgrade pywup --user --no-cache-dir
```

If you cannot run the wup command after installation, check if the path to the folder .local/bin is in your PATH. If not, add the following to the end of your ~/.bashrc:

```
export PATH=/home/<YOUR_USERNAME>/.local/bin:$PATH
```

# The library 

## configure

This is a python library for creating template-based configure scripts.

```python
#!/usr/bin/env python3

from pywup.configure import *

mf = TemplateBuilder()

mf.compiler     = find_program_or_abort(["clang++", "g++"], "Compiler", "clang")
mf.python       = find_header_or_abort("m/Python.h", "Python header", "python3-dev")
mf.highgui      = find_header_or_abort("/highgui.hpp", "Opencv's highgui", "opencv-dev")
mf.imgproc      = find_header_or_abort("/imgproc.hpp", "Opencv's imgproc", "opencv-dev")
mf.valgrind_py  = find_file_or_abort("python3-devel/valgrind-python.supp", "valgrind suppression file for python3", "python3-dev")
mf.libimgcodecs = find_lib("libopencv_imgcodecs.so", "libopencv_imgcodecs")

mf.libs         = "-lopencv_core -lopencv_highgui -lopencv_imgproc -I../../wup/cpp/include"
mf.headers      = "-DPYTHON_H=$(PYTHON_H) -DHIGHGUI_H=$(HIGHGUI_H) -DIMGPROC_H=$(IMGPROC_H)"

if mf.libimgcodecs:
    mf.libs     += " -lopencv_imgcodecs"

mf.build("Makefile", """\
CC={compiler}
HIGHGUI_H={highgui}
PYTHON_H={python}
IMGPROC_H={imgproc}
VALGRIND_PYTHON={valgrind_py}

LIBS = {libs}
HEADERS= {headers}

all:
	$(CC) -fPIC -shared wup_wrapper.cpp -o libwup.so -Wall -O3 -std=c++11 $(LIBS) $(HEADERS)

run:
	$(CC) main.cpp -o main -Wall -O3 -std=c++11 $(LIBS) $(HEADERS)
	./main

debug:
	$(CC) main.cpp -o main -Wall -g -std=c++11 $(LIBS) $(HEADERS)
	gdb main

valgrind:
	$(CC) -fPIC -shared wup_wrapper.cpp -o libwup.so -Wall -O1 -g -std=c++11 $(LIBS) $(HEADERS)
	valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes --verbose --suppressions=$(VALGRIND_PYTHON) python3 main3.py --model wisard --dataset mnist 2> valgrind.out
""")
```

# wup

This is a command line utility for running experiments, plotting and executing repetitive tasks.

## collect

collect runs a program multiple times and collects outputs.

Example 1 - Permutate variables and collect outputs

* This will permutate the variables THREADS (arithmetic: 1, 3, 5, 7, ...) and JOBS (geometric: 1, 1.6, ...)
* For each configuration, the program will run 10 times
* For each execution, the following attributes will be collected: TRAIN_TIME, TEST_TIME and ACC
* The output will be saved in CSV format at wespa.csv
* The permutations values for each variable are passed to the program in the same order they are declared. Each "{}" is replaced by the variable value.

```bash
wup collect \
    --p TRAIN_TIME "Info: Time to train was ([-0-9\.e\+]+) μs" \
    --p TEST_TIME "Info: Time to test was ([-0-9\.e\+]+) μs" \
    --p ACC "Test Acc = ([0-9\.]+)" \
    --runs 10 \
    --va THREADS 1 17 2 \
    --vg JOBS 1 80000 1.6 \
    --o wespa.csv \
    --c "./wisard -createModel RamWisard -ramBits 28 -decoder classic -ramType prime \
            -train mnist ../data/emnist/byclass/emnist-byclass-train \
            -test mnist ../data/emnist/byclass/emnist-byclass-test \
            -times -numThreads {} -hashSize 18041 -jobsPerThread {} -bleaching Y -pPredict 2"
```

Example 2 - Collect multiple rows from the same command execution

* The parameter --n defines a line break, allowing us to collect multiple rows for the same execution.
* The parameter --log defines an output file to write extra details during the process.

```bash
wup collect \
    --n "[a-zA-Z0-9]+ : AvgIntersectionScore = [-0-9\.e\+]+  AvgCenterDistanceScore = [-0-9\.e\+]+" \
    --p DS_NAME "([a-zA-Z0-9]+) : AvgIntersectionScore = [-0-9\.e\+]+  AvgCenterDistanceScore = [-0-9\.e\+]+" \
    --p INTERSECTION "[a-zA-Z0-9]+ : AvgIntersectionScore = ([-0-9\.e\+]+)  AvgCenterDistanceScore = [-0-9\.e\+]+" \
    --p CENTER_DISTANCE "[a-zA-Z0-9]+ : AvgIntersectionScore = [-0-9\.e\+]+  AvgCenterDistanceScore = ([-0-9\.e\+]+)" \
    --runs 10 \
    --o "./collect.csv" \
    --log "./collect.log" \
    --c "./run_all.sh"
```

Example 3 - Multiple commands and parallelization

* Specify multiple --c to call multiple commands. When multiple commands are presented they will receive the same variables.
* Their output will also be concatenated, you probably want to use --n to separate them in distinct lines.
* The program will parse all their outputs as if they were continuous, one after the other.
* Use --jobs to define the number of parallel processes.
* Parallelization is be applied across parameter permutation and commands. If you have 16 permutations and 2 commands we have 32 parallel tasks.
* You may also use --jobs without multiple commands.
* You may also use --c with just one --jobs.
* Use parallelism to tune parameters and single process to measure times. When you are measuring execution time, multiple processes may slightly slow each other as they compete for resources.

```bash
wup collect \
    --n "[a-zA-Z0-9]+ : AvgIntersectionScore = [-0-9\.e\+]+  AvgCenterDistanceScore = [-0-9\.e\+]+" \
    --p DS_NAME "([a-zA-Z0-9]+) : AvgIntersectionScore = [-0-9\.e\+]+  AvgCenterDistanceScore = [-0-9\.e\+]+" \
    --p INTERSECTION "[a-zA-Z0-9]+ : AvgIntersectionScore = ([-0-9\.e\+]+)  AvgCenterDistanceScore = [-0-9\.e\+]+" \
    --p CENTER_DISTANCE "[a-zA-Z0-9]+ : AvgIntersectionScore = [-0-9\.e\+]+  AvgCenterDistanceScore = ([-0-9\.e\+]+)" \
    --jobs 4 \
    --runs 10 \
    --o "./collect.csv" \
    --log "./collect.log" \
    --c "./run.sh 'Basketball'" \
    --c "./run.sh 'Biker'" \
    --c "./run.sh 'Bird1'" \
    --c "./run.sh 'Bird2'"
```

## heatmap

heatmap receives a csv file and generates a heatmap.

```bash
wup heatmap \
    --data ./wespa.csv \
    --y "THREADS" \
    --x "JOBS" \
    --z "TEST_TIME" \
    --tz "data[0,z] / data[i,z]" \
    --tx "\"%d\" % int(float(data[i,x]))" \
    --ty "\"%d\" % int(float(data[i,y]))" \
    --tzz "\"%.2f\" % data[i,j]" \
    --title "Speedup (threads / blockSize)" \
    --size 10 4 \
    --o heatmap_wespa.png
```

## bars

Generates a bar graphic using one or more csv files.

```bash
wup bars \
    --load ./note.csv \
    --line THREADS TEST_TIME "note test" \
    --line THREADS TRAIN_TIME "note train" \
 \
    --load ./out.csv \
    --line THREADS TEST_TIME "wespa test" \
    --line THREADS TRAIN_TIME "wespa train"\
 \
    --title "Predict speedups (threads / speedup)" \
    --ty "y[0,0] / y[i,j]" \
    --ts "y[0,0]*s[i,j] / (y[i,j]**2)" \
    --tyy "\"%.2f\" % ty[i,j] if ty[i,j] else ''" \
    --tx "int(float(x[i]))" \
    --xlabel "Threads" \
    --ylabel "Speedup" \
    --barwidth 0.9 \
    --size 10 4 \
    --verbose \
    --o bars_parallelPredictSpeedup.png
```

## backup

Example ***~/Dropbox/backups/system/wup.bak*** file

```
file;~/.local/bin/macro_play;./local_bin/
file;~/.local/bin/macro_rec_start;./local_bin/
file;~/.local/bin/macro_rec_stop;./local_bin/
folder;~/.config/compton;./compton
file;~/.vimrc;./vimrc
folder;~/.config/i3;./i3
```

Invoke backup / restore

```bash
# This will copy files from system (left) to backup folder (right), overwriting any change or previous file in the backup folder.
wup backup create ~/Dropbox/backups/system/wup.bak

# This will copy files from the backup folder (right) to the system (left), overwriting any change or previous file in the system.
wup backup restore ~/Dropbox/backups/system/wup.bak

# This will sync all files and backup folders, copying the most recent one to the right direction. 
wup backup sync ~/Dropbox/backups/system/wup.bak
```
