# tests2: alternative shedskin tests folder for named tests

`tests2` is an alternative tests folder for shedskin which explicitly requires named tests.

It was created to improve on the current numbered tests in the `tests` folder (see objectives below).

It contains two alternative ways to build and run the tests:

1. Builtin-method: using shedskin's generated `Makefile` per test.

2. CMake-method: using `cmake`, which has advantages for rapid test development.

The plan is to keep two test folders until all tests in the `tests` folder are eventually migrated to `tests2`. At that point `tests2` will become `tests`.


## Objectives

-  Introduce standardized test formats to enable testing for both shedskin translation modes: translation to c++ executables and to python extension modules.

- Make test names more meaningful for easier classification and grouping of similar or related tests.

- Reducing time to develop tests.

- Reduce redundant tests.

- Isolate non-implemented cases.


## Usage

This folder includes a commandline tool, `runtests.py`, to help setup, build and run the tests.

It has the following commmand line options

```bash
$ ./runtests.py --help
usage: runtests [-h] [-c] [-f TEST] [-m] [-p] [-r] [-v] [-e] [-x]

runs shedskin tests

options:
  -h, --help           show this help message and exit
  -c, --cmake          run tests using cmake
  -f TEST, --fix TEST  fix test with imports
  -m, --modified       run only most recently modified test
  -p, --pytest         run pytest before each test run
  -r, --reset          reset cmake build
  -v, --validate       validate each testfile before running
  -e, --extensions     run only extension tests
  -x, --exec           retain test executable
```

There are currently two ways to run tests: (1) the builtin way and (2) the cmake way. The latter is recommended if your platform is supported (linux, osx). Windows support is on the todo list.

### Builtin Method

To build and run all tests using the default testrunner:

```bash
./runtests.py
```

To build and run the most recently modified test (useful during test dev) using the default testrunner:

```bash
./runtests.py -m
```

### Cmake Method

To build and run all tests as executables using cmake:

```bash
./runtests.py -c
```

If the above command is run for the first time, it will run the equivalent of the following:

```bash
mkdir build && cd build && cmake .. && make && make test
```

If it is run subsequently, it will run the equivalent of the following:

```bash
cd build && cmake .. && make && make test
```

This is useful during test development and has the benefit of only picking up changes to modified tests and will not re-translate or re-compile unchanged tests.

To reset (i.e. remove) the cmake `build` directory and run cmake:

```bash
./runtests.py -c -r
```


To build and run all tests as python extensions using cmake:

```bash
./runtests.py -ce
```

You should reset the build directory before running either mode (executable or extension)


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

- With the exception of `test_hello.py`, each test in the `tests2` folder should be a python file named `test_<name>.py` and should include at least one test function with the usual `test_<name>()` naming convention as a well as a `test_all()` function which only calls other `test_<name>()` functions and which itself should only be called in the `__name__ == '__main__'` section. 

- Each `test_<name>()` function should include at least one `assert` to test a specific case and should not have any parameters.

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


## Todo:

- [x] include cmake (ctest) testing
- [x] run all tests as either executables or python extensions
- [ ] enabled windows platform support for cmake-based method
- [ ] unify both shedskin compilation modes for tests such that both executables and python extensions are generated, built and run for reach test run.
- [ ] convert more tests


