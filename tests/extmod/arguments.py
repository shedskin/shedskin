# argument checking of exported functions, methods and constructors: see
# arguments_main.py

# functions

def nothing():
    return 0


def one(a):
    return a


def two(a, b):
    return a + b


def three(a, b, c):
    return a + b + c


def opt(a, b=2):
    return a * 10 + b


def opts(a=1, b=2):
    return a * 10 + b


def flag(a, b=False):
    if b:
        return -a
    return a


def unicode_name(größe, b=1):
    return größe + b


# classes

class Point:
    def __init__(self, x, y=0):
        self.x = x
        self.y = y

    def move(self, dx, dy=0):
        self.x += dx
        self.y += dy
        return self.x * 100 + self.y

    def norm1(self):
        return abs(self.x) + abs(self.y)

    def __repr__(self):
        return 'Point(%d, %d)' % (self.x, self.y)

    def __str__(self):
        return '(%d, %d)' % (self.x, self.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __abs__(self):
        return Point(abs(self.x), abs(self.y))

    def __call__(self, n):
        return self.x * n


class Point3(Point):  # inherits __init__
    def depth(self):
        return 3


class Empty:  # no __init__
    def value(self):
        return 7


class Steps:
    def __init__(self, n):
        self.i = 0
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.i == self.n:
            raise StopIteration
        self.i += 1
        return self.i


if __name__ == '__main__':
    # make sure everything is called with the types used from arguments_main.py
    nothing()
    one(1)
    two(1, 2)
    three(1, 2, 3)
    opt(1)
    opt(1, 3)
    opts()
    opts(3, 4)
    flag(1)
    flag(1, True)
    unicode_name(1)
    unicode_name(1, 2)
    p = Point(1, 2)
    Point(1)
    p.move(1)
    p.move(1, 2)
    p.norm1()
    repr(p)
    str(p)
    -p
    abs(p)
    p(3)
    q = Point3(1, 2)
    q.depth()
    q.move(1)
    Empty().value()
    for s in Steps(3):
        pass
