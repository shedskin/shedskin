.. image:: https://img.shields.io/travis/shedskin/shedskin.svg
    :target: https://travis-ci.org/shedskin/shedskin
.. image:: http://img.shields.io/badge/benchmarked%20by-asv-green.svg?style=flat
    :target: http://shedskin.github.io/benchmarks

Shed Skin
=========

Shed Skin is an experimental compiler, that can translate pure, but implicitly statically typed Python (2.4-2.6) programs into optimized C++. It can generate stand-alone programs or extension modules that can be imported and used in larger Python programs.

Besides the typing restriction, programs cannot freely use the Python standard library (although about 25 common modules, such as random and re, are currently supported). Also, not all Python features, such as nested functions and variable numbers of arguments, are supported (see the `documentation <https://shedskin.github.io/docs/>`_ for details).

For a set of `75 non-trivial programs <https://github.com/shedskin/shedskin/releases/download/v0.9.4/shedskin-examples-0.9.4.tgz>`_ (at over 25,000 lines in total (sloccount)), measurements show a typical speedup of 2-200 times over CPython.

The following people have contributed to Shed Skin development so far:

  Hakan Ardo, Brian Blais, Paul Boddie, François Boutines, Djamel Cherif, James Coughlan, Mark Dewing, Mark Dufour, Artem Egorkine, Michael Elkins, Moataz Elmasry, Enzo Erbano, Ernesto Ferro, Salvatore Ferro, FFAO, Victor Garcia, Luis M. Gonzales, Fahrzin Hemmati, Karel Heyse, Kousuke, Denis de Leeuw Duarte, Van Lindberg, David Marek, Douglas McNeil, Andy Miller, Jeff Miller, Danny Milosavljevic, Joaquin Abian Monux, John Nagle, Harri Pasanen, Brent Pedersen, Joris van Rantwijk, Pierre-Marie de Rodat, Jérémie Roquet, Mike Schrick, SirNotAppearingInThisTutorial, Thomas Spura, Joerg Stippa, Dave Tweed, Jaroslaw Tworek, Tony Veijalainen, Pavel Vinogradov, Jason Ye, Liu Zhenhai, Joris van Zwieten

Installation
------------

::

  sudo python setup.py install
  shedskin test.py
  make
  ./test

Documentation
-------------

See: https://shedskin.github.io/docs/
