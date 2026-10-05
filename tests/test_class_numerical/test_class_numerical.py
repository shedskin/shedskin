class Integer:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return '<Integer: %s>' % self.x

    def __gt__(self, other):
        return self.x > other.x

    def __gte__(self, other):
        return self.x >= other.x

    def __lt__(self, other):
        return self.x < other.x

    def __lte__(self, other):
        return self.x <= other.x


def maxi(a, b):
    if a > b:
        return a
    return b


def test_int_class():
    a = Integer(10)
    b = Integer(12)
    assert maxi(a, b) == b


class Float:
    def __init__(self, v):
        self.v = v

    def __add__(self, other):
        return Float(self.v + other.v)

    def __mul__(self, other):
        return Float(self.v * other.v)


def test_float_class():
    a = Float(1.0)
    b = Float(0.0)

    c = a + b
    assert c.v == 1.0

    d = a * b
    assert d.v == 0.0


class Num:
    def __init__(self, value):
        self.value = value

    def __add__(self, other):
        return Num(self.value + other.value)

    def __radd__(self, other):
        return Num(other + self.value)

    def __iand__(self, other):
        return Num(self.value + other.value)

    def __isub__(self, other):
        return Num(self.value - other.value)

    def __str__(self):
        return "Num(%s)" % self.value

    def __repr__(self):
        return str(self)


def test_num():
    numbers = [Num(3), Num(4), Num(5), Num(6)]
    assert sum(numbers).value == Num(18).value


class Vec2D:
    # from: https://zetcode.com/python/magicmethods

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return self.x * other.x + self.y * other.y

    def length(self):
        return pow(self.x ** 2 + self.y ** 2, 1/2)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '(%s, %s)' % (self.x, self.y)


def test_vector2d():
     u = Vec2D(0, 1)
     v = Vec2D(2, 3)
     w = Vec2D(-1, 1)
     assert u == u
     assert u != v

     a = u + v
     assert a == Vec2D(2, 4)
     assert a != w

     a = u - v
     assert a == Vec2D(-2, -2)

     b = u * v
     assert b == 3

     assert u.length() == 1.0


class Power:
    def __init__(self, x):
        self.x = x

    def __pow__(self, n):
        return Power(self.x ** n)


class PowerOf:
    def __init__(self, x):
        self.x = x

    def __pow__(self, other):
        return PowerOf(self.x ** other.x)


class PowBase:
    def __pow__(self, n):
        return n


class PowSub(PowBase):
    def __pow__(self, n):
        return n * 10


class PowFloat:
    def __pow__(self, e):
        return 2.5 * e


def test_pow():
    # a user-defined __pow__ (2-arg) used to fail to compile
    a = Power(3)
    assert (a ** 2).x == 9
    assert pow(a, 3).x == 27
    a **= 2
    assert a.x == 9
    assert (PowerOf(3) ** PowerOf(2)).x == 9
    assert [o ** 4 for o in [PowBase(), PowSub()]] == [4, 40]
    assert PowFloat() ** 2.0 == 5.0
    # builtin types are unaffected
    assert 2 ** 10 == 1024
    assert 2.0 ** 3 == 8.0


class V3:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __add__(self, o):
        return V3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):
        return V3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s):
        return V3(self.x * s, self.y * s, self.z * s)

    def dot(self, o):
        return self.x * o.x + self.y * o.y + self.z * o.z

    def normalize(self):  # mutates self
        n = self.dot(self) ** 0.5
        self.x, self.y, self.z = self.x / n, self.y / n, self.z / n
        return self

made = []

class Tracked:
    def __init__(self, v):
        self.v = v
        made.append(self)  # escapes, even when the caller drops it

last = None

def keep(v):
    global last
    last = v  # escapes through a global
    return v.x

def test_temporaries():
    # temporaries that the C++ compiler may elide must behave identically
    a, b = V3(1.0, 2.0, 3.0), V3(4.0, 5.0, 6.0)
    total = 0.0
    for i in range(1000):
        d = (a + b * i) - a  # only d.x etc. are used
        total += d.dot(V3(1.0, 0.0, 0.0)) + (a - b).normalize().x
    assert abs(total - (sum(4.0 * i for i in range(1000)) - 1000 / 3 ** 0.5)) < 1e-6
    # aliasing and identity
    c = a + b
    e = c
    e.normalize()
    assert c is e and c.x == e.x and abs(c.dot(c) - 1.0) < 1e-12
    assert (a + b) is not (a + b)
    # escaping through __init__ and through a global
    for i in range(10):
        Tracked(V3(i, i, i) * 2.0)
    assert [t.v.x for t in made] == [2.0 * i for i in range(10)]
    assert keep(V3(7.0, 8.0, 9.0) - V3(1.0, 1.0, 1.0)) == 6.0
    assert last.y == 7.0 and last.z == 8.0


def test_all():
    test_temporaries()
    test_int_class()
    test_float_class()
    test_vector2d()
    test_num()
    test_pow()


if __name__ == '__main__':
    test_all()
