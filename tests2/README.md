# tests2: Alternative testing folder for named tests

This is an altnernative testing folder `tests2` for named tests. It was created to improve on the numbered tests in the current `tests` folder which are a bit difficult to follow and classify. 

The idea here is to keep two folders and eventually migrate the first to `tests2` style and finally end up with one `tests` folder.

## Usage

There's a `runtests.py` test runner to help run the tests. It has the following commmand line options

```bash
$ ./runtests.py --help
usage: runtests [-h] [-r] [-v] [-p] [-e]

runs shedskin tests

options:
  -h, --help      show this help message and exit
  -r, --recent    run only most recently modified test
  -v, --validate  validate each testfile before running
  -p, --pytest    run pytest before each test run
  -e, --exec      retain test executable
```

To run all tests:

```bash
./runtests.py
```

To run the most recently modified test (useful during test dev):

```bash
./runtests.py -r
```

## Standards

- Each test should be a python file named `test_<name>.py` and should include at least one test function with the typical `test_<name>()` naming convention.

- Group related tests together by subject and by file name using names which allow for similar things to be naturally grouped together. For example:

	```text
	test_type_float.py
	test_type_int.py
	test_type_str.py
	...
	```

- Test functions with the naming convention `test_<name>()` should not have any parameters.

- Each test function should include at least one `assert` to test a specific case.

- Call all relevant test functions in the `__name__ == '__main__'` section:

	```python
	if __name__ == '__main__':
		test_list_append()
		test_list_assign()
		# ...
	```


## Benefits

- This allows the tests to be tested in python for correctness (e.g. by using `pytest` for example) and external python tests to be quickly incorporated into the test suite.

- Grouped naming allows for selecting testing based on naming patterns. For example test all types: `test_type_*.py`



## Todo:

- [ ] investigate [ccache](https://ccache.dev) to speed up compilations

- [ ] convert more tests


