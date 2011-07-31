'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)

'''

import sys, getopt, os.path
from distutils import sysconfig

import infer, cpp, annotate, shared
from shared import newgx, setgx, getgx

def usage():
    print """Usage: shedskin [OPTION]... FILE

 -a --ann               Output annotated source code (.ss.py)
 -b --nobounds          Disable bounds checking
 -e --extmod            Generate extension module
 -f --flags             Provide alternate Makefile flags
 -l --long              Use long long ("64-bit") integers
 -m --makefile          Specify alternate Makefile name
 -o --noassert          Disable assert statements
 -r --random            Use fast random number generator (rand())
 -s --strhash           Use fast string hashing algorithm (murmur)
 -w --nowrap            Disable wrap-around checking
 -x --traceback         Print traceback for uncaught exceptions (slow)
"""
# -p --pypy              Make extension module PyPy-compatible
# -v --msvc              Output MSVC-style Makefile
    sys.exit(1)

def start():
    setgx(newgx())

    print '*** SHED SKIN Python-to-C++ Compiler 0.9 ***'
    print 'Copyright 2005-2011 Mark Dufour; License GNU GPL version 3 (See LICENSE)'
    print

    # --- some checks
    major, minor = sys.version_info[:2]
    if (major, minor) not in [(2, 4), (2, 5), (2, 6), (2, 7)]:
        print '*ERROR* Shed Skin is not compatible with this version of Python'
        sys.exit(1)
    if sys.platform == 'win32' and os.path.isdir('c:/mingw'):
        print '*ERROR* please rename or remove c:/mingw, as it conflicts with Shed Skin'
        sys.exit()

    # --- command-line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vbchef:wad:m:rolspx', ['help', 'extmod', 'nobounds', 'nowrap', 'flags=', 'debug=', 'makefile=', 'random', 'noassert', 'long', 'msvc', 'ann', 'strhash', 'pypy', 'traceback'])
    except getopt.GetoptError:
        usage()

    for o, a in opts:
        if o in ['-h', '--help']: usage()
        if o in ['-b', '--nobounds']: getgx().bounds_checking = False
        if o in ['-e', '--extmod']: getgx().extension_module = True
        if o in ['-a', '--ann']: getgx().annotation = True
        if o in ['-d', '--debug']: getgx().debug_level = a
        if o in ['-l', '--long']: getgx().longlong = True
        if o in ['-w', '--nowrap']: getgx().wrap_around_check = False
        if o in ['-r', '--random']: getgx().fast_random = True
        if o in ['-o', '--noassert']: getgx().assertions = False
        if o in ['-p', '--pypy']: getgx().pypy = True
        if o in ['-m', '--makefile']: getgx().makefile_name = a
        if o in ['-s', '--strhash']: getgx().fast_hash = True
        if o in ['-v', '--msvc']: getgx().msvc = True
        if o in ['-x', '--traceback']: getgx().backtrace = True
        if o in ['-f', '--flags']:
            if not os.path.isfile(a):
                print "*ERROR* no such file: '%s'" % a
                sys.exit(1)
            getgx().flags = a

    # --- argument
    if len(args) != 1:
        usage()
    name = args[0]
    if not name.endswith('.py'):
        name += '.py'
    if not os.path.isfile(name):
        print "*ERROR* no such file: '%s'" % name
        sys.exit(1)
    getgx().main_mod = name[:-3]

    # --- analyze & annotate
    infer.analyze(name)
    annotate.annotate()
    cpp.generate_code()
    shared.print_errors()

def main():
    sys.setrecursionlimit(100000)
    try:
        start()
    except KeyboardInterrupt:
        sys.exit(1)

if __name__ == '__main__':
    main()
