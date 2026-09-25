# Extension module tests

Each `name.py` here is compiled as an extension module, and tested by
running the accompanying `name_main.py` from CPython:

```
cd tests/extmod
shedskin build -e basics
python3 basics_main.py
```

`name_main.py` imports the compiled module from `build/` and checks that it
did not pick up `name.py` by accident. To check the tests themselves, run
them against the original Python module instead:

```
python3 basics_main.py --py
```

The `if __name__ == '__main__'` block in `name.py` must call everything that
`name_main.py` uses, with the same argument types, as only called (and
type-inferred) functions and methods are exported.
