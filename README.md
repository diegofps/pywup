# pywup
A small set of tools 

TODO: Expand this using [Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)

# configure

This is a python library for creating template based configure scripts.

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

collect runs a program multiple times and collects outputs

```bash
./wup collect \
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
            -times -numThreads 4 -hashSize 18041 -jobsPerThread 10000 -bleaching Y -pPredict 2"
```

## heatmap

heatmap receives a csv file and generates a heatmap 

```bash
./wup heatmap \
    --data ./wespa.csv \
    --y "THREADS" \
    --x "JOBS" \
    --z "TEST_TIME" \
    --tz "data[0,z] / data[i,z]" \
    --tx "\"%d\" % int(float(data[i,x]))" \
    --ty "\"%d\" % int(float(data[i,y]))" \
    --tzz "\"%.2f\" % data[i,j]" \
    --title "Speedup (threads / blockSize) x 10" \
    --size 10 4 \
    --o heatmap_wespa.png
```
