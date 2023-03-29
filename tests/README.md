# tests: shedskin testing folder

`tests` is a tests folder for shedskin which explicitly requires named tests.

It uses `cmake` for building and running tests.

## Objectives

- Collect standardized tests according to a consistent format to enable testing for both shedskin translation modes: translation to c++ executables and to python extension modules.

- Ensure that test names are meaningful for easier classification and grouping of similar or related tests.

- Reduce time to develop tests.

- Reduce test redundancy.

- Isolate non-implemented cases.

## Usage

This folder uses the shedskin `test` subcommand, which has extensive options to help setup, build and run its tests:

```bash
$ shedskin test --help
usage: shedskin test [-h] [-e] [-x] [--dryrun] [--include PATTERN] [--check]
                     [--modified] [--nocleanup] [--pytest] [--run TEST]
                     [--stoponfail] [--run-errs] [--progress] [--debug]
                     [--generator G] [--jobs N] [--build-type T] [--reset]
                     [--conan] [--spm] [--extproject] [--ccache]
                     [--target TARGET [TARGET ...]] [-c [CMAKE_OPT ...]]
                     [--nowarnings]

options:
  -h, --help            show this help message and exit
  -e, --extmod          Generate extension module
  -x, --executable      Generate executable
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
  --extproject          install cmake dependencies with externalproject
  --ccache              enable ccache with cmake
  --target TARGET [TARGET ...]
                        build only specified cmake targets
  -c [CMAKE_OPT ...], --cfg [CMAKE_OPT ...]
                        Add a cmake option '-D' prefix not needed
  --nowarnings          Disable '-Wall' compilation warnings
```

Shedskin uses CMake for testing: `shedskin` is only responsible for translation and `CMake` for everything else.


To build / run a **single** test using cmake:

```bash
shedksin test -r test_builtin_iter
```

To build and run **all** tests as executables using cmake on Linux and macOS:

```bash
shedksin test -x
```

To build and run **all** tests as executables using cmake on Windows requires the conan dependency manager to download dpendencies:

```bash
shedksin test --conan
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
shedksin test -xe
```

This will build/run an executable and python extension test for each test in the directory, basically the equivalent of the following (if it is run the first time):

```bash
mkdir build && cd build && cmake .. -DBUILD_EXECUTABLE=ON -DBUILD_EXTENSION=ON && cmake --build . && ctest
```

If it is run subsequently, it will run the equivalent of the following:

```bash
cd build && cmake .. -DBUILD_EXECUTABLE=ON -DBUILD_EXTENSION=ON && cmake --build . && ctest
```

To stop on the first failure:

```bash
shedksin test --stoponfail
```

To build / run the most recently modified test (here as exec only):

```bash
shedksin test -x --modified
```

To reset or remove the cmake `build` directory and run cmake:

```bash
shedksin test --reset -x
```


To build and run tests for error/warning messages:

```bash
shedskin test --run-errs
```

### Optimizing Building and Running Tests with Cmake

The cmake method has an option to build and run tests as parallel jobs. This can greatly speed up test runs.

You can specify the number of jobs to build and run tests in parallel:

```bash
shedksin test -xe -j 4
```

Another option is to use a different build system designed for speed like [Ninja](https://ninja-build.org) which automatically maximizes its use of available cores on your system.

If you have `Ninja` installed, you can have cmake use it as your underlying build system and automatically get improved performance vs the default Make-based system:

```bash
shedksin test -xe -gNinja
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

	```bash
	test_type_float.py
	test_type_int.py
	test_type_str.py
	...
	```


- Tests should be testable in python for correctness (e.g. by using `pytest` for example).

- Use grouped naming for selective testing based on name patterns. For example test all types: `test_type_*.py`

- Avoid turning a test in this folder into a benchmark test for speed. Adjust the scaling parameters to speed up a slow test since its purpose and inclusion in this folder is to check for correctness of implementation not to test for speed.

- Avoid using the `global` keyword for access to globals from functions: `pytest` does not work well with such constructs and will show errors. Several historical tests had to be rewritten to address this problem.


