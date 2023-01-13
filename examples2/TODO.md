# Remaining examples to be implemented in examples2 directory

## nested package-as-extension

Is a special case where the package is translated


### add_subdirectory(c64)

```bash
cd c64
python3 -m shedskin -be c64 && make && python3 -c "import c64; assert c64.__file__.endswith('.so')"
```

requires adding `-fbracket-depth=512` to `CCFLAGS` in the `Makefile`

ref: https://github.com/ndless-nspire/Ndless/issues/59

Compiles successfully with above changes but cannot run `c64_main.py` because cannot import `gi`

`pip install pygobject` fails on macos

conclusion: this is LINUX only.


### add_subdirectory(gs)

```bash
cd Gh0stenstein
python3 -m shedskin -bwe world_manager && make && python3 -c "import world_manager; assert world_manager.__file__.endswith('.so')"
```

Compiles successfully with above changes but cannot run `gs_main.py` because cannot import `gi`

`pip install pygobject` fails on macos

conclusion: this is LINUX only.


### add_subdirectory(mastermind) # nested ext

```bash
cd mm
python3 -m shedskin -e mastermind && make && python3 -c "import mastermind; assert mastermind.__file__.endswith('.so')"
```

compilation and running works


### add_subdirectory(pylot) # nested unbounded ext

```bash
cd pylot
python3 -m shedskin -be SimpleGeometry && make && python3 -c "import SimpleGeometry; assert SimpleGeometry.__file__.endswith('.so')"
```

compile ok (requires `_tkinter`)

