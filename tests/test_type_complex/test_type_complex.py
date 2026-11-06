

def test_complex():
    a = complex(1, 2)
    assert a.imag == 2.0
    assert a.real == 1.0

    c = complex(7.1, 4.7)
    # assert c == (7.1 + 4.7j)
    assert c.real == 7.1
    assert c.imag == 4.7

    d = complex(7)
    assert d.real
    assert d.imag == 0.0
    assert d.real == 7.0

    e = c + d
    assert e.real == 14.1
    assert e.imag == 4.7

    f = 1.2 + complex()
    assert f.real == 1.2
    assert f.imag == 0.0

    g = complex() + 1.3
    assert g.real == 1.3
    assert g.imag == 0.0

    c += complex(7, 1.0)
    assert c.real == 14.1
    assert c.imag == 5.7

    h = complex(7, 4) * complex(9, 5) * complex(7, 4)
    assert h.real == 17.0
    assert h.imag == 669.0

    assert h.conjugate().real == 17.0
    assert h.conjugate().imag == -669.0

    assert "%.8f" % abs(h) == '669.21595916'

    assert hash(h) == 669002024

    # non-integral parts should not be truncated
    assert hash(complex(1.5, 2)) != hash(complex(1, 2))
    assert hash(complex(1, 2.5)) != hash(complex(1, 2))
    assert hash(complex(-0.0, 0.0)) == hash(complex(0.0, -0.0))
    assert hash(complex(1e300, 0)) != hash(complex(float('inf'), 0))
    assert len(set([hash(complex(x * 0.01, y * 0.01)) for x in range(100) for y in range(100)])) > 9000
    dc = {}
    for x in range(100):
        for y in range(100):
            dc[complex(x * 0.01, y * 0.01)] = x
    assert len(dc) == 10000
    assert dc[complex(0.5, 0.25)] == 50

    assert +complex(1, -2) == complex(1, -2)
    assert -complex(1, -2) == complex(-1, 2)


def test_from_string():
    assert complex(" 2.4+0j") == complex(2.4)
    assert complex("2.4") == complex(2.4)
    assert complex(" .4j") == complex(0, .4)
    assert complex("1-j") == complex(1, -1)
    assert complex("-10-j") == complex(-10, -1)
    assert complex("+10.1+2.4j") == complex(10.1, 2.4)
    assert complex("+j") == complex(0, 1)
    assert complex("-j") == complex(0, -1)
    assert complex("j") == complex(0, 1)
    assert complex("0j") == complex(0, 0)

    # same grammar as CPython (1009-B7)
    assert complex("١+٢j") == complex(1, 2)
    assert complex(" 1j ") == complex(0, 1)
    assert complex(" ( 1+2j ) ") == complex(1, 2)
    assert complex("(j)") == complex(0, 1)
    assert complex("1+2J") == complex(1, 2)
    assert complex("-J") == complex(0, -1)
    assert complex("1e3J") == complex(0, 1000)
    assert complex("1_000") == complex(1000)
    assert complex("1e1_0j") == complex(0, 1e10)
    assert complex("+1-j") == complex(1, -1)
    assert complex("-1e-3-4.5e+2j") == complex(-0.001, -450)
    assert complex("1.e3j") == complex(0, 1000)
    assert str(complex("-inf+infj")) == "(-inf+infj)"
    assert str(complex("nanj")) == "nanj"
    assert repr(complex(1, -0.0)) == '(1-0j)'
    assert repr(complex(-0.0, 2)) == '(-0+2j)'
    assert repr(complex(0.0, -0.0)) == '-0j'
    assert repr(1.23456789+9.87654321j) == '(1.23456789+9.87654321j)'
    assert str(complex(1e16, 0.1)) == '(1e+16+0.1j)'
    for s in ["1 +2j", "1+ 2j", "0x10", "1+2j\x00", "\x1c1j", "1+2j)",
              "(1+2j", "()", "1+-2j", "1..j", "1j+2", "1 j", "1_+2j",
              "1__0j", "_1j", "+", "", " ", "1+2jj", "infinit"]:
        try:
            complex(s)
            assert False, s
        except ValueError:
            pass


class PI:
    def __complex__(self):
        return 3+4j

class PI2:
    def __float__(self):
        return 3.14

class PI3:
    def __index__(self):
        return 27


def test_from_class():
    assert complex(PI()) == 3+4j
    assert complex(PI2()) == complex(3.14, 0)
    assert complex(PI3()) == 27+0j


def test_from_number():
    assert complex.from_number(18) == 18+0j
    assert complex.from_number(18.8) == 18.8+0j
    assert complex.from_number(8+9j) == 8+9j

    assert complex.from_number(PI()) == 3+4j

    assert complex.from_number(PI2()) == complex(3.14, 0)
    assert complex.from_number(PI2()) == 3.14

    assert complex.from_number(PI3()) == 27+0j
    assert complex.from_number(PI3()) == 27


def test_attributes():
    c = 3 - 4j
    assert c.real == 3.0
    assert c.imag == -4.0
    assert c.conjugate() == 3 + 4j
    assert (c * c).real == -7.0
    assert [z.imag for z in [1j, 2 + 3j]] == [1.0, 3.0]


def test_keywords():
    # imag= alone must not be passed as the real part
    c = complex(imag=2.0)
    assert c.real == 0.0
    assert c.imag == 2.0
    assert complex(imag=3) == 3j
    assert complex(real=1.5) == 1.5
    assert complex(1.0, imag=4.0) == 1 + 4j


def test_precision():
    # abs uses hypot: no overflow/underflow of intermediate squares
    assert abs(complex(1e200, 1e200)) == 1.414213562373095e+200
    assert abs(complex(1e-200, 1e-200)) == 1.4142135623730951e-200
    assert abs(3 + 4j) == 5.0
    try:
        abs(complex(1.5e308, 1.5e308))
        assert False
    except OverflowError as e:
        assert str(e) == 'absolute value too large'

    # Smith's algorithm for division
    assert (1e200 + 1e200j) / (1e200 + 1e200j) == 1 + 0j
    assert (1e-200 + 1e-200j) / (1e-200 + 1e-200j) == 1 + 0j
    assert (1 + 2j) / (3 - 4j) == (-0.2 + 0.4j)
    assert (1 + 2j) / 2.0 == (0.5 + 1j)
    try:
        (1 + 2j) / 0j
        assert False
    except ZeroDivisionError:
        pass

    # integer exponents multiply instead of going through polar form
    assert repr((1j) ** 2) == '(-1+0j)'
    assert repr((1 + 1j) ** 2) == '2j'
    assert (1 + 1j) ** 3 == (-2 + 2j)
    assert (2 + 0j) ** 10 == (1024 + 0j)
    assert (1 + 1j) ** -2 == -0.5j
    assert (2j) ** 0 == (1 + 0j)
    assert (1 + 1j) ** 2.0 == 2j
    n = 3
    assert (1j) ** n == -1j
    # non-integer exponents still use polar form
    assert abs((1j) ** 0.5 - (0.7071067811865476 + 0.7071067811865475j)) < 1e-15

    # overflow raises, for both the integer and the polar path
    for base, exp in [(3 + 4j, 1000 + 0j), (1e200 + 0j, 2 + 0j), (3 + 4j, 1000.5 + 0j),
                      (2 + 0j, 2000 + 0j), (1e154 + 1e154j, 2 + 0j),
                      (1e-200 + 0j, -2.5 + 0j), (complex('inf'), 2.5 + 0j)]:
        try:
            base ** exp
            assert False
        except OverflowError as e:
            assert str(e) == 'complex exponentiation'
    try:
        (1e200 + 0j) ** 2
        assert False
    except OverflowError:
        pass
    try:
        (3 + 4j) ** 1000.5
        assert False
    except OverflowError:
        pass
    try:
        10 ** (400 + 0j)
        assert False
    except OverflowError as e:
        assert str(e) == 'complex exponentiation'
    try:
        pow(3 + 4j, 1000)
        assert False
    except OverflowError:
        pass
    x = 3 + 4j
    try:
        x **= 1000
        assert False
    except OverflowError:
        pass
    # nan or underflow is not an overflow
    assert repr(complex('inf') ** 2) == '(nan+nanj)'
    assert (2 + 0j) ** -2000 == 0
    assert (1e-300 + 0j) ** 1.5 == 0
    assert (1e300 + 1e300j) ** 1 == (1e300 + 1e300j)
    # negative integer exponent of a power that underflows to zero
    try:
        (1e-200 + 0j) ** -2
        assert False
    except ZeroDivisionError as e:
        assert str(e) == '0.0 to a negative or complex power'


def test_all():
    test_complex()
    test_precision()
    test_attributes()
    test_keywords()
    test_from_string()
    test_from_class()
    test_from_number()


if __name__ == "__main__":
    test_all()

