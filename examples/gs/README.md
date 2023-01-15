# gs

```bash
cd Gh0stenstein
python3 -m shedskin -bwe world_manager && make && python3 -c "import world_manager; assert world_manager.__file__.endswith('.so')"
```

requires `pyobject` see: https://pygobject.readthedocs.io

compiles and working on Linux (untested on macOS)

