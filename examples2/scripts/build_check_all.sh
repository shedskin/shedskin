#!/bin/bash

set -e
set -x

export PYTHONPATH=..:../..

time python3 ant.py
python3 -m shedskin ant && make
time ./ant

time python3 amaze.py
python3 -m shedskin amaze && make
time ./amaze

python3 -m shedskin -e astar && make && python3 -c "import astar; assert astar.__file__.endswith('.so')"
echo CHECK: astar_main!

time python3 bh.py -b 5000 -m
python3 -m shedskin bh && make
time ./bh -b 5000 -m

time python3 brainfuck.py
python3 -m shedskin brainfuck && make
time ./brainfuck

cd c64
python3 -m shedskin -boe c64 && make && python3 -c "import c64; assert c64.__file__.endswith('.so')"
cd ..
echo CHECK: c64_main!

time python3 chess.py
python3 -m shedskin chess && make
time ./chess

time python3 dijkstra.py
python3 -m shedskin dijkstra && make
time ./dijkstra

time python3 dijkstra2.py
python3 -m shedskin dijkstra2 && make
time ./dijkstra2

time python3 chaos.py
python3 -m shedskin chaos && make
time ./chaos
echo CHECK: py.ppm!

time python3 chull.py
python3 -m shedskin chull && make
time ./chull

python3 -m shedskin -e circle && make && python3 -c "import circle; assert circle.__file__.endswith('.so')"
echo CHECK: circle_main!

python3 -m shedskin -e fysphun && make && python3 -c "import fysphun; assert fysphun.__file__.endswith('.so')"
echo CHECK: fysphun_main!

time python3 genetic.py
python3 -m shedskin genetic && make
time ./genetic

time python3 genetic2.py
python3 -m shedskin genetic2 && make
time ./genetic2

time python3 go.py
python3 -m shedskin -b go && make
time ./go

cd Gh0stenstein
python3 -m shedskin -bwe world_manager && make && python3 -c "import world_manager; assert world_manager.__file__.endswith('.so')"
cd ..
echo CHECK: gs_main!

time python3 hq2x.py
python3 -m shedskin hq2x && make
time ./hq2x

time python3 life.py
python3 -m shedskin life && make
time ./life

python3 -m shedskin -e pylife && make && python3 -c "import pylife; assert pylife.__file__.endswith('.so')"
echo CHECK: pylife_main!

time python3 linalg.py
python3 -m shedskin linalg && make
time ./linalg

time python3 LZ2.py
python3 -m shedskin LZ2 && make
time ./LZ2

time python3 ac_encode.py
python3 -m shedskin ac_encode && make
time ./ac_encode

time python3 adatron.py
python3 -m shedskin adatron && make
time ./adatron

time python3 block.py
python3 -m shedskin block && make
time ./block

time python3 kanoodle.py
python3 -m shedskin kanoodle && make
time ./kanoodle

time python3 kmeanspp.py
python3 -m shedskin kmeanspp && make
time ./kmeanspp

time python3 loop.py
python3 -m shedskin loop && make
time ./loop

time python3 mandelbrot.py
python3 -m shedskin mandelbrot && make
time ./mandelbrot

python3 -m shedskin -e mandelbrot2 && make && python3 -c "import mandelbrot2; assert mandelbrot2.__file__.endswith('.so')"
echo CHECK: mandelbrot2_main!

cd mm
python3 -m shedskin -e mastermind && make && python3 -c "import mastermind; assert mastermind.__file__.endswith('.so')"
cd ..
echo CHECK: mastermind_main!

time python3 mastermind2.py
python3 -m shedskin mastermind2 && make
time ./mastermind2

time python3 minpng.py
python3 -m shedskin minpng && make
time ./minpng
echo CHECK: out.png, out.ppm!

python3 -m shedskin -Llib msp_ss && make
time ./msp_ss

time python3 mwmatching.py
python3 -m shedskin mwmatching && make
time ./mwmatching

time python3 nbody.py
python3 -m shedskin nbody && make
time ./nbody

time python3 neural1.py --test
python3 -m shedskin neural1 && make
time ./neural1 --test

time python3 neural2.py
python3 -m shedskin neural2 && make
time ./neural2

time python3 oliva2.py
python3 -m shedskin oliva2 && make
time ./oliva2
echo CHECK: oliva.pgm!

time python3 othello.py
python3 -m shedskin othello && make
time ./othello

time python3 pisang.py
python3 -m shedskin pisang && make
time ./pisang

time python3 pygmy.py
python3 -m shedskin pygmy && make
time ./pygmy
echo CHECK: test.ppm!

time python3 yopyra.py
python3 -m shedskin yopyra && make
time ./yopyra
echo CHECK: scene.txt.ppm!

time python3 mao.py
python3 -m shedskin -r mao && make
time ./mao
echo CHECK: ao_py.ppm!

time python3 minilight.py
python3 -m shedskin -r minilight && make
time ./minilight
echo CHECK: ml/cornellbox.txt.ppm!

time python3 path_tracing.py
python3 -m shedskin -r path_tracing && make
time ./path_tracing
echo CHECK: pt.ppm!

time python3 plcfrs.py
python3 -m shedskin plcfrs && make
time ./plcfrs

python3 -m shedskin -be pygasus && make && python3 -c "import pygasus; assert pygasus.__file__.endswith('.so')"
echo CHECK: pygasus_main!

cd pylot
python3 -m shedskin -be SimpleGeometry && make && python3 -c "import SimpleGeometry; assert SimpleGeometry.__file__.endswith('.so')"
cd ..
echo CHECK: pylot_main!

time python3 pystone.py
python3 -m shedskin pystone && make
time ./pystone

cd quameon
time python3 sto_atom.py
python3 -m shedskin sto_atom && make
time ./sto_atom
cd ..

time python3 richards.py
python3 -m shedskin richards && make
time ./richards

time python3 rdb.py -h
python3 -m shedskin rdb && make
time ./rdb -h

time python3 rsync.py
python3 -m shedskin -Llib rsync && make
time ./rsync

time python3 rubik.py
python3 -m shedskin rubik && make
time ./rubik

time python3 rubik2.py
python3 -m shedskin rubik2 && make
time ./rubik2

time python3 sat.py
python3 -m shedskin sat && make
time ./sat

time python3 score4.py
python3 -m shedskin score4 && make
time ./score4

time python3 sieve.py
python3 -m shedskin sieve && make
time ./sieve

time python3 sha.py hoempadoempa
python3 -m shedskin -Llib -l sha && make
time ./sha hoempadoempa

time python3 sokoban.py
python3 -m shedskin sokoban && make
time ./sokoban

time python3 solitaire.py -test
python3 -m shedskin solitaire && make
time ./solitaire -test

python3 -m shedskin -web stereo && make && python3 -c "import stereo; assert stereo.__file__.endswith('.so')"
echo CHECK: stereo_main!

time python3 sudoku1.py
python3 -m shedskin sudoku1 && make
time ./sudoku1

time python3 sudoku2.py
python3 -m shedskin sudoku2 && make
time ./sudoku2

time python3 sudoku3.py
python3 -m shedskin sudoku3 && make
time ./sudoku3

time python3 sudoku4.py
python3 -m shedskin sudoku4 && make
time ./sudoku4

time python3 sudoku5.py
python3 -m shedskin sudoku5 && make
time ./sudoku5

time python3 sunfish.py
python3 -m shedskin sunfish && make
time ./sunfish

time python3 tictactoe.py
python3 -m shedskin tictactoe && make
time ./tictactoe

time python3 timsort.py
python3 -m shedskin timsort && make
time ./timsort

time python3 TarsaLZP.py
python3 -m shedskin TarsaLZP && make
time ./TarsaLZP

time python3 TonyJpegDecoder.py
python3 -m shedskin TonyJpegDecoder && make
time ./TonyJpegDecoder
echo CHECK: tiger1.bmp!

time python3 voronoi.py
python3 -m shedskin voronoi && make
time ./voronoi

python3 -m shedskin voronoi2 && make

python3 -m shedskin WebServer && make
