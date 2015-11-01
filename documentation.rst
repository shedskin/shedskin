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

Shed Skin translates pure, but implicitly statically typed, Python programs into C++. The static typing restriction means that variables can only ever have a single, static type. So, for example,

::

  a = 1
  a = '1' # bad

is not allowed. However, as in C++, types can be abstract, so that for example,

::

  a = A()
  a = B() # good

where A and B have a common base class, is allowed.

The typing restriction also means that the elements of some collection (list, set, etc.) cannot have different types (because their subtype must also be static). Thus:

::

  a = ['apple', 'b', 'c'] # good
  b = (1, 2, 3) # good
  c = [[10.3, -2.0], [1.5, 2.3], []] # good

is allowed, but

::

  d = [1, 2.5, 'abc'] # bad
  e = [3, [1, 2]] # bad
  f = (0, 'abc', [1, 2, 3]) # bad

is not allowed. Dictionary keys and values may be of different types:

::

  g = {'a': 1, 'b': 2, 'c': 3} # good
  h = {'a': 1, 'b': 'hello', 'c': [1, 2, 3]} # bad

In the current version of Shed Skin, mixed types are also permitted in tuples of length two:

::

  a = (1, [1]) # good

In the future, mixed tuples up to a certain length will probably be allowed.

None may only be mixed with non-scalar types (i.e., not with int, float, bool or complex):

::

  l = [1]
  l = None # good

  m = 1
  m = None # bad

  def fun(x = None): # bad: use a special value for x here, e.g. x = -1
      pass
  fun(1)

Integers and floats can usually be mixed (the integers become floats). Shed Skin should complain in cases where they can't.

Python subset restrictions
--------------------------

Shed Skin will only ever support a subset of all Python features. The following common features are currently not supported:

* :code:`eval`, :code:`getattr`, :code:`hasattr`, :code:`isinstance`, anything really dynamic
* arbitrary-size arithmetic (integers become 32-bit (signed) by default on most architectures, see `Command-line options`_)
* argument (un)packing (:code:`*args` and :code:`**kwargs`)
* multiple inheritance
* nested functions and classes
* unicode
* inheritance from builtins (excluding :code:`Exception` and :code:`object`)
* overloading :code:`__iter__`, :code:`__call__`, :code:`__del__`
* closures

Some other features are currently only partially supported:

* class attributes must always be accessed using a class identifier:

::

  self.class_attr # bad
  SomeClass.class_attr # good
  SomeClass.some_static_method() # good

* function references can be passed around, but not method references or class references, and they cannot be contained:

::

  var = lambda x, y: x+y # good
  var = some_func # good
  var = self.some_method # bad, method reference
  var = SomeClass # bad
  [var] # bad, contained

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

There are two types of downloads available: a self-extracting **Windows** installer and a **UNIX** tarball. But preferrably of course, Shed Skin is installed via your **GNU/Linux** package manager (Shed Skin is available in at least **Debian**, **Ubuntu**, **Fedora** and **Arch**).

Windows
~~~~~~~

To install the **Windows** version, simply download and start it. If you use **ActivePython** or some other non-standard Python distribution, or **MingW**, please deinstall this first. Note also that the 64-bit version of Python seems to be lacking a file, so it's not possible to build extension modules. Please use the 32-bit version instead.

UNIX
~~~~

Using a package manager
```````````````````````

Example command for when using Ubuntu:

::

  sudo apt-get install shedskin

Manual installation
```````````````````

To manually install the UNIX tarball, take the following steps:

* download and unpack tarball
* run:

::

  sudo python setup.py install

Dependencies
............

To compile and run programs produced by shedskin the following libraries are needed:

* g++, the C++ compiler (version 4.2 or higher).
* pcre development files
* Python development files
* Boehm garbage collection

To install these libraries under Ubuntu, type:

::

  sudo apt-get install g++ libpcre++-dev python-all-dev libgc-dev

If the Boehm garbage collector is not available via your package manager, the following is known to work. Download for example version 7.2alpha6 from the `website <http://www.hboehm.info/gc/>`__, unpack it, and install it as follows:

::

  ./configure --prefix=/usr/local --enable-threads=posix --enable-cplusplus --enable-thread-local-alloc --enable-large-config
  make
  make check
  sudo make install

If the PCRE library is not available via your package manager, the following is known to work. Download for example version 8.12 from the `website <http://www.pcre.org/>`__, unpack it, and build as follows:

::

  ./configure --prefix=/usr/local
  make
  sudo make install

OSX
~~~

Manual installation
```````````````````

To install the UNIX tarball on an **OSX** system, take the following steps:

* download and unpack tarball
* run:

::

  sudo python setup.py install

Dependencies
............

To compile and run programs produced by shedskin the following libraries are needed:

* g++, the C++ compiler (version 4.2 or higher; comes with the Apple XCode development environment?)
* pcre development files
* Python development files
* Boehm garbage collection

If the Boehm garbage collector is not available via your package manager, the following is known to work. Download for example version 7.2alpha6 from the `website <http://www.hboehm.info/gc/>`__, unpack it, and install it as follows:

::

  ./configure --prefix=/usr/local --enable-threads=posix --enable-cplusplus --enable-thread-local-alloc --enable-large-config
  make
  make check
  sudo make install

If the PCRE library is not available via your package manager, the following is known to work. Download for example version 8.12 from the `website <http://www.pcre.org/>`__, unpack it, and build as follows:

::

  ./configure --prefix=/usr/local
  make
  sudo make install

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
