# reading a @property is not method passing (method passing itself: 44.py)

class P:
    def __init__(self):
        self._x = 1

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, v):
        self._x = v

    def gety(self):
        return self._x + 1

    y = property(gety)

class Q(P):
    @property
    def x(self):
        return self._x * 10

class R(P):
    pass

p = P()
print(p.x, p.y)
p.x = 5
print(p.x, R().x, R().y, Q().y)
for o in [P(), Q()]:
    print(o.x)

#!method passing is not supported
