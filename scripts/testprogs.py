import commands
import os
import sys
from multiprocessing import Pool
from multiprocessing.pool import IMapIterator


#Fix for multiprocessing. Without this, Ctrl+C will not kill the process immediately
set_timeout_decorator = lambda func: lambda self: func(self, timeout=1e100)
IMapIterator.next = set_timeout_decorator(IMapIterator.next)

SS = '../shedskin/__init__.py'


def do_cmd(cmd):
    status, output = commands.getstatusoutput(cmd)
    return status, '\n\n%s\n%s' % (cmd, output)


def test_prog(file):
    prefix = ''
    if file == 'c64.py':
        os.chdir('c64')
        prefix = '../'
    elif file == 'SimpleGeometry.py':
        os.chdir('pylot')
        prefix = '../'
    elif file == 'sto_atom.py':
        os.chdir('quameon')
        prefix = '../'

    outputs = ['*** test: %s' % file]
    try:
        commands = [
            'python %s -m Makefile.%s %s' % (prefix + SS, file, file),
            'make clean -f Makefile.%s' % file,
            'make -f Makefile.%s' % file,
            'python %s -m Makefile.%s -wboxlars %s' % (prefix + SS, file, file),
            'make clean -f Makefile.%s' % file,
            'make -f Makefile.%s' % file,
            'python %s -m Makefile.%s -e %s' % (prefix + SS, file, file),
            'make clean -f Makefile.%s' % file,
            'make -f Makefile.%s' % file]

        for command in commands:
            status, output = do_cmd(command)
            outputs.append(output)
            assert status == 0

        return True, file, ''.join(outputs)
    except AssertionError:
        return False, file, ''.join(outputs)
    finally:
        if file in ('c64.py', 'SimpleGeometry.py', 'sto_atom.py'):
            os.chdir('..')


if __name__ == '__main__':
    files = ['timsort.py', 'pygasus.py', 'sat.py', 'minpng.py', 'TarsaLZP.py', 'rubik2.py', 'rubik.py', 'stereo.py', 'hq2x.py', 'minilight_main.py', 'sudoku5.py', 'kmeanspp.py', 'mandelbrot2.py', 'sokoban.py', 'score4.py', 'plcfrs.py', 'sha.py', 'loop.py', 'solitaire.py', 'sto_atom.py', 'c64.py', 'SimpleGeometry.py', 'path_tracing.py', 'neural1.py', 'mandelbrot.py', 'sudoku3.py', 'pystone.py', 'nbody.py', 'genetic.py', 'richards.py', 'voronoi.py', 'oliva2.py', 'sieve.py', 'linalg.py', 'brainfuck.py', 'pisang.py', 'sudoku2.py', 'life.py', 'sudoku1.py', 'othello.py', 'chess.py', 'pygmy.py', 'tictactoe.py', 'yopyra.py', 'dijkstra.py', 'dijkstra2.py', 'amaze.py', 'neural2.py', 'mastermind_main.py', 'rdb.py', 'TonyJpegDecoder.py', 'mao.py', 'sudoku4.py', 'mastermind2.py', 'circle.py', 'voronoi2.py', 'ant.py', 'LZ2.py', 'ac_encode.py', 'block.py', 'go.py', 'mwmatching.py', 'bh.py', 'kanoodle.py', 'fysphun.py', 'pylife.py', 'astar.py', 'genetic2.py', 'adatron.py', 'chaos.py']

    if sys.platform != 'win32':
        files.extend(['msp_ss.py', 'rsync.py'])

    print 'examples: %d' % len(set(files))

    # cmd-line options

    print '*** cmd-line options:'

    print do_cmd('python %s -b othello' % SS)[1]
    print do_cmd('make')[1]
    print do_cmd('python %s -w othello' % SS)[1]
    print do_cmd('make')[1]

    # ss-progs

    print '*** examples:'
    os.system('cp lib/* ../shedskin/lib')
    pool = Pool()

    for success, file, output in pool.imap(test_prog, files):
        print output
        if not success:
            print file, 'failed!'
            break
