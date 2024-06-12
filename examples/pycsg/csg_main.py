import sys

from csg.core import CSG

d = CSG.sphere(radius=1.3, stacks=32, slices=32)
a = CSG.cube()
b = CSG.cylinder(radius=0.5, start=[0., -2., 0.], end=[0., 2., 0.], slices=32)
c = CSG.cylinder(radius=0.5, start=[-2., 0., 0.], end=[2., 0., 0.], slices=32)
e = CSG.cylinder(radius=0.5, start=[0., 0., -2.], end=[0., 0., 2.], slices=32)

#sys.setrecursionlimit(10000)

d.intersect(a).subtract(b).subtract(c).subtract(e).saveVTK('output.vtk')
