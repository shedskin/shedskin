# tests2: alternative tests folder for named tests

`tests2` is an alternative tests folder for shedskin which explicitly requires named tests. It was created to improve on the numbered tests in the current `tests` folder which are a bit difficult to follow and classify.

It contains two alternative ways to build and run the tests:

1. Builtin-method: using shedskin's builtin generated `Makefile`
2. CMake-method: using `cmake`, which has advantages for rapid test development.

The idea here is to keep two test folders until all tests in the `tests` folder are eventually migrated to `tests2`. At that point `tests2` will become `tests`

## Usage

This folder includes a commandline tool, `runtests.py`, to help setup, build and run the tests.

It has the following commmand line options

```bash
$ ./runtests.py --help
usage: runtests [-h] [-r] [-v] [-p] [-e] [-c]

runs shedskin tests

options:
  -h, --help      show this help message and exit
  -r, --recent    run only most recently modified test
  -v, --validate  validate each testfile before running
  -p, --pytest    run pytest before each test run
  -e, --exec      retain test executable
  -c, --cmake     run tests using cmake
```

To build and run all tests using the default testrunner:

```bash
./runtests.py
```

To build and run the most recently modified test (useful during test dev) using the default testrunner:

```bash
./runtests.py -r
```

To build and run all tests using cmake:

```bash
./runtests.py -c
```

The above command will automatically create a `build` folder, and then `cd build`, `cmake ..`, `make`, and finally `make test`.

In development, make changes to the python tests as required and then:

```bash
cd build
make && make test
```

This has the benefit of only picking up changes to modified tests and will not re-translate or re-compile unchanged tests.


## Standards

- With the exception of `test_hello.py`, each test should be a python file named `test_<name>.py` and should include at least one test function with the cannonical `test_<name>()` naming convention.

- Related tests should be grouped together by subject and should use file names which allow for tests to be naturally grouped together.

For example:

	```text
	test_type_float.py
	test_type_int.py
	test_type_str.py
	...
	```

- Test functions with the naming convention `test_<name>()` should not have any parameters.

- Each test function should include at least one `assert` to test a specific case.

- All relevant test functions should be called in the `__name__ == '__main__'` section:

	```python

	def test_addition():
		assert 1+1 == 2

	if __name__ == '__main__':
		test_addition()
		# ...

	```


## Benefits

- This allows the tests to be tested in python for correctness (e.g. by using `pytest` for example) and external python tests to be quickly incorporated into the test suite.

- Grouped naming allows for selecting testing based on naming patterns. For example test all types: `test_type_*.py`



## Todo:

- [x] include cmake (ctest) testing
- [ ] convert more tests


