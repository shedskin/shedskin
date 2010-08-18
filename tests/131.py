
# (c) Bearophile

from random import random
#from sets import Set

points = [ (random(), random()) for i in xrange(200) ]

def isntRightTurn(e):
    p0, p1 = e[-3]
    q0, q1 = e[-2]
    r0, r1 = e[-1]
    return q0*r1 + p0*q1 + r0*p1 >= q0*p1 + r0*q1 + p0*r1

def half(points):
    extrema = points[0:2]
    for p in points[2:]:
        extrema.append(p)
        while len(extrema)>2 and isntRightTurn(extrema):
            del extrema[-2]
    return extrema

points = sorted(set(points))
upper = half(points)
points.reverse()
lower = half(points)
print upper + lower[1:-1]

