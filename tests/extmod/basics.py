# extension module under test: compile with 'shedskin build -e basics',
# then run basics_main.py (see README.md)

# globals
answer = 42
greeting = 'hello'


# functions
def add(a, b):
    return a + b


def scale(x, factor=2.0):
    return x * factor


def join(words, sep):
    return sep.join(words)


def count(words):
    d = {}
    for w in words:
        d[w] = d.get(w, 0) + 1
    return d


def nothing():
    return None


def fail(n):
    if n < 0:
        raise ValueError('negative')
    return n


# classes
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def length2(self):
        return self.x * self.x + self.y * self.y

    def __repr__(self):
        return 'Vector(%d, %d)' % (self.x, self.y)

    def __str__(self):
        return '(%d, %d)' % (self.x, self.y)

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector(self.x * other.x, self.y * other.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __abs__(self):
        return Vector(abs(self.x), abs(self.y))

    def __bool__(self):
        return self.x != 0 or self.y != 0

    def __hash__(self):
        return self.x * 1000 + self.y

    def __call__(self, n):
        return self.x * n


class Countdown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n


if __name__ == '__main__':
    # make sure everything is called with the types used from basics_main.py
    add(1, 2)
    scale(1.5)
    scale(1.5, 3.0)
    join(['a', 'b'], '-')
    count(['a', 'b', 'a'])
    nothing()
    fail(1)
    v = Vector(1, 2)
    v.length2()
    repr(v)
    str(v)
    v + v
    v - v
    v * v
    -v
    abs(v)
    bool(v)
    hash(v)
    v(3)
    for i in Countdown(3):
        pass
