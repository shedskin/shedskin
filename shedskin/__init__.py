'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2022 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)

'''

import argparse
import logging
import os.path
import platform
import struct
import sys
import time
import traceback

if platform.system() == 'Windows':
    import blessed as blessings
else:
    import blessings

from . import graph
from .annotate import annotate
from .config import GlobalInfo
from .cpp import generate_code
from .error import print_errors
from .infer import analyze


class ShedskinFormatter(logging.Formatter):

    def __init__(self, gx, datefmt=None):
        self.gx = gx
        move = gx.terminal.move_x(0)
        self._info_formatter = logging.Formatter(
            move + '%(message)s', datefmt=datefmt)
        self._other_formatter = logging.Formatter(
            move + gx.terminal.bold('*%(levelname)s*') + ' %(message)s',
            datefmt=datefmt)

    def format(self, record):
        if record.levelname == 'INFO':
            return self._info_formatter.format(record)
        return self._other_formatter.format(record)


def parse_command_line_options():
    gx = GlobalInfo()
    gx.terminal = blessings.Terminal()

    # --- command-line options
    parser = argparse.ArgumentParser(
        prog = 'shedskin',
        usage='%(prog)s [options] <name>'
    )

    arg = opt = parser.add_argument

    arg("name", help="Python module to compile")

    opt("-a", "--ann",       help="Output annotated source code (.ss.py)", action="store_true")
    opt("-b", "--nobounds",  help="Disable bounds checking", action="store_true")
    opt("-c", "--nogc",      help="Disable garbage collection", action="store_true")
    opt("-d", "--debug",     help="Set debug level", type=int)
    opt("-e", "--extmod",    help="Generate extension module", action="store_true")
    opt("-f", "--flags",     help="Provide alternate Makefile flags")
    opt("-g", "--nogcwarns", help="Disable runtime GC warnings", action="store_true")
    opt("-l", "--long",      help="Use long long '64-bit' integers", action="store_true")
    opt("-m", "--makefile",  help="Specify alternate Makefile name")
    opt("-n", "--silent",    help="Silent mode, only show warnings", action="store_true")
    opt("-o", "--noassert",  help="Disable assert statements", action="store_true")
    opt("-r", "--random",    help="Use fast random number generator (rand())", action="store_true")
    opt("-w", "--nowrap",    help="Disable wrap-around checking", action="store_true")
    opt("-x", "--traceback", help="Print traceback for uncaught exceptions", action="store_true")
    opt("-L", "--lib",       help="Add a library directory", nargs='*')

    # opt("--pypy",        "-p", help="Make extension module PyPy-compatible")
    # opt("--msvc",        "-v", help="Output MSVC-style Makefile")

    args = parser.parse_args()

    logging_level = logging.INFO
    ifa_logging_level = logging.INFO

    if args.nobounds:
        gx.bounds_checking = False

    if args.extmod:
        gx.extension_module = True

    if args.ann:
        gx.annotation = True

    if args.debug:
        logging_level = logging.DEBUG
        if args.debug == 3:
            ifa_logging_level = logging.DEBUG

    if args.long:
        gx.longlong = True

    if args.nogc:
        gx.nogc = True

    if args.nogcwarns:
        gx.gcwarns = False

    if args.nowrap:
        gx.wrap_around_check = False

    if args.random:
        gx.fast_random = True

    if args.noassert:
        gx.assertions = False

    # if args.pypy:
    #     gx.pypy = True

    if args.makefile:
        gx.makefile_name = args.makefile

    if args.silent:
        logging_level = logging.WARNING

    # if args.msvc:
    #     gx.msvc = True

    if args.traceback:
        gx.traceback = True

    if args.lib:
        gx.libdirs = args.lib + gx.libdirs

    if args.flags:
        if not os.path.isfile(args.flags):
            logging.error("no such file: '%s'", args.flags)
            sys.exit(1)
        gx.flags = args.flags

    # silent -> WARNING only, debug -> DEBUG, default -> INFO
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(ShedskinFormatter(gx))
    root = logging.getLogger('')
    root.addHandler(console)
    root.setLevel(logging_level)
    # debug=3 -> IFA (iterative flow analysis) logging enabled.
    logging.getLogger('infer.ifa').setLevel(ifa_logging_level)

    logging.info('*** SHED SKIN Python-to-C++ Compiler 0.9.5 *** - ')
    logging.info('Copyright 2005-2022 Mark Dufour and contributors; License GNU GPL version 3 (See LICENSE)')
    logging.info('')

    # --- some checks
    major, minor = sys.version_info[:2]
    if (major, minor) not in [(2, 7), (3, 8), (3, 9), (3, 10), (3, 11)]:
        logging.error('Shed Skin is not compatible with this version of Python')
        sys.exit(1)
    if sys.platform == 'win32' and os.path.isdir('c:/mingw'):
        logging.error('please rename or remove c:/mingw, as it conflicts with Shed Skin')
        sys.exit()
    if sys.platform == 'win32' and struct.calcsize('P') == 8 and gx.extension_module:
        logging.warning('64-bit python may not come with necessary file to build extension module')

    # --- argument
    name = args.name[:]
    if not name.endswith('.py'):
        name += '.py'
    if not os.path.isfile(name):
        logging.error("no such file: '%s'", name)
        sys.exit(1)
    main_module_name = os.path.splitext(name)[0]

    return gx, main_module_name


def start(gx, main_module_name):
    # --- analyze & annotate
    t0 = time.time()
    analyze(gx, main_module_name)
    annotate(gx)
    generate_code(gx)
    print_errors()
    logging.info('[elapsed time: %.2f seconds]', (time.time() - t0))


def main():
    sys.setrecursionlimit(100000)
    gx, main_module_name = parse_command_line_options()
    try:
        start(gx, main_module_name)
    except KeyboardInterrupt as e:
        logging.debug('KeyboardInterrupt', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
