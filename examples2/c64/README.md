# c64

```bash
cd c64
python3 -m shedskin -be c64 && make && python3 -c "import c64; assert c64.__file__.endswith('.so')"
```

requires adding `-fbracket-depth=512` to `CCFLAGS` in the `Makefile` in macOS

ref: https://github.com/ndless-nspire/Ndless/issues/59

Compiles successfully with above changes but cannot run `c64_main.py` because cannot import `gi`

requires `pyobject` see: https://pygobject.readthedocs.io

not working on Linux -> Segmentation fault (core dumped)


