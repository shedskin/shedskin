========
Shedskin
========

---------------------------------------------------
An experimental (restricted) Python-to-C++ Compiler
---------------------------------------------------

:Date:   2022-11-03
:Version: 0.9.6
:Manual section: 1

SYNOPSIS
========

shedskin [OPTION]... FILE

DESCRIPTION
===========

Shed Skin is an experimental compiler, that can translate pure, but implicitly statically typed Python (3.8+) programs into optimized C++. It can generate stand-alone programs or extension modules that can be imported and used in larger Python programs.

Besides the typing restriction, programs cannot freely use the Python standard library (although about 25 common modules, such as random and re, are currently supported). Also, not all Python features, such as nested functions and variable numbers of arguments, are supported.

OPTIONS
=======

::

    usage: shedskin [options] <name>

    Python-to-C++ Compiler

    positional arguments:
      name                  Python file or module to compile

    options:
      -h, --help            show this help message and exit
      -a, --ann             Output annotated source code (.ss.py)
      -b, --nobounds        Disable bounds checking
      -c, --nogc            Disable garbage collection
      -d DEBUG, --debug DEBUG
                            Set debug level
      -e, --extmod          Generate extension module
      -f FLAGS, --flags FLAGS
                            Provide alternate Makefile flags
      -g, --nogcwarns       Disable runtime GC warnings
      -l, --long            Use long long '64-bit' integers
      -m MAKEFILE, --makefile MAKEFILE
                            Specify alternate Makefile name
      -n, --noassert        Disable assert statements
      -o OUTPUTDIR, --outputdir OUTPUTDIR
                            Specify output directory for generated files
      -r, --random          Use fast random number generator (rand())
      -s, --silent          Silent mode, only show warnings
      -w, --nowrap          Disable wrap-around checking
      -x, --traceback       Print traceback for uncaught exceptions
      -N, --nomakefile      Disable makefile generation
      -L [LIB ...], --lib [LIB ...]
                            Add a library directory
