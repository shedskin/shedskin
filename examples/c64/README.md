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
