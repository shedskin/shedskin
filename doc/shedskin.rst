========
Shedskin
========

---------------------------------------------------
An experimental (restricted) Python-to-C++ Compiler
---------------------------------------------------

:Author: mark.dufour@gmail.com
:Date:   2008-06-01
:Copyright: GPL version 3 or later
:Version: 0.0.28
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

-a, --noann             Don't output annotated source code
-b, --bounds            Enable bounds checking
-d, --dir               Specify alternate directory for output files
-e, --extmod            Generate extension module
-f, --flags             Provide alternate Makefile flags
-i, --infinite          Try to avoid infinite analysis time 
-n, --nowrap            Disable wrap-around checking 

THANKS
======
Google, Bearophile, Brian Blais, Paul Boddie, Djamel Cherif, Mark Dewing, James Coughlan, Luis M. Gonzales, Karel Heyse, Denis de Leeuw Duarte, Michael Elkins, Van Lindberg, David Marek, Jeff Miller, Joaquin Abian Monux, Harri Pasanen, SirNotAppearingInThisManPage, Dave Tweed, Jaroslaw Tworek, Pavel Vinogradov
