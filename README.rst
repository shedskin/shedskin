.. image:: https://img.shields.io/travis/shedskin/shedskin.svg
    :target: https://travis-ci.org/shedskin/shedskin
.. image:: http://img.shields.io/badge/benchmarked%20by-asv-green.svg?style=flat
    :target: http://shedskin.github.io/benchmarks

Shed Skin
=========

Shed Skin is an experimental compiler, that can translate pure, but implicitly statically typed Python (2.4-2.7) programs into optimized C++. It can generate stand-alone programs or extension modules that can be imported and used in larger Python programs.

Besides the typing restriction, programs cannot freely use the Python standard library (although about 25 common modules, such as random and re, are currently supported). Also, not all Python features, such as nested functions and variable numbers of arguments, are supported (see the `documentation <https://shedskin.readthedocs.io/>`_ for details).

For a set of `75 non-trivial programs <https://github.com/shedskin/shedskin/tree/master/examples>`_ (at over 25,000 lines in total (sloccount)), measurements show a typical speedup of 2-200 times over CPython.

Usage
-----

::

  shedskin test.py
  make
  ./test

Restrictions
------------

Shed Skin only supports a restricted subset of Python, so one should not expect a given program to compile without any changes, if possible at all. See the `documentation <https://shedskin.readthedocs.io/>`_ for an overview of the limitations.

Installation
------------

Shed Skin depends on some others projects, such as the `Boehm garbage collector <https://www.hboehm.info/gc/>`_. Please see the `documentation <https://shedskin.readthedocs.io/en/latest/documentation.html#installation>`_ on how to install these.

Contributors
------------

The following people have contributed to Shed Skin development so far:

::

  Hakan Ardo
  Brian Blais
  Paul Boddie
  François Boutines
  Djamel Cherif
  James Coughlan
  Mark Dewing
  Mark Dufour
  Artem Egorkine
  Michael Elkins
  Moataz Elmasry
  Enzo Erbano
  Ernesto Ferro
  Salvatore Ferro
  FFAO
  Victor Garcia
  Luis M. Gonzales
  Fahrzin Hemmati
  Folkert van Heusden
  Karel Heyse
  Johan Kristensen
  Kousuke
  Denis de Leeuw Duarte
  Van Lindberg
  David Marek
  Douglas McNeil
  Andy Miller
  Jeff Miller
  Danny Milosavljevic
  Joaquin Abian Monux
  John Nagle
  Harri Pasanen
  Brent Pedersen
  Joris van Rantwijk
  Retsyo
  Pierre-Marie de Rodat
  Jérémie Roquet
  Mike Schrick
  SirNotAppearingInThisTutorial
  Paul Sokolevsky
  Thomas Spura
  Joerg Stippa
  Dan Stromberg
  Dave Tweed
  Jaroslaw Tworek
  Tony Veijalainen
  Pavel Vinogradov
  Jason Ye
  Liu Zhenhai
  Joris van Zwieten
