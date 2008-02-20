========
Shedskin
========

--------------------------------------
An experimental Python-to-C++ Compiler
--------------------------------------

:Author: mark.dufour@gmail.com
:Date:   2008-01-05
:Copyright: GPL version 3 or later
:Version: 0.0.26
:Manual section: 1

SYNOPSIS
========

  shedskin [OPTION]... FILE

DESCRIPTION
===========

Shed Skin is an experimental Python-to-C++ compiler designed to speed up the execution of Python programs. It converts programs written in a static subset of Python to C++. The C++ code can be compiled to executable code, which can be run either as a standalone program or as a module imported and called from CPython. 

LIMITATIONS
===========
(See the documentation for a more detailed overview.)

1. Variables must be (implicitly) statically typed. Abstract and generic types (as in C++) are supported.
2. Several Python features cannot be used or only partially. For example, nested functions and variable numbers of arguments are not supported.
3. Programs cannot freely use the standard library, only those available in ``lib/*.py``.

OPTIONS
=======

-b, --bounds            Enable bounds checking
-e, --extmod            Generate extension module
-f, --flags             Provide alternative Makefile flags 
-n, --nowrap            Disable wrap-around checking
-i, --infinite          Try to avoid infinite analysis time

THANKS
======
Google, Bearophile, Brian Blais, Paul Boddie, Mark Dewing, James Coughlan, Luis M. Gonzales, Denis de Leeuw Duarte, Van Lindberg, David Marek, Jeff Miller, Joaquin Abian Monux, Harri Pasanen, SirNotAppearingInThisManPage, Jaroslaw Tworek, Pavel Vinogradov
