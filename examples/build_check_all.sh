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

time python2 block.py
python2 -m shedskin block && make
time ./block

time python2 kanoodle.py
python2 -m shedskin kanoodle && make
time ./kanoodle

time python2 kmeanspp.py
python2 -m shedskin kmeanspp && make
time ./kmeanspp

time python2 loop.py
python2 -m shedskin loop && make
time ./loop

time python2 mandelbrot.py
python2 -m shedskin mandelbrot && make
time ./mandelbrot

python2 -m shedskin -e mandelbrot2 && make && python2 -c "import mandelbrot2; assert mandelbrot2.__file__.endswith('.so')"
echo CHECK: mandelbrot2_main!

cd mm
python2 -m shedskin -e mastermind && make && python2 -c "import mastermind; assert mastermind.__file__.endswith('.so')"
cd ..
echo CHECK: mastermind_main!

time python2 mastermind2.py
python2 -m shedskin mastermind2 && make
time ./mastermind2

time python2 minpng.py
python2 -m shedskin minpng && make
time ./minpng
echo CHECK: out.png, out.ppm!

python2 -m shedskin -Llib msp_ss && make
time ./msp_ss

time python2 mwmatching.py
python2 -m shedskin mwmatching && make
time ./mwmatching

time python2 nbody.py
python2 -m shedskin nbody && make
time ./nbody

time python2 neural1.py --test
python2 -m shedskin neural1 && make
time ./neural1 --test

time python2 neural2.py
python2 -m shedskin neural2 && make
time ./neural2

time python2 oliva2.py
python2 -m shedskin oliva2 && make
time ./oliva2
echo CHECK: oliva.pgm!

time python2 othello.py
python2 -m shedskin othello && make
time ./othello

time python2 pisang.py
python2 -m shedskin pisang && make
time ./pisang

time python2 pygmy.py
python2 -m shedskin pygmy && make
time ./pygmy
echo CHECK: test.ppm!

time python2 yopyra.py
python2 -m shedskin yopyra && make
time ./yopyra
echo CHECK: scene.txt.ppm!

time python2 mao.py
python2 -m shedskin -r mao && make
time ./mao
echo CHECK: ao_py.ppm!

time python2 minilight.py
python2 -m shedskin -r minilight && make
time ./minilight
echo CHECK: ml/cornellbox.txt.ppm!

time python2 path_tracing.py
python2 -m shedskin -r path_tracing && make
time ./path_tracing
echo CHECK: pt.ppm!

time python2 plcfrs.py
python2 -m shedskin plcfrs && make
time ./plcfrs

python2 -m shedskin -be pygasus && make && python2 -c "import pygasus; assert pygasus.__file__.endswith('.so')"

cd pylot
python2 -m shedskin -be SimpleGeometry && make && python2 -c "import SimpleGeometry; assert SimpleGeometry.__file__.endswith('.so')"
cd ..

time python2 pystone.py
python2 -m shedskin pystone && make
time ./pystone

cd quameon
time python2 sto_atom.py
python2 -m shedskin sto_atom && make
time ./sto_atom
cd ..

time python2 richards.py
python2 -m shedskin richards && make
time ./richards

time python2 rdb.py -h
python2 -m shedskin rdb && make
time ./rdb -h

time python2 rsync.py
python2 -m shedskin -Llib rsync && make
time ./rsync

time python2 rubik.py
python2 -m shedskin rubik && make
time ./rubik

time python2 rubik2.py
python2 -m shedskin rubik2 && make
time ./rubik2

time python2 sat.py
python2 -m shedskin sat && make
time ./sat

time python2 score4.py
python2 -m shedskin score4 && make
time ./score4

time python2 sieve.py
python2 -m shedskin sieve && make
time ./sieve

time python2 sha.py hoempadoempa
python2 -m shedskin -l sha && make
time ./sha hoempadoempa

time python2 sokoban.py
python2 -m shedskin sokoban && make
time ./sokoban

time python2 solitaire.py -test
python2 -m shedskin solitaire && make
time ./solitaire -test

python2 -m shedskin -web stereo && make && python2 -c "import stereo; assert stereo.__file__.endswith('.so')"

time python2 sudoku1.py
python2 -m shedskin sudoku1 && make
time ./sudoku1

time python2 sudoku2.py
python2 -m shedskin sudoku2 && make
time ./sudoku2

time python2 sudoku3.py
python2 -m shedskin sudoku3 && make
time ./sudoku3

time python2 sudoku4.py
python2 -m shedskin sudoku4 && make
time ./sudoku4

time python2 sudoku5.py
python2 -m shedskin sudoku5 && make
time ./sudoku5

time python2 sunfish.py
python2 -m shedskin sunfish && make
time ./sunfish

time python2 tictactoe.py
python2 -m shedskin tictactoe && make
time ./tictactoe

time python2 timsort.py
python2 -m shedskin timsort && make
time ./timsort

time python2 TarsaLZP.py
python2 -m shedskin TarsaLZP && make
time ./TarsaLZP

time python2 TonyJpegDecoder.py
python2 -m shedskin TonyJpegDecoder && make
time ./TonyJpegDecoder
echo CHECK: tiger1.bmp!

time python2 voronoi.py
python2 -m shedskin voronoi && make
time ./voronoi

python2 -m shedskin voronoi2 && make

python2 -m shedskin WebServer && make
