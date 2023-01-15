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


# class Vec2D:
#     # from: https://zetcode.com/python/magicmethods

#     def __init__(self, x, y):

#         self.x = x
#         self.y = y

#     def __add__(self, other):
#         return Vec2D(self.x + other.x, self.y + other.y)

#     def __sub__(self, other):
#         return Vec2D(self.x - other.x, self.y - other.y)

#     def __mul__(self, other):
#         return self.x * other.x + self.y * other.y

#     # def __abs__(self):
#     #     return pow(self.x ** 2 + self.y ** 2, 1/2)

#     def __eq__(self, other):
#         return self.x == other.x and self.y == other.y

#     def __str__(self):
#         return '(%s, %s)' % (self.x, self.y)

#     def __ne__(self, other):
#         return not self.__eq__(other)  


# def test_vector2d():
#     u = Vec2D(0, 1)
#     v = Vec2D(2, 3)
#     w = Vec2D(-1, 1)

#     a = u + v
#     assert a == Vec2D(2, 4)
#     assert a != w

#     a = u - v
#     assert a == Vec2D(-2, -2)

#     a = u * v

#     # assert a == 3
#     # abs(u) == 1.0 ## mixing types
#     assert u != v

def test_all():
    test_int_class()
    test_float_class()
    # test_vector2d()
    test_num()


if __name__ == '__main__':
    test_all()
