Shed Skin documentation
=======================

Introduction
------------

Shed Skin is an experimental Python-to-C++ compiler designed to speed up the execution of computation-intensive Python programs. It converts programs written in a restricted subset of Python to C++. The C++ code can be compiled to executable code, which can be run either as a standalone program or as an extension module easily imported and used in a regular Python program.

Shed Skin uses type inference techniques to determine the implicit types used in a Python program, in order to generate the explicit type declarations needed in a C++ version. Because C++ is statically typed, Shed Skin requires Python code to be written such that all variables are (implicitly!) statically typed.

Besides the typing and subset restrictions, supported programs cannot freely use the Python standard library, although about 25 common modules are supported, such as :code:`random` and :code:`re` (see `Library limitations`_).

Additionally, the type inference techniques employed by Shed Skin currently do not scale very well beyond several thousand lines of code (the largest compiled program is about 6,000 lines (sloccount)). In all, this means that Shed Skin is currently mostly useful to compile smallish programs and extension modules, that do not make extensive use of dynamic Python features or the standard or external libraries. See here for a collection of 75 non-trivial example programs.

Because Shed Skin is still in an early stage of development, it can also improve a lot. At the moment, you will probably run into some bugs when using it. Please report these, so they can be fixed!

At the moment, Shed Skin is compatible with Python versions 2.4 to 2.7, behaves like 2.6, and should work on Windows and most UNIX platforms, such as GNU/Linux and OSX.

Typing restrictions
-------------------

.. TODO

Python subset restrictions
--------------------------

.. TODO

Library limitations
-------------------

At the moment, the following 25 modules are largely supported. Several of these, such as :code:`os.path`, were compiled to C++ using Shed Skin.

* :code:`array`
* :code:`binascii`
* :code:`bisect`
* :code:`collections` (defaultdict, deque)
* :code:`colorsys`
* :code:`ConfigParser` (no SafeConfigParser)
* :code:`copy`
* :code:`csv` (no Dialect, Sniffer)
* :code:`datetime`
* :code:`fnmatch`
* :code:`getopt`
* :code:`glob`
* :code:`heapq`
* :code:`itertools` (no starmap)
* :code:`math`
* :code:`mmap`
* :code:`os` (some functionality missing on Windows)
* :code:`os.path`
* :code:`random`
* :code:`re`
* :code:`select` (only select function, on UNIX)
* :code:`socket`
* :code:`string`
* :code:`struct` (no Struct, pack_into, unpack_from)
* :code:`sys`
* :code:`time`

Note that any other module, such as :code:`pygame`, :code:`pyqt` or :code:`pickle`, may be used in combination with a Shed Skin generated extension module. For examples of this, see the `Shed Skin examples <https://github.com/shedskin/shedskin/releases/download/v0.9.4/shedskin-examples-0.9.4.tgz>`_.

See `How to help out in development`_ on how to help improve or add to the set of supported modules.

Installation
------------

.. TODO

Windows
~~~~~~~

.. TODO

UNIX
~~~~

Using a package manager
```````````````````````

.. TODO

Manual installation
```````````````````

.. TODO

Dependencies
............

.. TODO

OSX
~~~

Manual installation
```````````````````

.. TODO

Dependencies
............

.. TODO

Compiling a standalone program
------------------------------

.. TODO

Generating an extension module
------------------------------

.. TODO

Limitations
~~~~~~~~~~~

.. TODO

Numpy integration
~~~~~~~~~~~~~~~~~

.. TODO

Distributing binaries
---------------------

Windows
~~~~~~~

.. TODO

UNIX
~~~~

.. TODO

Multiprocessing
---------------

.. TODO

Calling C/C++ code
------------------

.. TODO

Standard library
~~~~~~~~~~~~~~~~

.. TODO

Shed Skin types
~~~~~~~~~~~~~~~

.. TODO

Command-line options
--------------------

.. TODO

Performance tips and tricks
---------------------------

Performance tips
~~~~~~~~~~~~~~~~

.. TODO

Tricks
~~~~~~

.. TODO

How to help out in development
------------------------------

Open source projects thrive on feedback. Please send in bug reports, patches or other code, or suggestions about this document; or join the mailing list and start or participate in discussions. There is also `a page with suggestions <https://github.com/shedskin/shedskin/labels/easytask>`_ for possible tasks to start out with.

If you are a student, you might want to consider applying for the yearly Google Summer of Code or GHOP projects. Shed Skin has so far successfully participated in one Summer of Code and one GHOP.
