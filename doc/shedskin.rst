========
Shedskin
========

---------------------------------------------------
An experimental (restricted) Python-to-C++ Compiler
---------------------------------------------------

:Author: mark.dufour@gmail.com
:Date:   2011-09-01
:Copyright: GPL version 3
:Version: 0.9
:Manual section: 1

SYNOPSIS
========

shedskin [OPTION]... FILE

DESCRIPTION
===========

Shed Skin is an experimental Python-to-C++ compiler designed to speed up the execution of Python programs. It converts programs written in a static subset of Python to C++. The C++ code can be compiled to executable code, which can be run either as a standalone program or as a module imported and called from CPython.

LIMITATIONS
===========
(See the online documentation for a more detailed overview.)

1. Variables must be (implicitly) statically typed.
2. Several Python features cannot be used or only partially. For example, nested functions and variable numbers of arguments are not supported.
3. Programs cannot freely use the standard library, only about 25 common ones (such as random and re).

OPTIONS
=======

 -a --ann               Output annotated source code (.ss.py)

 -b --nobounds          Disable bounds checking

 -e --extmod            Generate extension module

 -f --flags             Provide alternate Makefile flags

 -l --long              Use long long integers

 -m --makefile          Specify alternate Makefile name

 -n --silent            Silent mode, only show warnings

 -o --noassert          Disable assert statements

 -r --random            Use fast random number generator (rand())

 -s --strhash           Use fast string hashing algorithm (murmur)

 -w --nowrap            Disable wrap-around checking

 -x --traceback         Print traceback for uncaught exceptions

THANKS
======
Hakan Ardo, Brian Blais, Paul Boddie, François Boutines, Djamel Cherif, James Coughlan, Mark Dewing, Mark Dufour, Artem Egorkine, Michael Elkins, Enzo Erbano, FFAO, Victor Garcia, Luis M. Gonzales, Fahrzin Hemmati, Karel Heyse, Denis de Leeuw Duarte, Van Lindberg, David Marek, Douglas McNeil, Andy Miller, Jeff Miller, Danny Milosavljevic, Joaquin Abian Monux, John Nagle, Harri Pasanen, Brent Pedersen, Joris van Rantwijk, Jeremie Roquet, Mike Schrick, SirNotAppearingInThisTutorial, Thomas Spura, Dave Tweed, Jaroslaw Tworek, Tony Veijalainen, Pavel Vinogradov, Jason Ye, Joris van Zwieten
