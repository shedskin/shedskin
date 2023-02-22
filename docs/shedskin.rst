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

    % shedskin --help
    usage: shedskin [-h] {analyze,translate,build,test,run} ...

    Python-to-C++ Compiler

    options:
      -h, --help            show this help message and exit

    subcommands:
        analyze             analyze and validate python module
        translate           translate python module to cpp
        build               build translated module
        run                 run built and translated module
        test                run tests
