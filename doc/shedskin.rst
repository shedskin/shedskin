========
Shedskin
========

---------------------------------------------------
An experimental (restricted) Python-to-C++ Compiler
---------------------------------------------------

:Author: mark.dufour@gmail.com
:Date:   2010-01-08
:Copyright: GPL version 3 or later
:Version: 0.3
:Manual section: 1

SYNOPSIS
========

shedskin [OPTION]... FILE

 -a --ann               Output annotated source code

 -b --nobounds          Disable bounds checking

 -d --dir               Specify alternate directory for output files

 -e --extmod            Generate extension module

 -f --flags             Provide alternate Makefile flags

 -m --makefile          Specify alternate Makefile name

 -r --random            Use fast random number generator

 -w --nowrap            Disable wrap-around checking

DESCRIPTION
===========

Shed Skin is an experimental Python-to-C++ compiler designed to speed up the execution of Python programs. It converts programs written in a static subset of Python to C++. The C++ code can be compiled to executable code, which can be run either as a standalone program or as a module imported and called from CPython.

LIMITATIONS
===========
(See the documentation for a more detailed overview.)

1. Variables must be (implicitly) statically typed. Abstract types (as in C++) are supported.
2. Several Python features cannot be used or only partially. For example, nested functions and variable numbers of arguments are not supported.
3. Programs cannot freely use the standard library, only those available in ``lib/``.

OPTIONS
=======


THANKS
======
Google, Bearophile, Brian Blais, Paul Boddie, Djamel Cherif, Mark Dewing, James Coughlan, Luis M. Gonzales, Karel Heyse, Denis de Leeuw Duarte, Michael Elkins, FFAO, Van Lindberg, David Marek, Douglas McNeil, Jeff Miller, Joaquin Abian Monux, Harri Pasanen, Joris van Rantwijk, Jeremie Roquet, Mike Schrick, SirNotAppearingInThisManPage, Thomas Spura, Dave Tweed, Jaroslaw Tworek, Pavel Vinogradov
