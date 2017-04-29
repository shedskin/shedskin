'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2013 Mark Dufour; License GNU GPL version 3 (See LICENSE)

'''
import getopt
import logging
import os.path
import struct
import sys
import time
import traceback

import blessings

from shedskin import graph
from shedskin.annotate import annotate
from shedskin.cpp import generate_code
from shedskin.error import print_errors
from shedskin.infer import analyze

class GlobalInfo:  # XXX add comments, split up
    def __init__(self):
        self.constraints = set()
        self.allvars = set()
        self.allfuncs = set()
        self.allclasses = set()
        self.cnode = {}
        self.types = {}
        self.templates = 0
        self.modules = {}
        self.inheritance_relations = {}
        self.inheritance_temp_vars = {}
        self.parent_nodes = {}
        self.inherited = set()
        self.nrcltypes = 8
        self.empty_constructors = set()
        self.sig_nr = {}
        self.nameclasses = {}
        self.module = None
        self.builtins = ['none', 'str_', 'float_', 'int_', 'class_', 'list',
                         'tuple', 'tuple2', 'dict', 'set', 'frozenset', 'bool_']
        # instance node for instance Variable assignment
        self.assign_target = {}
        # allocation site type information across iterations
        self.alloc_info = {}
        self.iterations = 0
        self.total_iterations = 0
        self.lambdawrapper = {}
        self.init_directories()
        illegal_file = open(os.path.join(self.sysdir, 'illegal'))
        self.cpp_keywords = set(line.strip() for line in illegal_file)
        self.ss_prefix = '__ss_'
        self.list_types = {}
        self.loopstack = []  # track nested loops
        self.filterstack = []  # track 'if isinstance(..)'
        self.filters = {}  # syntax node filter determined using filterstack
        self.comments = {}
        self.import_order = 0  # module import order
        self.from_module = {}
        self.class_def_order = 0
        # command-line options
        self.wrap_around_check = True
        self.bounds_checking = True
        self.fast_random = False
        self.assertions = True
        self.extension_module = False
        self.longlong = False
        self.flags = None
        self.annotation = False
        self.msvc = False
        self.gcwarns = True
        self.pypy = False
        self.backtrace = False
        self.makefile_name = 'Makefile'
        self.fast_hash = False
        self.debug_level = 0

        # Others
        self.item_rvalue = {}
        self.genexp_to_lc = {}
        self.bool_test_only = set()
        self.tempcount = {}
        self.struct_unpack = {}
        self.maxhits = 0  # XXX amaze.py termination
        self.gc_cleanup = False
        self.terminal = None
        self.progressbar = None

    def init_directories(self):
        shedskin_directory = os.sep.join(__file__.split(os.sep)[:-1])
        for dirname in sys.path:
               if os.path.exists(os.path.join(dirname, shedskin_directory)):
                   shedskin_directory = os.path.join(dirname, shedskin_directory)
                   break
        shedskin_libdir = os.path.join(shedskin_directory, 'lib')
        system_libdir = '/usr/share/shedskin/lib'

        self.sysdir = shedskin_directory
        if os.path.isdir(shedskin_libdir):
            self.libdirs = [shedskin_libdir]
        elif os.path.isdir(system_libdir):
            self.libdirs = [system_libdir]
        else:
            print('*ERROR* Could not find lib directory in %s or %s.\n'%(shedskin_libdir, system_libdir))
            sys.exit(1)


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


def usage():
    print("""Usage: shedskin [OPTION]... FILE

 -a --ann               Output annotated source code (.ss.py)
 -b --nobounds          Disable bounds checking
 -e --extmod            Generate extension module
 -f --flags             Provide alternate Makefile flags
 -g --nogcwarns         Disable runtime GC warnings
 -l --long              Use long long ("64-bit") integers
 -m --makefile          Specify alternate Makefile name
 -n --silent            Silent mode, only show warnings
 -o --noassert          Disable assert statements
 -r --random            Use fast random number generator (rand())
 -s --strhash           Use fast string hashing algorithm (murmur)
 -w --nowrap            Disable wrap-around checking
 -x --traceback         Print traceback for uncaught exceptions
 -L --lib               Add a library directory
""")
# -p --pypy              Make extension module PyPy-compatible
# -v --msvc              Output MSVC-style Makefile
    sys.exit(1)


def parse_command_line_options():
    gx = GlobalInfo()
    gx.terminal = blessings.Terminal()

    # --- command-line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vbchef:wad:m:rolspxngL:', ['help', 'extmod', 'nobounds', 'nowrap', 'flags=', 'debug=', 'makefile=', 'random', 'noassert', 'long', 'msvc', 'ann', 'strhash', 'pypy', 'traceback', 'silent', 'nogcwarns', 'lib'])
    except getopt.GetoptError:
        usage()

    logging_level = logging.INFO
    ifa_logging_level = logging.INFO

    for opt, value in opts:
        if opt in ['-h', '--help']:
            usage()
        if opt in ['-b', '--nobounds']:
            gx.bounds_checking = False
        if opt in ['-e', '--extmod']:
            gx.extension_module = True
        if opt in ['-a', '--ann']:
            gx.annotation = True
        if opt in ['-d', '--debug']:
            logging_level = logging.DEBUG
            if int(value) == 3:
                ifa_logging_level = logging.DEBUG
        if opt in ['-l', '--long']:
            gx.longlong = True
        if opt in ['-g', '--nogcwarns']:
            gx.gcwarns = False
        if opt in ['-w', '--nowrap']:
            gx.wrap_around_check = False
        if opt in ['-r', '--random']:
            gx.fast_random = True
        if opt in ['-o', '--noassert']:
            gx.assertions = False
        if opt in ['-p', '--pypy']:
            gx.pypy = True
        if opt in ['-m', '--makefile']:
            gx.makefile_name = value
        if opt in ['-n', '--silent']:
            logging_level = logging.WARNING
        if opt in ['-s', '--strhash']:
            gx.fast_hash = True
        if opt in ['-v', '--msvc']:
            gx.msvc = True
        if opt in ['-x', '--traceback']:
            gx.backtrace = True
        if opt in ['-L', '--lib']:
            gx.libdirs = [value] + gx.libdirs
        if opt in ['-f', '--flags']:
            if not os.path.isfile(value):
                logging.error("no such file: '%s'", value)
                sys.exit(1)
            gx.flags = value

    # silent -> WARNING only, debug -> DEBUG, default -> INFO
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(ShedskinFormatter(gx))
    root = logging.getLogger('')
    root.addHandler(console)
    root.setLevel(logging_level)
    # debug=3 -> IFA (iterative flow analysis) logging enabled.
    logging.getLogger('infer.ifa').setLevel(ifa_logging_level)

    logging.info('*** SHED SKIN Python-to-C++ Compiler 0.9.4 *** - ')
    logging.info('Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)')
    logging.info('')

    # --- some checks that are required to run shedskin
    if sys.platform == 'win32' and os.path.isdir('c:/mingw'):
        logging.error('please rename or remove c:/mingw, as it conflicts with Shed Skin')
        sys.exit()
    if sys.platform == 'win32' and struct.calcsize('P') == 8 and gx.extension_module:
        logging.warning('64-bit python may not come with necessary file to build extension module')

    # --- argument
    if len(args) != 1:
        usage()
    name = args[0]
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
