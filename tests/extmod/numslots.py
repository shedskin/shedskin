# extension module under test: compile with 'shedskin build -e numslots',
# then run numslots_main.py (see README.md)


class Mod:
    # a modulo is required: pow(a, n, m) only
    def __init__(self, x):
        self.x = x

    def __pow__(self, n, m):
        return Mod(pow(self.x, n, m))


class Pow:
    # no modulo: a ** n and pow(a, n) only
    def __init__(self, x):
        self.x = x

    def __pow__(self, n):
        return Pow(self.x ** n)


class ModDefault:
    # optional modulo: all three spellings
    def __init__(self, x):
        self.x = x

    def __pow__(self, n, m=1000):
        return ModDefault(pow(self.x, n, m))


class Num:
    # all binary and unary number slots (except __pow__, see above)
    def __init__(self, x):
        self.x = x

    def __add__(self, o):
        return Num(self.x + o.x)

    def __sub__(self, o):
        return Num(self.x - o.x)

    def __mul__(self, o):
        return Num(self.x * o.x)

    def __mod__(self, o):
        return Num(self.x % o.x)

    def __divmod__(self, o):
        return (Num(self.x // o.x), Num(self.x % o.x))

    def __lshift__(self, n):
        return Num(self.x << n)

    def __rshift__(self, n):
        return Num(self.x >> n)

    def __and__(self, o):
        return Num(self.x & o.x)

    def __xor__(self, o):
        return Num(self.x ^ o.x)

    def __or__(self, o):
        return Num(self.x | o.x)

    def __floordiv__(self, o):
        return Num(self.x // o.x)

    def __truediv__(self, o):
        return self.x / o.x

    def __matmul__(self, o):
        return self.x * o.x + 1

    def __neg__(self):
        return Num(-self.x)

    def __pos__(self):
        return Num(self.x + 1)

    def __abs__(self):
        return Num(abs(self.x))

    def __invert__(self):
        return Num(~self.x)

    def __bool__(self):
        return self.x != 0

    def __int__(self):
        return self.x * 10

    def __float__(self):
        return self.x + 0.5

    def __index__(self):
        return self.x


class Index:
    # int() and float() fall back on __index__
    def __init__(self, x):
        self.x = x

    def __index__(self):
        return self.x


class IntFloat:
    # no __index__: not usable as an index
    def __init__(self, x):
        self.x = x

    def __int__(self):
        return self.x

    def __float__(self):
        return self.x * 1.5


class Acc:
    # in-place operators, that modify and return self
    def __init__(self, x):
        self.x = x

    def __iadd__(self, n):
        self.x += n
        return self

    def __isub__(self, n):
        self.x -= n
        return self

    def __imul__(self, n):
        self.x *= n
        return self

    def __imod__(self, n):
        self.x %= n
        return self

    def __ipow__(self, n):
        self.x **= n
        return self

    def __ilshift__(self, n):
        self.x <<= n
        return self

    def __irshift__(self, n):
        self.x >>= n
        return self

    def __iand__(self, n):
        self.x &= n
        return self

    def __ixor__(self, n):
        self.x ^= n
        return self

    def __ior__(self, n):
        self.x |= n
        return self

    def __ifloordiv__(self, n):
        self.x //= n
        return self

    def __itruediv__(self, n):
        self.x = self.x * 100 // n
        return self

    def __imatmul__(self, n):
        self.x = self.x * n + 1
        return self


if __name__ == '__main__':
    # make sure everything is called with the types used from numslots_main.py
    pow(Mod(3), 4, 5).x
    (Pow(3) ** 4).x
    pow(Pow(3), 4).x
    (ModDefault(3) ** 4).x
    pow(ModDefault(3), 4, 5).x

    a, b = Num(7), Num(3)
    (a + b).x
    (a - b).x
    (a * b).x
    (a % b).x
    q, r = divmod(a, b)
    q.x
    r.x
    (a << 2).x
    (a >> 1).x
    (a & b).x
    (a ^ b).x
    (a | b).x
    (a // b).x
    a / b
    a.__matmul__(b)
    (-a).x
    (+a).x
    abs(a).x
    (~a).x
    bool(a)
    int(a)
    float(a)
    a.__index__()
    n = Num(1)
    n += Num(2)  # generated __iadd__
    n.x
    i = Index(5)
    int(i)
    float(i)
    i.__index__()
    f = IntFloat(4)
    int(f)
    float(f)
    acc = Acc(5)
    acc += 3
    acc -= 1
    acc *= 4
    acc %= 10
    acc **= 3
    acc <<= 2
    acc >>= 1
    acc &= 0xff
    acc ^= 5
    acc |= 16
    acc //= 3
    acc /= 7
    acc.__imatmul__(2)
    acc.x
