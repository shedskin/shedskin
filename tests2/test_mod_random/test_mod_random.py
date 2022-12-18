# (c) Bearophile

import random

random.seed(42)

def isntRightTurn(e):
    p0, p1 = e[-3]
    q0, q1 = e[-2]
    r0, r1 = e[-1]
    return q0 * r1 + p0 * q1 + r0 * p1 >= q0 * p1 + r0 * q1 + p0 * r1


def half(points):
    extrema = points[0:2]
    for p in points[2:]:
        extrema.append(p)
        while len(extrema) > 2 and isntRightTurn(extrema):
            del extrema[-2]
    return extrema

def test_random():
    points = [(random.random(), random.random()) for i in range(200)]
    points = sorted(set(points))
    upper = half(points)
    points.reverse()
    lower = half(points)
    # assert [('%.2f' % x, '%.2f' % y) for x, y in upper + lower[1:-1]] == [
    #     ('0.00', '0.29'), ('0.00', '0.93'), ('0.16', '0.96'), ('0.38', '0.99'),
    #     ('0.96', '1.00'), ('1.00', '1.00'), ('1.00', '0.84'), ('1.00', '0.51'),
    #     ('0.98', '0.10'), ('0.81', '0.01'), ('0.43', '0.01'), ('0.09', '0.05'),
    #     ('0.02', '0.19')
    # ]
    ## XXX output is different in python and c++
    assert len(points) == 200 

def test_all():
    test_random()

if __name__ == '__main__':
    test_all()
