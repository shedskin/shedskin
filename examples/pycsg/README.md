# pycsg

```bash
cd csg
shedskin build -e geom
cp build/geom.so .
cd ..
python csg_main.py
paraview output.vtk
(press 'apply')
```
