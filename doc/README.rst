Shed Skin Tutorial
==================

:Version: Shed Skin 0.0.29
:Date: September 20, 2008
:Authors: Mark Dufour and James Coughlan

.. _Parallel Python: http://www.parallelpython.com/
.. _Googlecode Site: http://shedskin.googlecode.com/
.. _pprocess: http://www.boddie.org.uk/python/pprocess.html
.. _numpy: http://numpy.scipy.org/
.. _quameon: http://quameon.sourceforge.net/
.. _Summer of code: http://code.google.com/soc/
.. _GHOP: http://code.google.com/opensource/ghop/
.. _Boehm: http://www.hpl.hp.com/personal/Hans_Boehm/gc/ 

.. contents::

.. _Purpose of this Tutorial:

Purpose of this Tutorial
------------------------

This tutorial provides an overview of **Shed Skin** and its limitations, as well as step-by-step instructions on how to use it to compile and run standalone programs and modules callable from regular Python code. 

.. _Introduction:

Introduction
------------

**Shed Skin** is an *experimental* **Python-to-C++ compiler** designed to speed up the execution of computation-intensive Python programs. It converts programs written in a *static subset* of Python to C++. The C++ code can be compiled to executable code, which can be run either as a standalone program or as a module easily imported and called from Python. 

**Shed Skin** uses type inference techniques to determine the *implicit* types used in a Python program, in order to generate the *explicit* type declarations needed in a C++ version. Because C++ is *statically typed*, **Shed Skin** requires Python code to be written such that all variables are (implicitly) statically typed.

Besides the *typing* and *subset* restrictions, supported programs cannot freely use the Python standard library, although the most common modules are supported, such as ``math`` and ``random`` (see `Library Limitations`_). 

Additionally, the type inference techniques employed by **Shed Skin** currently do not scale very well beyond several hundred lines of code (the largest compiled program is about 1,600 lines). In all, this means that **Shed Skin** is currently mostly useful to compile *smallish* programs and extension modules, that do not make extensive use of dynamic Python features or the standard library.

Because **Shed Skin** is still in a very early stage of development, it can also improve a lot. At the moment, you will probably run into some bugs when using it. Please report these, so they can be fixed! 

At the moment, **Shed Skin** is only compatible with Python versions 2.3 to 2.5, and should work on GNU/Linux platforms, FreeBSD, OpenSolaris, OSX and Windows XP.

.. _Typing Restrictions:

Typing Restrictions
-------------------

**Shed Skin** translates pure, but *implicitly statically typed*, Python programs into C++. The static typing restriction means that variables can only ever have a *single, static type*. So, for example, ::

    a = 1; a = ’1’ # bad

is not allowed. However, as in C++, types can be *abstract* or *generic*, so that, for example, ::

    a = A(); a = B() # good

where **A** and **B** have a common base class, is allowed. (See `Tips and Tricks`_ for an example of a generic type.) 

The typing restriction also means that the elements of some collection (``list``, ``set``, etc.) cannot have different types (because their *subtype* must also be static). Thus: ::

    a=[’apple’, ’b’, ’c’] # good
    b=(1, 2, 3) # good
    c=[[10.3, -2.0], [1.5, 2.3], []] # good

are allowed, but ::

    d=[1, 2.5, ’abc’] # bad
    e=[3, [1,2]] # bad
    f=(0,’abc’,[1,2,3]) # bad

are not allowed. Of course, dictionary keys and values can be of different types: ::

    g={’a’:1, ’b’:2, ’c’:3} # good
    h={’a’:1, ’b’:’hello’, ’c’:[1,2,3]} # bad

In the current version of **Shed Skin**, mixed types are also permitted in tuples of length two: ::

    a=(1, [1]) # good

In the future, mixed tuples up to a certain length will be allowed.

``None`` may only be mixed with non-scalar types (i.e., not with ``int`` or ``float``): ::

    l = [1]
    l = None # good

    m = 1
    m = None # bad

    def fun(x=None): pass # bad: use a special value for x here, e.g. x=-1
    fun(1) 

Integers and floats can often be mixed, but it is better to avoid this where possible, as it may confuse **Shed Skin**: ::

    a = [1.0] 
    a = [1] # wrong - use a float here, too


.. _Python Subset Restrictions:

Python Subset Restrictions
--------------------------

**Shed Skin** will only ever support a subset of all Python features. The following common features are currently not supported:

  - variable numbers of arguments and keyword arguments 
  - arbitrary-size arithmetic (integers become 32-bit on a 32-bit architecture!)
  - reflection (getattr, hasattr), eval, or other really dynamic stuff
  - multiple inheritance
  - generator expressions
  - nested functions and classes
  - inheritance from builtins (excluding Exception and object) 

Some other features are currently only partially supported:

  - class attributes must always be accessed using a class identifier: ::

        self.class_attr # bad
        bla.class_attr # good

  - anonymous function passing works reasonably well, but not for methods, and placing them in containers potentially confuses **Shed Skin**: ::

        var = lambda x,y: x+y # good
        [var] # asking for trouble
        method_ref = self.some_method # bad

.. _Library Limitations:

Library Limitations
-------------------

Programs to be compiled with **Shed Skin** cannot freely use the Python standard library. Only about 17 common modules are currently supported. 

Note that **Shed Skin** can be used to build an extension module, so the main program can use arbitrary modules (and of course all Python features!). See `Compiling an Extension Module`_. 

In general, programs can only import functionality that is defined in the **Shed Skin** ``lib/`` directory. The following modules are largely supported at the moment: 

  - bisect
  - collections
  - ConfigParser
  - copy
  - datetime
  - fnmatch
  - getopt
  - glob
  - math
  - os (needs more work, especially under Windows)
  - os.path 
  - random
  - re
  - socket 
  - string
  - sys 
  - time 

For version **0.1** of **Shed Skin**, complete support for ``os`` is planned. (See `How to help out in Shed Skin Development`_ on how to help improve or add to these modules.)

.. _Installation:

Installation
------------

The latest version of **Shed Skin** can be downloaded from the `Googlecode site`_. There are three types of packages available: a self-extracting **Windows** installer, a **Debian** package, and a UNIX source package. 

To install the **Windows** version, simply download and start it. (If you use ActivePython or some other non-standard Python distribution, please deinstall this first.)

To install the **Debian** package, simply download and install it using your package manager. 

To install the UNIX source package on a **GNU/Linux** system, take the following steps:

 - download and unpack it 

 - run ``python setup.py`` and place the generated ``shedskin`` file in your path 

 - make sure you can run ``g++``, the C++ compiler

 - install the Boehm garbage collector
 
   on a **Debian** system, this is simply:
    
   ``sudo apt-get install libgc-dev``

   on a **Fedora** system, this is simply:
   
   ``sudo yum install gc-devel``

 - install the PCRE library:
 
   on a **Debian** system this is simply:

   ``sudo apt-get install libpcre3-dev``

   on a **Fedora** system, this is simply:

   ``sudo yum install pcre-devel``

To install the UNIX source package on a **FreeBSD** system, take the following steps:

 - download and unpack it
 
 - run ``python setup.py`` and place the generated ``shedskin`` file in your path 

 - install the Boehm garbage collector (optionally using the latest version from `Boehm`_)
   
   make sure to disable threading support, e.g. using a tarball:

   ``./configure --enable-cplusplus --disable-threads --prefix=/usr && make install``

 - install the PCRE library:

   from a tarball:

   ``./configure && make install``

To install the UNIX source package on an **OpenSolaris** system, take the following steps:

 - download and unpack it
 
 - run ``python setup.py`` and place the generated ``shedskin`` file in your path 

 - install the following packages:

   ``SUNWgcc``
   ``SUNWhea``
   ``SUNWarc``
   ``SUNWlibgc``
   ``SUNWpcre``

To install the UNIX source package on an **OSX** system, take the following steps:

 - download and unpack it

 - run ``python setup.py`` and place the generated ``shedskin`` file in your path 

 - install the Apple XCode development environment

 - install the Boehm garbage collector; without a package manager, download the source package and run: 
    
   ``./configure && sudo make install``

 - install the PCRE library; without a package manager, download the source package and run: 

   ``./configure && sudo make install``

.. _Compiling and Running a Stand-Alone Program:

Compiling and Running a Stand-Alone Program
-------------------------------------------

To use **Shed Skin** under Windows, first execute (double-click) the ``init.bat`` file in the ``shedskin-0.0.28`` directory, relative to where you installed it.  A command-line window will appear, with the current directory set to the ``shedskin-0.0.28\shedskin`` directory (hereafter referred to as the *Shed Skin working directory*).

Suppose we have defined a simple test program, called ``test.py``: ::

    print 'hello, world!'

To compile this program to C++, type: ::

    shedskin test

This will create two C++ files, called ``test.cpp`` and ``test.hpp``, as well as a type-annotated file called ``test.ss.py``.

To create and run an executable file (called ``test.exe`` under Windows or otherwise ``test``), type: ::

    make run

The following output should now appear on the command line: ::

    hello, world!

To only build, but not run the executable file, omit the ``run`` part: ::

    make

For the executable file to execute properly under Windows, note that ``gc.dll`` and ``libpcre-0.dll`` (located in the **Shed Skin** working directory) must be located somewhere in the Windows path. This happens automatically when running ``init.bat``. 


.. _Compiling an Extension Module:

Compiling an Extension Module
-----------------------------

The ability to build extension modules is useful since it permits the use of unrestricted Python code in the 'main' program, while still allowing the speedup of compiling speed-critical parts with **Shed Skin**.

**Simple Example**

We begin with a simple example module, called ``simple_module.py``, containing two simple functions: ::

    #simple_module.py
    def func1(x):
        return x+1

    def func2(n):
        d=dict([(i, i*i)  for i in range(n)])
        return d

    # In order for type inference to work, 
    # we must show Shed Skin how functions will be called:
    if __name__ == '__main__':
        print func1(5)
        print func2(10)

In order for type inference to work, note that the module must (*indirectly*) call its own functions (if ``func1`` calls ``func2``, we can omit the call to ``func2``). This is accomplished in the example by putting the function calls in the ``if __name__=='__main__'`` statement, so that they will not be executed when the module is imported.

To compile the module into an extension module, type: ::

    shedskin -e simple_module
    make

Depending on platform, the resulting extension module (*shared library*) is called ``simple_module.so`` or ``simple_module.pyd``.

The extension module can now be simply imported as usual: ::

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

This error would not arise in standard Python, but arises with **Shed Skin** since it infers *specific* argument types for each function, based on how it is called in the module.
 
It is useful to know which version of the module you are importing: either the **Shed Skin** version (``simple_module.so`` or ``simple_module.pyd``) or the original Python version (``simple_module.py`` or ``simple_module.pyc``). One way to determine this, is to include the following code in the top of the module: ::

    import sys
    print sys.version

**Restrictions**

There are several important restrictions that must be observed when compiling an extension module:

1. Only builtin scalar and container types (``int``, ``float``, ``str``, ``list``, ``tuple``, ``dict``, ``set``) as well as ``None`` can be passed/returned. Support for custom classes will be added in a later version of **Shed Skin**.

2. Objects are completely converted for each call/return from **Shed Skin** to **CPython** types and back, including all of their contents. This means you cannot directly change **CPython** objects from the **Shed Skin** side and vice versa, and that conversion may become a bottleneck.

3. Global module variables are converted at module initialization time, and cannot be changed later on from the **Shed Skin** side.

**Example for NumPy/SciPy users**

The following example demonstrates how a matrix created in `NumPy`_ can be processed by a module compiled with **Shed Skin**. The function ``my_sum`` sums all the elements in a matrix: ::

    #simple_module2.py
    #function to compute sum of elements in list of lists (matrix):
    def my_sum(a):
        h=len(a) #number of rows in matrix
        w=len(a[0]) #number of columns
        s=0.
        for i in range(h):
            for j in range(w):
                s += a[i][j]
        return s

    # In order for type inference to work, 
    # we must show how functions will be (indirectly) called:
    if __name__ == '__main__':
        a=[[1.,2.],[3.,4.]]
        print my_sum(a)

(This example is given purely as an illustration, since `NumPy`_ arrays already include a built-in ``sum`` method.) 

After compiling the module with **Shed Skin**, the ``my_sum`` function can now be used as follows: ::

    >>> import numpy
    >>> from simple_module import my_sum
    >>> a=numpy.array(([1.,2.],[3.,4.]))
    >>> my_sum(a.tolist())
    10.0

The ``tolist`` call is necessary here, as **Shed Skin** does not directly support `NumPy`_ types.


.. _Parallel Processing:

Parallel Processing
-------------------
Extension modules generated by **Shed Skin** can be easily combined with parallel processing software such as `Parallel Python`_ and `pprocess`_. 

Suppose we have defined the following function in a file, called ``meuk.py``: ::

    def part_sum(start, end):
        """Calculates partial sum"""
        sum = 0
        for x in xrange(start, end):
            if x % 2 == 0:
                sum -= 1.0 / x
            else:
                sum += 1.0 / x
        return sum

    if __name__ == ’__main__’:
        part_sum(1, 10)

To use this module with `Parallel Python`_ or `pprocess`_, we must first compile it into an extension module (see `Compiling an Extension Module`_): ::

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

To use the extension module with `pprocess`_, follow the same approach: ::

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

3. Besides ``test.py``, this also compiles ``stuff.py`` to C++. Now you can fill in manual C/C++ code in ``stuff.cpp``. But to avoid that it is overwritten the next time ``test.py`` is compiled, first move ``stuff.*`` to the **Shed Skin** ``lib/`` dir. 

**Standard Library**

By moving ``stuff.*`` to ``lib/``, we have in fact added support for an arbitrary module to **Shed Skin**. Other programs compiled by **Shed Skin** can now import ``stuff`` and use ``more_primes``. There is no difference with adding support for a *standard library* module. In fact, in the ``lib/`` directory, you can find type models and implementations for all supported modules (see `Library Limitations`_). As you may notice, some have been partially converted to C++ using **Shed Skin**. 

**Shed Skin Types**

**Shed Skin** reimplements the Python builtins with its own set of C++ classes, built on the C++ Standard Template Library. They have a similar interface, so they should be easy to use (provided you have some basic C++ knowledge.) See the class definitions in ``lib/builtin.hpp`` for details. If in doubt, convert some equivalent Python code to C++, and have a look at the result.

.. _Command-line Options:

Command-line Options
--------------------

The ``shedskin`` command has the following options: ::

    -a --noann             Don't output annotated source code
    -b --bounds            Enable bounds checking
    -d --dir               Specify alternate directory for output files
    -e --extmod            Generate extension module
    -f --flags             Provide alternate Makefile flags
    -i --infinite          Try to avoid infinite analysis time 
    -w --nowrap            Disable wrap-around checking 

(To see an up-to-date list of these options simply type ``shedskin`` without any argument.)

For example, to use the bounds checking option to compile ``test.py``, type ``shedskin –b test`` or ``shedskin ––bounds test``. 

The ``--bounds`` option is used to catch index out-of-bounds errors in lists, tuples and strings, which would produce errors in **CPython**.  Without it, the following erroneous code would give a spurious value rather than reporting an error: ::

    a=[1,2,3]
    print a[5] # invalid index: out of bounds

The ``--nowrap`` option can speed up program execution by a modest amount, at the risk of giving wrong values for negative indices (``a[-1]`` in the above example.) Before using this option, make sure that your code will run safely with it.

.. _Tips and Tricks:

Tips and Tricks
---------------

**Tips**

1. When recompiling an extension module, ``make`` will fail if the ``.pyd`` or ``.so`` file can’t be overwritten. This problem may occur when using **IPython**: after importing a module, it is impossible to overwrite the ``.pyd`` or ``.so`` file as long as **IPython** is kept open.

2. If you modify a module after compiling it with **Shed Skin**, you may find yourself unable to import the new version (e.g. to test it in **CPython** before recompiling with **Shed Skin**) until you delete the corresponding ``.pyd`` or ``.so`` file.
 
3. **Shed Skin** takes the flags it sends to the C++ compiler from the ``FLAGS`` file in the **Shed Skin** working directory. These flags can be overridden by creating a local file with the same name.

4. Allocating many small objects (e.g. by using ``zip``) typically does not slow down Python programs by much. However, after compilation to C++, it can quickly become a bottleneck. 

**Tricks**

1. The used type inference techniques can end up in an infinite loop, especially for larger programs. If this happens, it sometimes helps to run **Shed Skin** with the ``--infinite`` command-line option.

2. The following two code fragments work the same, but only the second one is supported: ::

    statistics = {'nodes': 28, 'solutions': set()}
   
    class statistics: pass
    s = statistics(); s.nodes = 28; s.solutions = set()

3. The evaluation order of arguments to a function or ``print`` changes with translation to C++, so it's better not to depend on this: ::

    print 'hoei', raw_input() # raw_input is called first!

4. Tuples with different types of elements and length > 2 are not supported. It can however be useful to 'simulate' them: ::

    a = (1, '1', 1.0) # bad
    a = (1, ('1', 1.0)) # good

5. The following example shows how to model a *generic* type: ::

    class matrix:
        def __init__(self, hop):
            self.unit = hop

    m1 = matrix([1])
    m2 = matrix([1.0])

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
* Jeff Miller
* Joaquin Abian Monux
* Harri Pasanen
* SirNotAppearingInThisTutorial
* Dave Tweed
* Jaroslaw Tworek
* Pavel Vinogradov

.. _Roadmap:

Shed Skin Roadmap
-----------------

The following activities are planned for future versions of **Shed Skin**:

**0.1** (6-12 months from now)

* Complete support for the ``os`` module, and all modules mentioned in `Library Limitations`_.

* Improve the type inference techniques with at least *iterative deepening* and basic selector-based *filters*.

* Compile at least one program of around 3,000 lines, for example `Quameon`_.  

* Improve **Shed Skin** ``set`` efficiency to be similar to that of CPython ``set``.

**0.2** (12-24 months from now)

* Replace many quick hacks in the compiler core

* Perform several major cleanups.

* Improve readability of generated code.

* Locate bugs using some Python regression test suite, and fix them.

* Improve packaging of generated code

* Add support for tuples with mixed elements up to a certain length

**0.9** (18-36 months from now)

* Efficient and complete extension module support.

* Improve type inference to the point where it works for typical, arbitrary programs of around 3,000 lines.

* Add support for multiple inheritance, generator expressions and nested functions

* Add basic stack allocation, out-of-bounds and wrap-around optimizations.

