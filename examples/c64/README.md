# c64

```bash
cd c64
shedskin build -e c64
cp build/c64.so .
cd ..
python c64_main.py --tape=intkarat.t64
load
run
```

requires adding `-fbracket-depth=512` to `CCFLAGS` in the `Makefile` in macOS

ref: https://github.com/ndless-nspire/Ndless/issues/59

requires `pyobject` see: https://pygobject.readthedocs.io
