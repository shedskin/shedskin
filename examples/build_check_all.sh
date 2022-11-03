#!/bin/bash

set -e
set -x

export PYTHONPATH=..:../..

#time python2 ant.py
#python2 -m shedskin ant && make
#time ./ant
#
#time python2 amaze.py
#python2 -m shedskin amaze && make
#time ./amaze
#
#python2 -m shedskin -e astar && make && python2 -c "import astar; assert astar.__file__.endswith('.so')"
#
#time python2 bh.py -b 5000 -m
#python2 -m shedskin bh && make
#time ./bh -b 5000 -m
#
#time python2 brainfuck.py
#python2 -m shedskin brainfuck && make
#time ./brainfuck

cd c64
python2 -m shedskin -boe c64 && make && python2 -c "import c64; assert c64.__file__.endswith('.so')"
cd ..
