# str.format (literal format strings only; rewritten into f-strings)

calls = []

def side(x):
    calls.append(x)
    return x


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.coords = [x, y]

    def __repr__(self):
        return 'Point(%d, %d)' % (self.x, self.y)

    def describe(self, label):
        return '{}: ({}, {}) {c}'.format(label, self.x, self.y, c=self.coords)


class Point3(Point):  # inherited method copy
    pass


def test_basic():
    assert '{} and {}'.format(1, 'two') == '1 and two'
    assert 'plain'.format() == 'plain'
    assert ''.format() == ''
    assert '{}'.format(None) == 'None'
    assert '{}{}'.format(True, 1.5) == 'True1.5'
    assert '{}'.format([1, 2]) == '[1, 2]'
    assert '{}'.format({'k': (1, 'a')}) == "{'k': (1, 'a')}"
    assert '{}'.format('{}') == '{}'


def test_braces():
    assert '{{}}'.format() == '{}'
    assert '{{{}}}'.format(7) == '{7}'
    assert '{{x}} {}'.format(1) == '{x} 1'


def test_numbering():
    assert '{1} {0} {1}'.format('a', 'b') == 'b a b'
    assert '{0}{0}{0}'.format('ab') == 'ababab'
    assert '{x}-{y}-{x}'.format(x=3, y=4.5) == '3-4.5-3'
    assert '{} {name}'.format(1, name='n') == '1 n'
    assert '{0} {name} {0}'.format(1, name='n') == '1 n 1'
    assert str.format('{}{x}', 1, x=2) == '12'


def test_conversions():
    assert '{!r} {!s}'.format('q', 'q') == "'q' q"
    assert '{0!r} {0}'.format(Point(1, 2)) == 'Point(1, 2) Point(1, 2)'
    assert '{!a}'.format('caf\u00e9') == "'caf\\xe9'"
    assert '{!r}'.format(None) == 'None'


def test_fields():
    p = Point(5, 6)
    assert '{0.x} {0.coords[1]} {0.y}'.format(p) == '5 6 6'
    assert '{[1]} {[0][1]}'.format((1, 2), [[3, 4]]) == '2 4'
    assert '{0[a]}'.format({'a': 1}) == '1'
    assert '{p.x}'.format(p=p) == '5'
    assert '{.y}'.format(p) == '6'


def test_evaluation():
    # each argument is evaluated once, in order, even if unused
    del calls[:]
    assert '{1} {0} {1}'.format(side(1), side(2)) == '2 1 2'
    assert calls == [1, 2]

    del calls[:]
    assert 'unused {}'.format(side(3), side(4)) == 'unused 3'
    assert calls == [3, 4]

    del calls[:]
    assert '{b}{a}'.format(a=side(5), b=side(6)) == '65'
    assert calls == [5, 6]

    x = 1
    assert '{} {}'.format(x, (x := 5)) == '1 5'
    assert x == 5

    # nested
    del calls[:]
    assert '[{}]'.format('<{}>'.format(side(7) * 2)) == '[<14>]'
    assert calls == [7]


def test_expressions():
    assert '{}-{}'.format(1, 2).upper().split('-') == ['1', '2']
    assert 'x{}y'.format(3) + 'z' == 'x3yz'
    assert len('{0}{0}'.format('abc')) == 6
    assert ['v{}'.format(i * i) for i in range(3)] == ['v0', 'v1', 'v4']
    assert [s for s in ['{}'.format(i) for i in range(3)] if s != '{}'.format(1)] == ['0', '2']
    assert (lambda z: '<{}>'.format(z + 1))(1) == '<2>'
    assert sorted(['b', 'a'], key=lambda s: '-{}'.format(s)) == ['a', 'b']


def gen(n):
    for i in range(n):
        yield '{}:{}'.format(i, side(i))


def default(a='{}!'.format(42)):
    return a


def test_contexts():
    assert list(gen(2)) == ['0:0', '1:1']
    assert default() == '42!'
    assert Point(1, 2).describe('p') == 'p: (1, 2) [1, 2]'
    assert Point3(3, 4).describe('q') == 'q: (3, 4) [3, 4]'


GLOBAL = '{}+{}'.format(1, side(2))


def test_global():
    assert GLOBAL == '1+2'


def test_all():
    test_basic()
    test_braces()
    test_numbering()
    test_conversions()
    test_fields()
    test_evaluation()
    test_expressions()
    test_contexts()
    test_global()


if __name__ == '__main__':
    test_all()
