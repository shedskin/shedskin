#!/usr/bin/env python
'''
*** SHED SKIN Python-to-C++ Compiler ***
Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)

ss.py: main program file

uses: graph.py (build constraint graph for dataflow analysis)
      infer.py (iterative type analysis over constraint graph)
      cpp.py (generate C++ code)
      shared.py (functions shared by several of these modules)

analysis(): call into above modules to compile a Python program
annotate(): output type-annotated Python files (*.ss.py)
generate_code(): generate Makefile and use cpp.py to output C++ code
main(): parse command-line options, call analysis and annotate

TODO: move generate_code() to cpp.py
      move and revisit confusion misc()
'''
import sys, getopt, os.path
from distutils import sysconfig

import infer, cpp, annotate
from shared import newgx, setgx, getgx


def usage():
    print """Usage: shedskin [OPTION]... FILE

 -a --ann               Output annotated source code (.ss.py)
 -b --nobounds          Disable bounds checking
 -d --dir               Specify alternate directory for output files
 -e --extmod            Generate extension module
 -f --flags             Provide alternate Makefile flags
 -m --makefile          Specify alternate Makefile name
 -r --random            Use fast random number generator
 -w --nowrap            Disable wrap-around checking
"""
    sys.exit(1)

def main():
    setgx(newgx())

    print '*** SHED SKIN Python-to-C++ Compiler 0.3 ***'
    print 'Copyright 2005-2009 Mark Dufour; License GNU GPL version 3 (See LICENSE)'
    print

    # --- some checks
    major, minor = sys.version_info[:2]
    if major != 2 or minor < 4:
        print '*ERROR* Shed Skin is not compatible with this version of Python'
        sys.exit(1)
    if sys.platform == 'win32' and os.path.isdir('c:/mingw'):
        print '*ERROR* please rename or remove c:/mingw, as it conflicts with Shed Skin'
        sys.exit()

    # --- command-line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'bchef:wad:m:r', ['extmod', 'nobounds', 'nowrap', 'flags=', 'dir=', 'makefile=', 'random'])
    except getopt.GetoptError:
        usage()

    for o, a in opts:
        if o in ['-h', '--help']: usage()
        if o in ['-b', '--nobounds']: getgx().bounds_checking = False
        if o in ['-e', '--extmod']: getgx().extension_module = True
        if o in ['-a', '--ann']: getgx().annotation = True
        if o in ['-d', '--dir']: getgx().output_dir = a
        if o in ['-w', '--nowrap']: getgx().wrap_around_check = False
        if o in ['-r', '--random']: getgx().fast_random = True
        if o in ['-m', '--makefile']: getgx().makefile_name = a
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

if __name__ == '__main__':
    main()
