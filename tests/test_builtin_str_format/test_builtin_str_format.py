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
    assert '{!s:5}'.format(5) == '5    '
    assert '{0!s:>12}'.format(Point(1, 2)) == ' Point(1, 2)'


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


def test_format_spec():
    assert '{:.2f}'.format(2.5) == '2.50'
    assert '{0:+08.3f} {0:.1f}'.format(-1.25) == '-001.250 -1.2'
    assert '{x:6.1f}|{y:F}'.format(x=3, y=float('-inf')) == '   3.0|-INF'
    assert '{0.x:.1f}'.format(Point(1, 2)) == '1.0'
    # same renderer as %-formatting
    for v in [0.5, -2.0, 1e10, 123.456]:
        assert '{:+012.3f}'.format(v) == '%+012.3f' % v
        assert '{:#.0f}'.format(v) == '%#.0f' % v
    # ints, bools and strs
    assert '{:5}|{:05d}|{:+}'.format(42, -42, 0) == '   42|-0042|+0'
    assert '{0:b} {0:#o} {0:#x} {0:X} {1:c}'.format(255, 97) == '11111111 0o377 0xff FF a'
    assert '{x:.1%} {y:4}|{y:d}'.format(x=1, y=True) == '100.0%    1|1'
    assert '{:6}|{:.2}|{:04s}'.format('ab', 'xyz', 'q') == 'ab    |xy|q000'
    assert '{0.y:#06x}'.format(Point(1, 26)) == '0x001a'
    assert '{:}|{:.3}|{:08}'.format(1.5, 100.0, -0.25) == '1.5|1e+02|-0000.25'
    for n in [0, 1, -1, 4096, -123456]:
        assert '{:+#012x}'.format(n) == '%+#012x' % n
    # fill, alignment, grouping, 'z' and 'n'
    assert '{:*^7}|{:<4}|{:=+6}|{:>3}'.format('ab', 1, -2, 'x') == '**ab***|1   |-    2|  x'
    assert '{0:,}|{0:_x}|{0:010,}|{1:z.1f}|{2:n}'.format(1234567, -0.01, 0.5) == '1,234,567|12_d687|01,234,567|0.0|0.5'
    assert '{x:#_b}|{x:0^9,.1f}'.format(x=1234) == '0b100_1101_0010|01,234.00'


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
    test_format_spec()


if __name__ == '__main__':
    test_all()
