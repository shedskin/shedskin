Introduction
============

PaletteOptimiser is a tool for converting images to the eight colours
supported on the 8-bit Acorn microcomputers: black, white, and the primary and
secondary colours. It then chooses four of these colours per horizontal line
of each eight-colour image, permitting such images to be displayed in
four-colour modes with palette switching on a line-by-line basis.

Usage
=====

optimiser.py <input filename> <output filename> [ <options> ]

Run the program with the --help argument to see a description of the options:

optimiser.py --help

Dependencies
============

Apart from Python, this software requires the following:

Packages                    Release Information
--------                    -------------------

Python Imaging Library      Debian package: python-imaging
(PIL)                       (Tested with 1.1.7-4+deb7u1)
                            Source: http://www.effbot.org/zone/pil-index.htm

exif-py                     Debian package: python-exif
                            (Tested with 1.0.8-3)
                            Source: https://github.com/ianare/exif-py

The following optional dependencies apply for compilation with Shedskin:

Packages                    Release Information
--------                    -------------------

Shedskin                    Debian package: shedskin
                            (Tested with 0.9.2-2)
                            Source: http://code.google.com/p/shedskin/

g++                         Debian package: g++
                            (Tested with 4:4.7.2-1)
                            Source: https://gcc.gnu.org/

make                        Debian package: make
                            (Tested with 3.81-8.2)
                            Source: https://www.gnu.org/software/make/

Compilation with Shedskin
=========================

Suitable versions of the code (see the simpleimage-shedskin branch below) can
be compiled with the Shedskin Python-to-C++ compiler for additional
performance gains. This is done as follows:

shedskin -e optimiserlib.py
make

A file called optimiserlib.so should be produced which should then behave just
like the original Python version, at least when used with the optimiser.py
program.

Repository Branches
===================

The default branch is the original development branch where new techniques
have been introduced.

The simpleimage branch introduces an alternative image class so that the image
processing routines need not be tightly coupled with the Python Imaging
Library abstractions.

The simpleimage-shedskin branch takes advantage of the simpleimage branch to
define a separate module that can be compiled using the Shedskin Python-to-C++
compiler. The resulting compiled module enables an approximate four-fold
increase in speed.

The shedskin branch is an obsolete and not particularly effective attempt to
try and get an earlier version of the tool to compile using Shedskin.

Contact, Copyright and Licence Information
==========================================

See the following Web page for more information about this work:

http://hgweb.boddie.org.uk/PaletteOptimiser

The author can be contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/gpl-3.0.txt for more information.
