#!/bin/bash

set -e
set -x

export PYTHONPATH=..:../..

time python2 ant.py
python2 -m shedskin ant && make
time ./ant

time python2 amaze.py
python2 -m shedskin amaze && make
time ./amaze

python2 -m shedskin -e astar && make && python2 -c "import astar; assert astar.__file__.endswith('.so')"
echo CHECK: astar_main!

time python2 bh.py -b 5000 -m
python2 -m shedskin bh && make
time ./bh -b 5000 -m

time python2 brainfuck.py
python2 -m shedskin brainfuck && make
time ./brainfuck

cd c64
python2 -m shedskin -boe c64 && make && python2 -c "import c64; assert c64.__file__.endswith('.so')"
cd ..
echo CHECK: c64_main!

time python2 chess.py
python2 -m shedskin chess && make
time ./chess

time python2 dijkstra.py
python2 -m shedskin dijkstra && make
time ./dijkstra

time python2 dijkstra2.py
python2 -m shedskin dijkstra2 && make
time ./dijkstra2

time python2 chaos.py
python2 -m shedskin chaos && make
time ./chaos
echo CHECK: py.ppm!

time python2 chull.py
python2 -m shedskin chull && make
time ./chull

python2 -m shedskin -e circle && make && python2 -c "import circle; assert circle.__file__.endswith('.so')"
echo CHECK: circle_main!

python2 -m shedskin -e fysphun && make && python2 -c "import fysphun; assert fysphun.__file__.endswith('.so')"
echo CHECK: fysphun_main!

time python2 genetic.py
python2 -m shedskin genetic && make
time ./genetic

time python2 genetic2.py
python2 -m shedskin genetic2 && make
time ./genetic2

time python2 go.py
python2 -m shedskin -b go && make
time ./go

cd Gh0stenstein
python2 -m shedskin -bwe world_manager && make && python2 -c "import world_manager; assert world_manager.__file__.endswith('.so')"
cd ..
echo CHECK: gs_main!

time python2 hq2x.py
python2 -m shedskin hq2x && make
time ./hq2x

time python2 life.py
python2 -m shedskin life && make
time ./life

python2 -m shedskin -e pylife && make && python2 -c "import pylife; assert pylife.__file__.endswith('.so')"
echo CHECK: pylife_main!

time python2 linalg.py
python2 -m shedskin linalg && make
time ./linalg

time python2 LZ2.py
python2 -m shedskin LZ2 && make
time ./LZ2

time python2 ac_encode.py
python2 -m shedskin ac_encode && make
time ./ac_encode

time python2 adatron.py
python2 -m shedskin adatron && make
time ./adatron
