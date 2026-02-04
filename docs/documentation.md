# Shed Skin Documentation

## Introduction

Shed Skin is an experimental Python-to-C++ compiler designed to speed up the execution of computation-intensive Python programs. It converts programs written in a restricted subset of Python to C++. The C++ code can be compiled to executable code, which can be run either as a standalone program or as an extension module that can be imported and used in larger Python programs.

Shed Skin uses type inference techniques to determine the implicit types used in a Python program, in order to generate the explicit type declarations needed in a C++ version. Because C++ is statically typed, Shed Skin requires Python code to be written such that all variables are (implicitly!) statically typed.

Besides the typing and subset restrictions, supported programs cannot freely use the Python standard library, although about 30 common modules are (partially) supported, such as `random` and `re` (see [Library limitations](#library-limitations)).

Additionally, the type inference techniques employed by Shed Skin currently do not scale very well beyond several thousand lines of code (the largest compiled program is about 6,000 lines (sloccount)). In all, this means that Shed Skin is currently mostly useful to compile smallish programs and extension modules, that do not make extensive use of dynamic Python features or the standard or external libraries.

Because Shed Skin is still in an early stage of development, it can also improve a lot. At the moment, you will probably run into some bugs when using it. Please report these, so they can be fixed!

## Typing Restrictions

Shed Skin translates pure, but implicitly statically typed, Python programs into C++. The static typing restriction means that variables can only ever have a single, static type. So, for example,

```python
a = 1
a = '1' # bad
```

is not allowed. However, as in C++, types can be abstract, so that for example,

```python
a = A()
a = B() # good
```

where A and B have a common base class, is allowed.

The typing restriction also means that the elements of some collection (list, set, etc.) cannot have different types (because their subtype must also be static). Thus:

```python
a = ['apple', 'b', 'c'] # good
b = (1, 2, 3) # good
c = [[10.3, -2.0], [1.5, 2.3], []] # good
```

is allowed, but

```python
d = [1, 2.5, 'abc'] # bad
e = [3, [1, 2]] # bad
f = (0, 'abc', [1, 2, 3]) # bad
```

is not allowed. Dictionary keys and values may be of different types:

```python
g = {'a': 1, 'b': 2, 'c': 3} # good
h = {'a': 1, 'b': 'hello', 'c': [1, 2, 3]} # bad
```

In the current version of Shed Skin, mixed types are also permitted in tuples of length two:

```python
a = (1, [1]) # good
```

In the future, mixed tuples up to a certain length will probably be allowed.

None may only be mixed with non-scalar types (i.e., not with int, float, bool or complex):

```python
l = [1]
l = None # good

m = 1
m = None # bad

def fun(x = None): # bad: use a special value for x here, e.g. x = -1
    pass
fun(1)
```

Integers and floats can usually be mixed (the integers become floats). Shed Skin should complain in cases where they can't.

## Python Subset Restrictions

Shed Skin will only ever support a subset of all Python features. The following common features are currently not supported:

* `eval`, `getattr`, `hasattr`, `isinstance`, anything really dynamic
* arbitrary-size arithmetic (integers become 32-bit (signed) by default on most architectures, see [Command-line options](#command-line-options))
* argument (un)packing (`*args` and `**kwargs`)
* multiple inheritance
* nested functions and classes
* full unicode support (currently restricted to 1-byte characters)
* inheritance from builtins (excluding `Exception` and `object`)
* closures

Some other features are currently only partially supported:

* class attributes must always be accessed using a class identifier:

```python
self.class_attr # bad
SomeClass.class_attr # good
SomeClass.some_static_method() # good
```

* function references can be passed around, but not method references or class references, and they cannot be contained:

```python
var = lambda x, y: x+y # good
var = some_func # good
var = self.some_method # bad, method reference
var = SomeClass # bad
[var] # bad, contained
```

## Library Limitations

At the moment, the following 30 modules are (fully or partially) supported. Several of these, such as `os.path`, were compiled to C++ using Shed Skin.

* `array`
* `binascii`
* `bisect`
* `collections` (defaultdict, deque)
* `colorsys`
* `configparser` (no SafeConfigParser)
* `copy`
* `csv` (no Dialect, Sniffer)
* `datetime`
* `fnmatch`
* `functools` (reduce)
* `gc` (enable, disable, collect)
* `getopt`
* `glob`
* `heapq`
* `io` (BytesIO, StringIO)
* `itertools` (no starmap)
* `math`
* `mmap`
* `os`
* `os.path`
* `random`
* `re`
* `select` (select)
* `socket`
* `string`
* `struct` (no Struct, iter_unpack)
* `sys`
* `time`

Note that any other module, such as `pygame`, `pyqt` or `pickle`, may be used in combination with a Shed Skin generated extension module. For examples of this, see the [Shed Skin examples](https://github.com/shedskin/shedskin/tree/master/examples).

See [How to help out in development](#how-to-help-out-in-development) on how to help improve or add to the set of supported modules.

## Installation

### GNU/Linux

#### From Distribution

Example command for when using Ubuntu:

```bash
sudo apt-get install shedskin
```

#### Manual Installation

To manually install the UNIX tarball, take the following steps:

* download and unpack tarball
* run:

```bash
sudo python setup.py install
```

#### Dependencies

To compile and run programs produced by shedskin the following libraries are needed:

* g++, the C++ compiler (version 4.2 or higher).
* pcre2 development files
* Python development files
* Boehm garbage collection

To install these libraries under Ubuntu, type:

```bash
sudo apt-get install g++ libpcre2-dev python-all-dev libgc-dev
```

If the Boehm garbage collector is not available via your package manager, the following is known to work. Download for example version 7.2alpha6 from the [website](http://www.hboehm.info/gc/), unpack it, and install it as follows:

```bash
./configure --prefix=/usr/local --enable-threads=posix --enable-cplusplus --enable-thread-local-alloc --enable-large-config
make
make check
sudo make install
```

If the PCRE2 library is not available via your package manager, the following is known to work. Download for example version 10.44 from the [website](http://www.pcre.org/), unpack it, and build as follows:

```bash
./configure --prefix=/usr/local
make
sudo make install
```

### OSX

#### Manual Installation

To install the UNIX tarball on an **OSX** system, take the following steps:

* download and unpack tarball
* run:

```bash
sudo python setup.py install
```

#### Dependencies

To compile and run programs produced by shedskin the following libraries are needed:

* g++, the C++ compiler (version 4.2 or higher; comes with the Apple XCode development environment?)
* pcre2 development files
* Python development files
* Boehm garbage collection

If the Boehm garbage collector is not available via your package manager, the following is known to work. Download for example version 7.2alpha6 from the [website](http://www.hboehm.info/gc/), unpack it, and install it as follows:

```bash
./configure --prefix=/usr/local --enable-threads=posix --enable-cplusplus --enable-thread-local-alloc --enable-large-config
make
make check
sudo make install
```

If the PCRE2 library is not available via your package manager, the following is known to work. Download for example version 10.44 from the [website](http://www.pcre.org/), unpack it, and build as follows:

```bash
./configure --prefix=/usr/local
make
sudo make install
```

### Windows

Install the following dependencies:

* Microsoft Visual Studio Build Tools (enable CMake in installation process)
* CMake
* Conan 1.62.0 (`pip install 'conan==1.62.0'`)

## Compiling a Standalone Program

To compile the following simple test program, called `test.py`:

```python
print('hello, world!')
```

Under Linux/macOS, type:

```bash
shedskin build test
```

This will create a `build` directory, containing the generated C++ code and binary.

Under Windows (note that this will download dependencies), type:

```bash
shedskin build --conan test
```

If there is an error about `nmake` not being found, you may have to enter a "visual studio developer command prompt" first.

Under Linux/macOS, the binary is named `build/test`. Under Windows, it is named `build/Debug/test.exe`.

## Generating an Extension Module

To compile the following program, called `simple_module.py`, as an extension module:

```python
# simple_module.py

def func1(x):
    return x+1

def func2(n):
    d = dict([(i, i*i)  for i in range(n)])
    return d

if __name__ == '__main__':
    print(func1(5))
    print(func2(10))
```

Type:

```bash
shedskin build -e simple_module
```

For this to succeed, make sure to have the Python development files installed (under **Debian**, install `python-dev`; under **Fedora**, install `python-devel`).

Note that for type inference to be possible, the module must (indirectly) call its own functions. This is accomplished in the example by putting the function calls under the `if __name__=='__main__'` statement, so that they are not executed when the module is imported. Functions only have to be called indirectly, so if func2 calls func1, the call to func1 can be omitted.

The extension module can now be simply imported and used as usual (first change to `build/` under Linux/macOS, or `build/Debug` under Windows):

```python
>>> from simple_module import func1, func2
>>> func1(5)
6
>>> func2(10)
{0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25, 6: 36, 7: 49, 8: 64, 9: 81}
```

### Limitations

There are some important differences between using the compiled extension module and the original.

1. Only builtin scalar and container types (`int`, `float`, `complex`, `bool`, `str`, `bytes`, `bytearray`, `list`, `tuple`, `dict`, `set`) as well as `None` and instances of user-defined classes can be passed/returned. So for instance, anonymous functions and iterators are currently not supported.
2. Builtin objects are completely converted for each call/return from Shed Skin to CPython types and back, including their contents. This means you cannot change CPython builtin objects from the Shed Skin side and vice versa, and conversion may be slow. Instances of user-defined classes can be passed/returned without any conversion, and changed from either side.
3. Global variables are converted once, at initialization time, from Shed Skin to CPython. This means that the value of the CPython version and Shed Skin version can change independently. This problem can be avoided by only using constant globals, or by adding getter/setter functions.
4. Multiple (interacting) extension modules are not supported at the moment. Also, importing and using the Python version of a module and the compiled version at the same time may not work.

### Numpy Integration

Shed Skin does not currently come with direct support for Numpy. It is possible however to pass a Numpy array to a Shed Skin compiled extension module as a list, using its `tolist` method. Note that this is very inefficient (see above), so it is only useful if a relatively large amount of time is spent inside the extension module. Consider the following example:

```python
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
    print(my_sum([[1.0, 2.0], [3.0, 4.0]]))
```

After compiling this module as an extension module with Shed Skin, we can pass in a Numpy array as follows:

```python
>>> import numpy
>>> import simple_module2
>>> a = numpy.array(([1.0, 2.0], [3.0, 4.0]))
>>> simple_module2.my_sum(a.tolist())
10.0
```

## Distributing Binaries

To use a generated (linux/OSX) binary on another system, make sure `libgc` and `libpcre2-8-0` are installed there. If they are not, and you cannot install them globally, you can place copies of these libraries into the same directory as the binary, using the following approach:

```bash
$ ldd test
libgc.so.1 => /usr/lib/libgc.so.1
libpcre2-8.so.0 => /lib/x86_64-linux-gnu/libpcre2-8.so.0
$ cp /usr/lib/libgc.so.1 .
$ cp /lib/x86_64-linux-gnu/libpcre2-8.so.0 .
$ LD_LIBRARY_PATH=. ./test
```

Note that both systems have to be 32- or 64-bit for this to work. If not, Shed Skin must be installed on the other system, to recompile the binary.

## Multiprocessing

Suppose we have defined the following function in a file, called `meuk.py`:

```python
def part_sum(start, end):
    """ calculate partial sum """
    sum = 0
    for x in range(start, end):
        if x % 2 == 0:
            sum -= 1.0 / x
        else:
            sum += 1.0 / x
    return sum

if __name__ == '__main__':
    part_sum(1, 10)
```

To compile this into an extension module, type:

```bash
shedskin build -e meuk
cp build/meuk.so .
```

To use the generated extension module with the `multiprocessing` standard library module, simply add a pure-Python wrapper:

```python
from multiprocessing import Pool

def part_sum((start, end)):
    import meuk
    return meuk.part_sum(start, end)

pool = Pool(processes=2)
print(sum(pool.map(part_sum, [(1,10000000), (10000001, 20000000)])))
```

## Calling C/C++ Code

To call manually written C/C++ code, follow these steps:

* Provide Shed Skin with enough information to perform type inference, by providing it with a *type model* of the C/C++ code. Suppose we wish to call a simple function that returns a list with the n smallest prime numbers larger than some number. The following type model, contained in a file called `stuff.py`, is sufficient for Shed Skin to perform type inference:

```python
#stuff.py

def more_primes(n, nr=10):
    return [1]
```

* To actually perform type inference, create a test program, called `test.py`, that uses the type model, and compile it:

```python
#test.py

import stuff
print(stuff.more_primes(100))
```

```bash
shedskin build test
```

* Besides `test.py`, this also compiles `stuff.py` to C++. Now you can fill in manual C/C++ code in `stuff.cpp`. To avoid that it is overwritten the next time `test.py` is compiled, move `stuff.*` to the Shed Skin `lib/` dir.

### Standard Library

By moving `stuff.*` to `lib/`, we have in fact added support for an arbitrary library module to Shed Skin. Other programs compiled by Shed Skin can now import `stuff` and use `more_primes`. In fact, in the `lib/` directory, you can find type models and implementations for all supported modules. As you may notice, some have been partially converted to C++ using Shed Skin.

### Shed Skin Types

Shed Skin reimplements the Python builtins with its own set of C++ classes. These have a similar interface to their Python counterparts, so they should be easy to use (provided you have some basic C++ knowledge.) See the class definitions in `lib/builtin.hpp` for details. If in doubt, convert some equivalent Python code to C++, and have a look at the result!

## Command-line Options

shedskin has recently adopted a command-line api with subcommands:

```
$ shedskin --help
usage: shedskin [-h] {analyze,translate,build,run,test} ...

Restricted-Python-to-C++ Compiler

options:
  -h, --help            show this help message and exit

subcommands:
    analyze             analyze and validate python module
    translate           translate python module to cpp
    build               build translated module
    run                 run built and translated module
    test                run tests
```

The historical behaviour is provided by the `translate` subcommand, with the other commands except `analyze` requiring [cmake](https://cmake.org/) to work.

### analyze

The `analyze` command is intended to provided analysis and validation of a shedskin target without code-generation.

```
$ shedskin analyze --help
usage: shedskin analyze [-h] name

positional arguments:
  name        Python file or module to analyze

options:
  -h, --help  show this help message and exit
```

### translate

The shedskin translate command can be given the following options:

```
usage: shedskin translate [-h] [-a] [-d DEBUG] [-e] [-f] [-F FLAGS]
                          [-L [LIB ...]] [-l] [-m MAKEFILE] [-o OUTPUTDIR]
                          [-r] [-s] [-x] [--noassert] [-b] [--nogc]
                          [--nomakefile] [--nowrap]
                          name

positional arguments:
  name                  Python file or module to compile

options:
  -h, --help            show this help message and exit
  -a, --ann             Output annotated source code (.ss.py)
  -d DEBUG, --debug DEBUG
                        Set debug level
  -e, --extmod          Generate extension module
  -F FLAGS, --flags FLAGS
                        Provide alternate Makefile flags
  -L [LIB ...], --lib [LIB ...]
                        Add a library directory
  --int32               Use 32-bit integers
  --int64               Use 64-bit integers
  --int128              Use 128-bit integers
  --float32             Use 32-bit floats
  --float64             Use 64-bit floats
  -m MAKEFILE, --makefile MAKEFILE
                        Specify alternate Makefile name
  -o OUTPUTDIR, --outputdir OUTPUTDIR
                        Specify output directory for generated files
  -r, --random          Use fast random number generator (rand())
  -s, --silent          Silent mode, only show warnings
  -x, --traceback       Print traceback for uncaught exceptions
  --noassert            Disable assert statements
  -b, --nobounds        Disable bounds checking
  --nogc                Disable garbage collection
  --nomakefile          Disable makefile generation
  --nowrap              Disable wrap-around checking
```

For example, to compile the file `test.py` as an extension module, type

```bash
shedskin translate -e test
```

or

```bash
shedskin translate --extmod test
```

Using `-b` or `--nobounds` is also very common, as it disables out-of-bounds exceptions (`IndexError`), which can have a large impact on performance.

```python
a = [1, 2, 3]
print(a[5]) # invalid index: out of bounds
```

### build

The `build` command calls `shedskin translate` on a target via cmake, generates a suitable `CMakeLists.txt` file and then builds it, placing build artefacts in a `build` directory.

```
$ shedskin build --help
usage: shedskin build [-h] [--generator G] [--jobs N] [--build-type T] [--test] [--reset] [--conan]
                      [--spm] [--fetchcontent] [--ccache] [--target TARGET [TARGET ...]] [-a]
                      [-d DEBUG] [-e] [-f] [-F FLAGS] [-L [LIB ...]] [-l] [-m MAKEFILE]
                      [-o OUTPUTDIR] [-r] [-s] [-x] [--noassert] [--nobounds] [--nogc]
                      [--nomakefile] [--nowrap]
                      name

positional arguments:
  name                  Python file or module to compile

options:
  -h, --help            show this help message and exit
  --generator G         specify a cmake build system generator
  --jobs N              build and run in parallel using N jobs
  --build-type T        set cmake build type (default: 'Debug')
  --test                run ctest
  --reset               reset cmake build
  --conan               install cmake dependencies with conan
  --spm                 install cmake dependencies with spm
  --fetchcontent          install cmake dependencies with fetchcontent
  --ccache              enable ccache with cmake
  --target TARGET [TARGET ...]
                        build only specified cmake targets
  -a, --ann             Output annotated source code (.ss.py)
  -d DEBUG, --debug DEBUG
                        Set debug level
  -e, --extmod          Generate extension module
  -F FLAGS, --flags FLAGS
                        Provide alternate Makefile flags
  -L [LIB ...], --lib [LIB ...]
                        Add a library directory
  --int32               Use 32-bit integers
  --int64               Use 64-bit integers
  --int128              Use 128-bit integers
  --float32             Use 32-bit floats
  --float64             Use 64-bit floats
  -m MAKEFILE, --makefile MAKEFILE
                        Specify alternate Makefile name
  -o OUTPUTDIR, --outputdir OUTPUTDIR
                        Specify output directory for generated files
  -r, --random          Use fast random number generator (rand())
  -s, --silent          Silent mode, only show warnings
  -x, --traceback       Print traceback for uncaught exceptions
  --noassert            Disable assert statements
  --nobounds            Disable bounds checking
  --nogc                Disable garbage collection
  --nomakefile          Disable makefile generation
  --nowrap              Disable wrap-around checking
```

### run

The `run` command does everything the `build` command does and then runs the resultant executable.

```
$ shedskin run --help
usage: shedskin run [-h] [--generator G] [--jobs N] [--build-type T] [--test] [--reset] [--conan]
                    [--spm] [--fetchcontent] [--ccache] [--target TARGET [TARGET ...]] [-a] [-d DEBUG]
                    [-e] [-f] [-F FLAGS] [-L [LIB ...]] [-l] [-m MAKEFILE] [-o OUTPUTDIR] [-r] [-s]
                    [-x] [--noassert] [--nobounds] [--nogc] [--nomakefile] [--nowrap]
                    name

positional arguments:
  name                  Python file or module to run

options:
  -h, --help            show this help message and exit
  --generator G         specify a cmake build system generator
  --jobs N              build and run in parallel using N jobs
  --build-type T        set cmake build type (default: 'Debug')
  --test                run ctest
  --reset               reset cmake build
  --conan               install cmake dependencies with conan
  --spm                 install cmake dependencies with spm
  --fetchcontent          install cmake dependencies with fetchcontent
  --ccache              enable ccache with cmake
  --target TARGET [TARGET ...]
                        build only specified cmake targets
  -a, --ann             Output annotated source code (.ss.py)
  -d DEBUG, --debug DEBUG
                        Set debug level
  -e, --extmod          Generate extension module
  -F FLAGS, --flags FLAGS
                        Provide alternate Makefile flags
  -L [LIB ...], --lib [LIB ...]
                        Add a library directory
  --int32               Use 32-bit integers
  --int64               Use 64-bit integers
  --int128              Use 128-bit integers
  --float32             Use 32-bit floats
  --float64             Use 64-bit floats
  -m MAKEFILE, --makefile MAKEFILE
                        Specify alternate Makefile name
  -o OUTPUTDIR, --outputdir OUTPUTDIR
                        Specify output directory for generated files
  -r, --random          Use fast random number generator (rand())
  -s, --silent          Silent mode, only show warnings
  -x, --traceback       Print traceback for uncaught exceptions
  --noassert            Disable assert statements
  --nobounds            Disable bounds checking
  --nogc                Disable garbage collection
  --nomakefile          Disable makefile generation
  --nowrap              Disable wrap-around checking
```

### test

The `test` command provides builtin test discovery and running.

Basically `cd shedskin/tests` or `cd shedskin/examples` and then type the following:

```bash
shedskin test
```

command-line options are extensive:

```
$ shedskin test --help
usage: shedskin test [-h] [-e] [--dryrun] [--include PATTERN] [--check] [--modified] [--nocleanup]
                    [--pytest] [--run TEST] [--stoponfail] [--run-errs] [--progress] [--debug]
                    [--generator G] [--jobs N] [--build-type T] [--reset] [--conan] [--spm]
                    [--fetchcontent] [--ccache] [--target TARGET [TARGET ...]]

options:
  -h, --help            show this help message and exit
  -e, --extmod          Generate extension module
  --dryrun              dryrun without any changes
  --include PATTERN     provide regex of tests to include with cmake
  --check               check testfile py syntax before running
  --modified            run only recently modified test
  --nocleanup           do not cleanup built test
  --pytest              run pytest before each test run
  --run TEST            run single test
  --stoponfail          stop when first failure happens in ctest
  --run-errs            run error/warning message tests
  --progress            enable short progress output from ctest
  --debug               set cmake debug on
  --generator G         specify a cmake build system generator
  --jobs N              build and run in parallel using N jobs
  --build-type T        set cmake build type (default: 'Debug')
  --reset               reset cmake build
  --conan               install cmake dependencies with conan
  --spm                 install cmake dependencies with spm
  --fetchcontent          install cmake dependencies with fetchcontent
  --ccache              enable ccache with cmake
  --target TARGET [TARGET ...]
                        build only specified cmake targets
```

## Performance Tips and Tricks

### Performance Tips

* Small memory allocations (e.g. creating a new tuple, list or class instance..) typically do not slow down Python programs by much. However, after compilation to C++, they can quickly become a bottleneck. This is because for each allocation, memory has to be requested from the system, the memory has to be garbage-collected, and many memory allocations are further likely to cause cache misses. The key to getting very good performance is often to reduce the number of small allocations, for example by rewriting a small list comprehension by a for loop or by avoiding intermediate tuples in some calculation.
* But note that for the idiomatic `for a, b in enumerate(..)`, `for a, b in enumerate(..)` and `for a, b in somedict.iteritems()`, the intermediate small objects are optimized away, and that 1-length strings are cached.
* Several Python features (that may slow down generated code) are not always necessary, and can be turned off. See the section [Command-line options](#command-line-options) for details. Turning off bounds checking is usually a very safe optimization, and can help a lot for indexing-heavy code.
* Attribute access is faster in the generated code than indexing. For example, `v.x * v.y * v.z` is faster than `v[0] * v[1] * v[2]`.
* Shed Skin takes the flags it sends to the C++ compiler from the `FLAGS*` files in the Shed Skin installation directory. These flags can be modified, or overruled by creating a local file named `FLAGS`.
* When doing float-heavy calculations, it is not always necessary to follow exact IEEE floating-point specifications. Avoiding this by adding -ffast-math can sometimes greatly improve performance.
* Profile-guided optimization can help to squeeze out even more performance. For a recent version of GCC, first compile and run the generated code with `-fprofile-generate`, then with `-fprofile-use`.
* For best results, configure a recent version of the Boehm GC using `CPPFLAGS="-O3 -march=native" ./configure --enable-cplusplus --enable-threads=pthreads --enable-thread-local-alloc --enable-large-config --enable-parallel-mark`. The last option allows the GC to take advantage of having multiple cores.
* When optimizing, it is extremely useful to know exactly how much time is spent in each part of your program. The program [Gprof2Dot](https://github.com/jrfonseca/gprof2dot) can be used to generate beautiful graphs for a stand-alone program, as well as the original Python code. The program [OProfile](http://oprofile.sourceforge.net/news/) can be used to profile an extension module.

To use Gprof2dot, download `gprof2dot.py` from the website, and install Graphviz. Then:

```bash
shedskin translate program
make program_prof
./program_prof
gprof program_prof | gprof2dot.py | dot -Tpng -ooutput.png
```

To use OProfile, install it and use it as follows.

```bash
shedskin translate -e extmod
make
sudo opcontrol --start
python main_program_that_imports_extmod
sudo opcontrol --shutdown
opreport -l extmod.so
```

### Tricks

* The following two code fragments work the same, but only the second one is supported:

```python
statistics = {'nodes': 28, 'solutions': set()}

class statistics: pass
s = statistics(); s.nodes = 28; s.solutions = set()
```

* The evaluation order of arguments to a function or print changes with translation to C++, so it's better not to depend on this:

```python
print('hoei', raw_input()) # raw_input is called before printing 'hoei'!
```

* Tuples with different types of elements and length > 2 are currently not supported. It can however be useful to 'simulate' them:

```python
class mytuple:
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c
```

* Block comments surrounded by `#{` and `#}` are ignored by Shed Skin. This can be used to comment out code that cannot be compiled. For example, the following will only produce a plot when run using CPython:

```python
print("x =", x)
print("y =", y)
#{
import pylab as pl
pl.plot(x, y)
pl.show()
#}
```

## How to Help Out in Development

Open source projects thrive on feedback. Please send in bug reports, patches or other code, or suggestions about this document; or join the mailing list and start or participate in discussions. There is also [an "easytask" issue label](https://github.com/shedskin/shedskin/issues?q=is%3Aissue+is%3Aopen+label%3Aeasytask) for possible tasks to start out with.

If you are a student, you might want to consider applying for the yearly Google Summer of Code or GHOP projects. Shed Skin has so far successfully participated in one Summer of Code and one GHOP.
