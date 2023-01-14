# Remaining examples to be implemented in examples2 directory

### c64

```bash
cd c64
python3 -m shedskin -be c64 && make && python3 -c "import c64; assert c64.__file__.endswith('.so')"
```

requires adding `-fbracket-depth=512` to `CCFLAGS` in the `Makefile` in macOS

ref: https://github.com/ndless-nspire/Ndless/issues/59

Compiles successfully with above changes but cannot run `c64_main.py` because cannot import `gi`

requires `pyobject` see: https://pygobject.readthedocs.io

not working on Linux -> Segmentation fault (core dumped)


### gs

```bash
cd Gh0stenstein
python3 -m shedskin -bwe world_manager && make && python3 -c "import world_manager; assert world_manager.__file__.endswith('.so')"
```

requires `pyobject` see: https://pygobject.readthedocs.io

compiles and working on Linux (untested on macOS)



### mastermind

```bash
cd mm
python3 -m shedskin -e mastermind && make && python3 -c "import mastermind; assert mastermind.__file__.endswith('.so')"
```

compilation and working on both macOS and Linux


### pylot

```bash
cd pylot
python3 -m shedskin -be SimpleGeometry && make && python3 -c "import SimpleGeometry; assert SimpleGeometry.__file__.endswith('.so')"
```

requires `sudo apt install python3-tk` and `pip install Pillow`

compiled and working on Linux (untested on macOS)

