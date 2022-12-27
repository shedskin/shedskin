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


def test_all():
    test_int_class()
    test_float_class()


if __name__ == '__main__':
    test_all()
