import os

def do_cmd(cmd):
    print '\n\n', cmd, '\n'
    assert os.system(cmd) == 0

files = ['neural1.py', 'mask_alg.py', 'mandelbrot.py', 'sudoku3.py', 'pystone.py', 'nbody.py', 'genetic.py', 'richards.py', 'voronoi.py', 'oliva2.py', 'sieve.py', 'linalg.py', 'brainfuck.py', 'pisang.py', 'sudoku2.py', 'life.py', 'sudoku1.py', 'othello.py', 'chess.py', 'msp_ss.py', 'pygmy.py', 'tictactoe.py', 'yopyra.py', 'dijkstra.py', 'amaze.py', 'neural2.py'] # XXX fysphun.py

print 'examples: %d' % len(set(files))

# cmd-line options

print '*** cmd-line options:'

do_cmd('shedskin -b othello && make run')
do_cmd('shedskin -w othello && make run')

# ss-progs

print '*** examples:'

os.system('cp lib/* ../lib')

for (i, file) in enumerate(files):
    print '*** test: %s %d' % (file, i)

    options = ''
    if file == 'yopyra.py':
        options += ' -i'

    do_cmd('shedskin %s %s && make run' % (options.strip(), file)) 
    do_cmd('shedskin -e %s %s && make' % (options.strip(), file))


