Shed Skin Tutorial
==================

:Version: 0.3
:Date: Jan 8 2010
:Authors: Mark Dufour and James Coughlan

.. _Parallel Python: http://www.parallelpython.com/
.. _Googlecode Site: http://shedskin.googlecode.com/
.. _pprocess: http://www.boddie.org.uk/python/pprocess.html
.. _numpy: http://numpy.scipy.org/
.. _quameon: http://quameon.sourceforge.net/
.. _Summer of code: http://code.google.com/soc/
.. _GHOP: http://code.google.com/opensource/ghop/
.. _Boehm: http://www.hpl.hp.com/personal/Hans_Boehm/gc/
.. _PCRE: http://www.pcre.org/
.. _Gprof2Dot: http://code.google.com/p/jrfonseca/wiki/Gprof2Dot

.. contents::

.. _Introduction:

Introduction
------------

**Shed Skin** is an *experimental* **Python-to-C++ compiler** designed to speed up the execution of computation-intensive Python programs. It converts programs written in a *static subset* of Python to C++. The C++ code can be compiled to executable code, which can be run either as a standalone program or as an extension module easily imported and used in a regular Python program.

**Shed Skin** uses type inference techniques to determine the *implicit* types used in a Python program, in order to generate the *explicit* type declarations needed in a C++ version. Because C++ is *statically typed*, **Shed Skin** requires Python code to be written such that all variables are (implicitly) statically typed.

Besides the *typing* and *subset* restrictions, supported programs cannot freely use the Python standard library, although about 20 common modules are supported, such as ``random`` and ``re`` (see `Library Limitations`_).

Additionally, the type inference techniques employed by **Shed Skin** currently do not scale very well beyond several hundred lines of code (the largest compiled program is about 1,200 lines (sloccount)). In all, this means that **Shed Skin** is currently mostly useful to compile *smallish* programs and extension modules, that do not make extensive use of dynamic Python features or the standard library.

Because **Shed Skin** is still in an early stage of development, it can also improve a lot. At the moment, you will probably run into some bugs when using it. Please report these, so they can be fixed! 

At the moment, **Shed Skin** is compatible with Python versions 2.4 to 2.7, behaves like 2.6, and should work on GNU/Linux platforms, FreeBSD, OpenSolaris, OSX and Windows XP.

.. _Typing Restrictions:

Typing Restrictions
-------------------

**Shed Skin** translates pure, but *implicitly statically typed*, Python programs into C++. The static typing restriction means that variables can only ever have a *single, static type*. So, for example, ::

    a = 1
    a = ’1’ # bad

is not allowed. However, as in C++, types can be *abstract*, so that, for example, ::

    a = A()
    a = B() # good

where **A** and **B** have a common base class, is allowed. 

The typing restriction also means that the elements of some collection (``list``, ``set``, etc.) cannot have different types (because their *subtype* must also be static). Thus: ::

    a = [’apple’, ’b’, ’c’] # good
    b = (1, 2, 3) # good
    c = [[10.3, -2.0], [1.5, 2.3], []] # good

are allowed, but ::

    d = [1, 2.5, ’abc’] # bad
    e = [3, [1, 2]] # bad
    f = (0, ’abc’, [1, 2, 3]) # bad

are not allowed. Of course, dictionary keys and values may be of different types: ::

    g = {’a’: 1, ’b’: 2, ’c’: 3} # good
    h = {’a’: 1, ’b’: ’hello’, ’c’: [1, 2, 3]} # bad

In the current version of **Shed Skin**, mixed types are also permitted in tuples of length two: ::

    a = (1, [1]) # good

In the future, mixed tuples up to a certain length will probably be allowed.

``None`` may only be mixed with non-scalar types (i.e., not with ``int`` or ``float``): ::

    l = [1]
    l = None # good

    m = 1
    m = None # bad

    def fun(x = None): # bad: use a special value for x here, e.g. x = -1
        pass
    fun(1)

Integers and floats can often be mixed, but it is better to avoid this where possible, as it may confuse **Shed Skin**: ::

    a = [1.0]
    a = [1] # wrong - use a float here, too


.. _Python Subset Restrictions:

Python Subset Restrictions
--------------------------

**Shed Skin** will only ever support a subset of all Python features. The following common features are currently not supported:

  - reflection (getattr, hasattr), eval, or other really dynamic stuff
  - arbitrary-size arithmetic (integers become 32-bit on most architectures!)
  - generator expressions
  - variable numbers of arguments and keyword arguments
  - multiple inheritance
  - nested functions and classes
  - inheritance from builtins (excluding Exception and object)
  - overloading ``__iter__`` and ``__call__``

Some other features are currently only partially supported:

  - class attributes must always be accessed using a class identifier: ::

        self.class_attr # bad
        SomeClass.class_attr # good

        SomeClass.some_static_method() # good

  - anonymous function passing works reasonably well, but not for methods, and they cannot be contained: ::

        var = lambda x, y: x+y # good
        var = some_func # good
        var = self.some_method # bad
        [var] # bad

.. _Library Limitations:

Library Limitations
-------------------

Programs to be compiled with **Shed Skin** cannot freely use the Python standard library. Only about 20 common modules are currently supported.

Note that **Shed Skin** can be used to build an extension module, so the main program can freely use arbitrary modules (and of course all Python features!). See `Compiling an Extension Module`_.

The following modules are largely supported at the moment. Several of these, such as ``os.path``, were compiled to C++ using **shedskin**.

  - bisect
  - collections
  - ConfigParser
  - copy
  - csv
  - datetime (Pavel Vinogradov, Karel Heyse, FFAO, David Marek)
  - fnmatch (SirNotAppearingInThisTutorial)
  - getopt
  - glob (SirNotAppearingInThisTutorial)
  - heapq (Jeremie Roquet)
  - itertools (Jeremie Roquet)
  - math
  - os (some functionality missing under Windows)
  - os.path
  - random (Jeff Miller)
  - re (SirNotAppearingInThisTutorial; uses libpcre)
  - socket (Michael Elkins)
  - string
  - sys
  - time

See `How to help out in Shed Skin Development`_ on how to help improve or add to the set of supported modules.

.. _Installation:

Installation
------------

The latest version of **Shed Skin** can be downloaded from the `Googlecode site`_. There are three types of packages available: a self-extracting **Windows** installer, a **Debian** (**Ubuntu**) package, and a **UNIX** source package.

**Windows**

To install the **Windows** version, simply download and start it. (If you use **ActivePython** or some other non-standard Python distribution, or **MingW**, please deinstall this first.)

**Debian** (**Ubuntu**)

To install the **Debian** package, simply download and install it using your package manager.

If there are complaints about missing dependencies, the following explicitly installs these:

``sudo apt-get install g++ libpcre3-dev libgc-dev``

**GNU/Linux**

To install the **UNIX** source package on a **GNU/Linux** system, take the following steps:

 - download and unpack it

 - run ``sudo python setup.py install``

 - make sure you can run ``g++``, the C++ compiler

 - install the `Boehm`_ garbage collector

 - install the `PCRE`_ library

on a **Fedora** system, the last three steps are simply:

``sudo yum install gcc-c++ pcre-devel gc-devel``

**FreeBSD**

To install the **UNIX** source package on a **FreeBSD** system, take the following steps:

 - download and unpack it

 - run ``sudo python setup.py install``

 - install the `Boehm`_ garbage collector, making sure to disable threading support:

   ``./configure --enable-cplusplus --disable-threads --prefix=/usr && make install``

 - install the `PCRE`_ library

**OpenSolaris**

To install the **UNIX** source package on an **OpenSolaris** system, take the following steps:

 - download and unpack it

 - run ``sudo python setup.py install``

 - install the following packages: ::

    SUNWgcc
    SUNWhea
    SUNWarc
    SUNWlibgc
    SUNWpcre

**OSX**

To install the **UNIX** source package on an **OSX** system, take the following steps:

 - download and unpack it

 - run ``sudo python setup.py install``

 - install the Apple XCode development environment

 - install the `Boehm`_ garbage collector

 - install the `PCRE`_ library

.. _Compiling and Running a Stand-Alone Program:

Compiling and Running a Stand-Alone Program
-------------------------------------------

To use **Shed Skin** under Windows, first execute (double-click) the ``init.bat`` file in the ``shedskin-0.3`` directory, relative to where you installed it.  A command-line window will appear, with the current directory set to the ``shedskin-0.3\shedskin`` directory (hereafter referred to as the *Shed Skin working directory*).

Consider the following simple test program, called ``test.py``: ::

    # test.py

    print 'hello, world!'

To compile this program to C++, type: ::

    shedskin test

This will create two C++ files, called ``test.cpp`` and ``test.hpp``, as well as a ``Makefile`` and a type-annotated file called ``test.ss.py``.

To create and run an executable file (called ``test.exe`` under Windows or otherwise ``test``), type: ::

    make run

The following output should now appear on the command line: ::

    hello, world!

To only build, but not run the executable file, omit the ``run`` part: ::

    make

For the executable file to execute properly under Windows, note that ``gc.dll`` and ``libpcre-0.dll`` (located in the **Shed Skin** working directory) must be located somewhere in the Windows path. This automatically the case after running ``init.bat``.


.. _Compiling an Extension Module:

Compiling an Extension Module
-----------------------------

Extension modules are compiled binaries, typically written in C or C++ for speed, that can be imported and used like regular Python modules. They allow one to write most of a project in unrestricted Python, while optimizing one or more speed-critical parts.

It is very easy to generate extension modules with **Shed Skin**.

**Simple Example**

We begin with a simple example module, called ``simple_module.py``, containing two simple functions: ::

    # simple_module.py

    def func1(x):
        return x+1

    def func2(n):
        d = dict([(i, i*i)  for i in range(n)])
        return d

    if __name__ == '__main__':
        print func1(5)
        print func2(10)

For type inference to work, the module must (*indirectly*) call its own functions (if ``func1`` calls ``func2``, we can omit the call to ``func2``). This is accomplished in the example by putting the function calls under the ``if __name__=='__main__'`` statement, so that they will not be executed when the module is imported.

To compile the module into an extension module, type: ::

    shedskin -e simple_module
    make

On **UNIX** systems, for 'make' to succeed, make sure to have the Python development files installed (under **Debian**, install ``python-dev``; under **Fedora**, install ``python-devel``).

Depending on platform, the resulting extension module (*shared library*) is called ``simple_module.so`` or ``simple_module.pyd``.

The extension module can now be simply imported and used as usual: ::

    >>> from simple_module import func1, func2
    >>> func1(5)
    6
    >>> func2(10)
    {0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36, 7: 49, 8: 64, 9: 81}

Note that calling ``func1`` with a non-integer argument causes an error: ::

    >>> func1(10.5)
    Traceback (most recent call last):
      File "<pyshell#0>", line 1, in -toplevel-
        func1(10.5)
    TypeError: error in conversion to Shed Skin (integer expected)

It is useful to know which version of the module you are importing: either the **Shed Skin** version (``simple_module.so`` or ``simple_module.pyd``) or the original Python version (``simple_module.py`` or ``simple_module.pyc``). One way to determine this, is to include the following code in the top of the module: ::

    import sys
    print sys.version

**Restrictions**

There are several important restrictions that must be observed when compiling an extension module:

1. Only builtin scalar and container types (``int``, ``float``, ``complex``, ``str``, ``list``, ``tuple``, ``dict``, ``set``, ``frozenset``) as well as ``None`` and instances of user-defined classes can be passed/returned. So for instance, anonymous functions and iterators are currently not supported.

2. Builtin objects are completely converted for each call/return from **Shed Skin** to **CPython** types and back, including their contents. This means you cannot change **CPython** builtin objects from the **Shed Skin** side and vice versa, and conversion may be slow. Instances of user-defined classes can be passed/returned without any conversion, and changed from either side.

3. Global variables are converted once, at initialization time, from **Shed Skin** to **CPython**. This means that the value of the **CPython** version and **Shed Skin** version can change independently. This problem can be avoided by only using constant globals, or by adding getter/setter functions.

**Example for NumPy/SciPy users**

The following example demonstrates how a matrix created in `NumPy`_ can be processed by an extension module generated with **Shed Skin**. The function ``my_sum`` sums all the elements in a matrix: ::

    # simple_module2.py

    def my_sum(a):
        """ compute sum of elements in list of lists (matrix) """
        h = len(a) # number of rows in matrix
        w = len(a[0]) # number of columns
        s = 0.0
        for i in range(h):
            for j in range(w):
                s += a[i][j]
        return s

    if __name__ == '__main__':
        print my_sum([[1.0, 2.0], [3.0, 4.0]])

(This example is given purely as an illustration, since `NumPy`_ arrays already include a built-in ``sum`` method.)

After compiling the module with **Shed Skin**, the ``my_sum`` function can now be used as follows: ::

    >>> import numpy
    >>> from simple_module2 import my_sum
    >>> a = numpy.array(([1.0, 2.0], [3.0, 4.0]))
    >>> my_sum(a.tolist())
    10.0

The ``tolist`` call is necessary here, as **Shed Skin** does not directly support `NumPy`_ types.


.. _Parallel Processing:

Parallel Processing
-------------------
Extension modules generated by **Shed Skin** can be easily combined with parallel processing software such as `Parallel Python`_ and `pprocess`_.

Suppose we have defined the following function in a file, called ``meuk.py``: ::

    # meuk.py

    def part_sum(start, end):
        """ calculate partial sum """
        sum = 0
        for x in xrange(start, end):
            if x % 2 == 0:
                sum -= 1.0 / x
            else:
                sum += 1.0 / x
        return sum

    if __name__ == ’__main__’:
        part_sum(1, 10)

To compile this into an extension module, type: ::

    shedskin -e meuk
    make

**Parallel Python**

To use the generated extension module with `Parallel Python`_ >= 1.5.1, simply add a pure-Python wrapper: ::

    import pp

    def part_sum(start, end):
        import meuk
        return meuk.part_sum(start, end)

    job_server = pp.Server()
    job_server.set_ncpus(2)

    jobs = []
    jobs.append(job_server.submit(part_sum, (1, 10000000)))
    jobs.append(job_server.submit(part_sum, (10000001, 20000000)))

    print sum([job() for job in jobs])

**pprocess**

To use the generated extension module with `pprocess`_, follow the same approach: ::

    import pprocess

    def part_sum(start, end):
       import meuk
       return meuk.part_sum(start, end)

    results = pprocess.Map(limit=2)
    part_sum = results.manage(pprocess.MakeParallel(part_sum))

    part_sum(1, 10000000)
    part_sum(10000001, 20000000)

    print sum(results)


.. _Calling C/C++ Code:

Calling C/C++ Code
------------------

To call manually written C/C++ code, follow these steps:

1. Provide **Shed Skin** with enough information to perform type inference, by providing it with a *type model* of the C/C++ code. Suppose we wish to call a simple function that returns a list with the n smallest prime numbers larger than some number. The following type model, contained in a file called ``stuff.py``, is sufficient for **Shed Skin** to perform type inference: ::

    #stuff.py

    def more_primes(n, nr=10):
        return [1]

2. To actually perform type inference, create a test program, called ``test.py``, that uses the type model, and compile it: ::

    #test.py

    import stuff
    print stuff.more_primes(100)

    shedskin test

3. Besides ``test.py``, this also compiles ``stuff.py`` to C++. Now you can fill in manual C/C++ code in ``stuff.cpp``. To avoid that it is overwritten the next time ``test.py`` is compiled, move ``stuff.*`` to the **Shed Skin** ``lib/`` dir.

**Standard Library**

By moving ``stuff.*`` to ``lib/``, we have in fact added support for an arbitrary module to **Shed Skin**. Other programs compiled by **Shed Skin** can now import ``stuff`` and use ``more_primes``. There is no difference with adding support for a *standard library* module. In fact, in the ``lib/`` directory, you can find type models and implementations for all supported modules (see `Library Limitations`_). As you may notice, some have been partially converted to C++ using **Shed Skin**.

**Shed Skin Types**

**Shed Skin** reimplements the Python builtins with its own set of C++ classes (built on the C++ Standard Template Library). These have a similar interface to their Python counterparts, so they should be easy to use (provided you have some basic C++ knowledge.) See the class definitions in ``lib/builtin.hpp`` for details. If in doubt, convert some equivalent Python code to C++, and have a look at the result!

.. _Command-line Options:

Command-line Options
--------------------

The ``shedskin`` command can be given the following options: ::

    -a --ann               Output annotated source code (.ss.py)
    -b --nobounds          Disable bounds checking
    -d --dir               Specify alternate directory for output files
    -e --extmod            Generate extension module
    -f --flags             Provide alternate Makefile flags
    -r --random            Use fast random number generator
    -w --nowrap            Disable wrap-around checking

For example, to compile the file ``test.py`` as an extension module, type ``shedskin –e test`` or ``shedskin ––extmod test``.

In Python, exceptions are raised for index out-of-bounds errors, as in the following example. Because checking for these errors can slow down certain programs, it can be turned off with the ``--nobounds`` option. ::

    a = [1, 2, 3]
    print a[5] # invalid index: out of bounds

Also, negative index values can often be used to count 'backwards' (``a[-1]`` in the example). Because checking for this can also slow down certain programs, it can be turned off with the ``--nowrap`` option.

.. _Tips and Tricks:

Tips and Tricks
---------------

**Performance**

1. Allocating many small objects (e.g. by using ``zip``) typically does not slow down Python programs by much. However, after compilation to C++, it can quickly become a bottleneck. The key to getting excellent performance is to allocate as few objects as possible.

2. **Shed Skin** takes the flags it sends to the C++ compiler from the ``FLAGS`` file in the **Shed Skin** working directory. These flags can be modified or overruled by creating a local file with the same name, or by directly editing the generated Makefile. The following flags typically give good results: ::

    -O3 -s -fomit-frame-pointer -msse2

3. Profile-guided optimization can help to squeeze out even more performance. For a recent version of GCC, first compile and run the generated code with ``-fprofile-generate``, then with ``fprofile-use``.

4. Several Python features (that may slow down generated code) are not always necessary, and can be turned off. See the section `Command-line Options`_ for details.

5. When optimizing, it is extremely useful to know exactly how much time is spent in each part of your program. The program `Gprof2Dot`_ can be used to generate beautiful graphs for both the Python code and the compiled code.

**Tricks**

1. The following two code fragments work the same, but only the second one is supported (using attributes also much faster in C++!): ::

    statistics = {'nodes': 28, 'solutions': set()}

    class statistics: pass
    s = statistics(); s.nodes = 28; s.solutions = set()

2. The evaluation order of arguments to a function or ``print`` changes with translation to C++, so it's better not to depend on this: ::

    print 'hoei', raw_input() # raw_input is called before printing 'hoei'!

3. Tuples with different types of elements and length > 2 are not supported. It can however be useful to 'simulate' them: ::

    a = (1, '1', 1.0) # bad
    a = (1, ('1', 1.0)) # good

.. _How to help out in Shed Skin Development:

How to help out in Shed Skin Development
----------------------------------------

Open source projects, especially new ones such as **Shed Skin**, thrive on user feedback. Please send in bug reports, patches or other code, or suggestions about this document; or join the mailing list and start or participate in discussions (see the `Googlecode site`_.)

If you are a student, you might want to consider applying for the yearly Google `Summer of Code`_ or `GHOP`_ projects. **Shed Skin** has so far successfully participated in one Summer of Code and one GHOP.

I would like to thank the following company/people, for their help with **Shed Skin** so far:

* Google
* Bearophile
* Brian Blais
* Paul Boddie
* Djamel Cherif
* Mark Dewing
* James Coughlan
* Michael Elkins
* FFAO
* Luis M. Gonzales
* Karel Heyse
* Denis de Leeuw Duarte
* Van Lindberg
* David Marek
* Douglas McNeil
* Jeff Miller
* Joaquin Abian Monux
* Harri Pasanen
* Jeremie Roquet
* SirNotAppearingInThisTutorial
* Joris van Rantwijk
* Thomas Spura
* Dave Tweed
* Jaroslaw Tworek
* Pavel Vinogradov

As well as all the people that wrote and shared the 44 example programs.
