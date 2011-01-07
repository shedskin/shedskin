import os
import sys

def do_cmd(cmd):
    print '\n\n', cmd, '\n'
    assert os.system(cmd) == 0

files = ['minilight.py', 'c64.py', 'SimpleGeometry.py', 'rsync.py', 'path_tracing.py', 'neural1.py', 'mandelbrot.py', 'sudoku3.py', 'pystone.py', 'nbody.py', 'genetic.py', 'richards.py', 'voronoi.py', 'oliva2.py', 'sieve.py', 'linalg.py', 'brainfuck.py', 'pisang.py', 'sudoku2.py', 'life.py', 'sudoku1.py', 'othello.py', 'chess.py', 'pygmy.py', 'tictactoe.py', 'yopyra.py', 'dijkstra.py', 'dijkstra2.py', 'amaze.py', 'neural2.py', 'mastermind.py', 'rdb.py', 'TonyJpegDecoder.py', 'mao.py', 'sudo.py', 'mastermind2.py', 'circle.py', 'voronoi2.py', 'ant.py', 'LZ2.py', 'ac_encode.py', 'block.py', 'go.py', 'mwmatching.py', 'bh.py', 'kanoodle.py', 'fysphun.py', 'pylife.py', 'astar.py', 'genetic2.py', 'adatron.py', 'chaos.py']

if sys.platform != 'win32':
    files.extend(['msp_ss.py'])

print 'examples: %d' % len(set(files))

# cmd-line options

print '*** cmd-line options:'

do_cmd('shedskin -b othello')
do_cmd('make')
do_cmd('shedskin -w othello')
do_cmd('make')

# ss-progs

print '*** examples:'
os.system('cp lib/* ../shedskin/lib')

for (i, file) in enumerate(files):
    print '*** test: %s %d' % (file, i)
    if file == 'c64.py':
        os.chdir('c64')
    if file == 'SimpleGeometry.py':
        os.chdir('pylot')
    do_cmd('shedskin %s' % file)
    do_cmd('make')
    do_cmd('shedskin -lars %s' % file)
    do_cmd('make')
    do_cmd('shedskin -e %s' % file)
    do_cmd('make')
    if file in ('c64.py', 'SimpleGeometry.py'):
        os.chdir('..')
