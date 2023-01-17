# tests: shedskin testing folder

`tests` is a tests folder for shedskin which explicitly requires named tests.

It contains two alternative ways to build and run its tests:

1. Builtin-method: using shedskin's generated `Makefile` per test.

2. CMake-method: using `cmake`, which has advantages for rapid test development.

## Objectives

- Collect standardized tests according to a consistent format to enable testing for both shedskin translation modes: translation to c++ executables and to python extension modules.

- Ensure that test names are meaningful for easier classification and grouping of similar or related tests.

- Reduce time to develop tests.

- Reduce test redundancy.

- Isolate non-implemented cases.

## Usage

This folder includes a commandline tool, `run.py`, with extensive options to help setup, build and run its tests:

```bash
$ ./run.py --help
usage: run [-h] [-c] [-e] [-g GENERATOR] [-i PATTERN] [-j N] [-k] [-m]
                [-n] [-p] [-r TEST] [-s] [-t TARGET [TARGET ...]] [-x]
                [--progress] [--reset]

runs shedskin tests

options:
  -h, --help            show this help message and exit
  -c, --cmake           run tests using cmake
  -e, --extension       include python extension tests
  -g GENERATOR, --generator GENERATOR
                        specify a cmake build system generator
  -i PATTERN, --include PATTERN
                        provide regex of tests to include with cmake
  -j N, --parallel N    build and run tests in parallel using N jobs
  -k, --check           check testfile py syntax before running
  -m, --modified        run only recently modified test
  -n, --nocleanup       do not cleanup built test
  -p, --pytest          run pytest before each test run
  -r TEST, --run TEST   run single test
  -s, --stoponfail      stop when first failure happens in ctest
  -t TARGET [TARGET ...], --target TARGET [TARGET ...]
                        build only specified targets
  -x, --run-errs        run error/warning message tests
  --progress            enable short progress output from ctest
  --reset               reset cmake build
```

There are currently two methods to run tests:

1. Builtin method: the translate-build-run cycle is all managed by `shedskin`.
2. CMake method: `shedskin` is only responsible for translation and `CMake` for everything else.

The second method is recommended if your platform is supported (linux, osx). Windows support is on the todo list.

### Builtin Method

To build and run a single test in cpp-executable mode:

```bash
./run -r test_<name>.py
```

To build and run a single test in python-extension mode:

```bash
./run -er test_<name>.py
```

To build and run all tests in cpp-executable mode:

```bash
./run.py
```

To build and run all tests in python-extension mode:

```bash
./run.py -e
```

To build and run the most recently modified test (useful during test dev):

```bash
./run.py -m
```

or

```bash
./run.py -me
```

To build and run tests for error/warning messages:

```bash
./run.py -x
```

### CMake Method

In `cmake` mode, the `run.py` script acts as a frontend to `cmake` tools:

To build / run a **single** test using cmake as an executable:

```bash
./run.py -c -r test_builtin_iter
```

To build / run a **single** test using cmake as a python extension:

```bash
./run.py -ce -r test_builtin_iter
```

To build and run **all** tests as executables using cmake:

```bash
./run.py -c
```

If the above command is run for the first time, it will run the equivalent of the following:

```bash
mkdir build && cd build && cmake .. && cmake --build . && ctest
```

If it is run subsequently, it will run the equivalent of the following:

```bash
cd build && cmake .. && cmake --build . && ctest
```

This is useful during test development and has the benefit of only picking up changes to modified tests and will not re-translate or re-compile unchanged tests.

To build and run **all** cmake tests as executables **and** python extensions using cmake:

```bash
./run.py -ce
```

This will build/run an executable and python extension test for each test in the directory, basically the equivalent of the following (if it is run the first time):

```bash
mkdir build && cd build && cmake .. -DTEST_EXT=ON && cmake --build . && ctest
```

If it is run subsequently, it will run the equivalent of the following:

```bash
cd build && cmake .. -DTEST_EXT=ON && cmake --build . && ctest
```

To stop on the first failure:

```bash
./run.py -ce -s
```

To build / run the most recently modified test (here as exec only):

```bash
./run.py -c -m
```

To reset or remove the cmake `build` directory and run cmake:

```bash
./run.py --reset -c
```

### Optimizing Test Runs with Cmake

The cmake method has an option to build and run tests as parallel jobs. This can greatly speed up test runs.

You can specify the number of jobs to build and run tests in parallel:

```bash
./run.py -ce -j 4
```

Another option is to use a different build system with system that is designed for speed like [Ninja](https://ninja-build.org) which automatically maximizes its use of available cores on your system.

If you have `Ninja` installed, you can have cmake use it your underlying build system and automatically get improved performance vs the default Make-based system:

```bash
./run.py -ce -gNinja
```


### Skipping Tests

- To skip a test just change the `test_` prefix of the file or folder to `skip_`

- Note that skipped tests may still be picked up by `pytest`, this is not a bad thing as every test in this folder active or otherwise should pass under `pytest`.


## Standards

An example of a hypothetical test file `test_calc.py` which is consistent with the standard:

```python
def test_add():
    assert 1+1 == 2

def test_subtract():
    assert 2-1 == 1

# ...

def test_all():
    test_add()
    test_subtract()

if __name__ == '__main__':
    test_all()
````

- Each test in the `tests2` folder should be a python file named `test_<name>.py` and should include at least one test function with the usual `test_<name>()` naming convention as a well as a `test_all()` function which only calls other `test_<name>()` functions and which itself should only be called in the `__name__ == '__main__'` section. 

- Each `test_<name>()` function should include at least one `assert` to test a specific case and should not take arguments or keyword parameters.

- Related tests should be grouped together by subject and should use file names which allow for tests to be naturally sorted and grouped together.

For example:

	```text
	test_type_float.py
	test_type_int.py
	test_type_str.py
	...
	```


- Tests should be testable in python for correctness (e.g. by using `pytest` for example).

- Use grouped naming for selective testing based on name patterns. For example test all types: `test_type_*.py`

- Avoid turning a test in this folder into a benchmark test for speed. Adjust the scaling parameters to speed up a slow test since its purpose and inclusion in this folder is to check for correctness of implementation not to test for speed.

- Avoid using the `global` keyword for access to globals from functions: `pytest` does not work well with such constructs and will show errors. Several historical tests had to be rewritten to address this problem.


## TODO:

- [ ] update `.travis.yml` file to reflect recent changes in testing mechanism
- [ ] improved cleanup for default method in cases of multiple local imports
- [ ] enabled windows platform support for cmake-based method and [conan](https://conan.io)
- [ ] auto-collect all non-working tests into a written log


