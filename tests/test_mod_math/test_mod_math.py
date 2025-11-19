#based on the file: pypy/module/math/test/test_math.py
#from the pypy project

import math


def test_fsum():
    # detect evidence of double-rounding: fsum is not always correctly
    # rounded on machines that suffer from double rounding.
    # It is a known problem with IA32 floating-point arithmetic.
    # It should work fine e.g. with x86-64.
    x, y = 1e16, 2.9999  # use temporary values to defeat peephole optimizer

    test_values = [
        ([], 0.0),
        ([0.0], 0.0),
        # ([1e100, 1.0, -1e100, 1e-100, 1e50, -1.0, -1e50], 1e-100), # cpp: -1e+50 != 1e-100
        # ([2.0 ** 53, -0.5, -2.0 ** -54], 2.0 ** 53 - 1.0),
        # ([2.0 ** 53, 1.0, 2.0 ** -100], 2.0 ** 53 + 2.0),
        # ([2.0 ** 53 + 10.0, 1.0, 2.0 ** -100], 2.0 ** 53 + 12.0),
        # ([2.0 ** 53 - 4.0, 0.5, 2.0 ** -54], 2.0 ** 53 - 3.0),
        # ([1e16, 1., 1e-16], 10000000000000002.0),
        # ([1e16 - 2., 1. - 2. ** -53, -(1e16 - 2.), -(1. - 2. ** -53)], 0.0), # cpp: 1 != 0.0
        # exercise code for resizing partials array
    ]

    for i, (vals, expected) in enumerate(test_values):
        assert math.fsum(vals) == expected
        # print(math.fsum(vals), expected)


def test_pow():
    assert int(math.pow(2, 3)) == 8
    assert math.pow(2.0, 3.0) == 8.0
    assert math.pow(2, 3.0) == 8.0
    assert math.pow(2.0, 3) == 8.0
    assert math.pow(2, 3) == 8.0
    assert math.pow(1, 1000) == 1.0


def test_math():
    assert math.isinf(float("inf")) 
    assert math.isnan(float("nan"))
    assert '%.8f' % math.cosh(2)  == '3.76219569'
    assert '%.8f' % math.erf(2)   == '0.99532227'
    assert '%.8f' % math.erfc(2)  == '0.00467773'

    assert '%.8f' % math.expm1(2) == '6.38905610'
    assert int(100 * math.fma(2.7, 3.3, 1.1)) == 1001

    assert math.frexp(2) == (0.5, 2)
    assert math.gamma(2) == 1.0
    assert math.lgamma(2) == 0.0

    assert math.ldexp(float("inf"), -10 ** 20) == float("inf")

    assert math.factorial(0) == 1
    assert math.factorial(1) == 1
    assert math.factorial(2) == 2
    assert math.factorial(5) == 120

    assert -2 % 3 == 1
    assert -2.0 % 3 == 1.0
    assert 2 % 3 == 2
    assert math.fmod(-2.0, 3) == -2.0
    assert 4 % 3 == 1
    assert 4 % 3.0 == 1.0
    assert math.fmod(2.0, -3) == 2.0
    assert -2.0 % -3 == -2.0
    assert -2.0 % -3.0 == -2.0
    assert 2.0 % -3.0 == -1.0

    assert math.log(1/math.e) == -1
    assert math.log(math.e) == 1
    assert math.log(math.e**2) == 2
    assert '%.3f' % math.log(10) == '2.303'

    assert '%.8f' % (math.log1p(1 / math.e - 1) + 0.5) == '-0.50000000'
    assert math.log1p(0) == 0.0
    assert '%.8f' % (math.log1p(math.e - 1) + 0.5) == '1.50000000'
    assert '%.8f' % math.log1p(1) == '0.69314718'

    assert "%.8f" % math.cosh(2) == '3.76219569'

    assert '%.8f' % math.acosh(1) == '0.00000000'
    assert '%.8f' % math.acosh(2) == '1.31695790'
    assert math.isinf(math.asinh(float("inf")))

    assert '%.8f' % math.asinh(0) == '0.00000000'
    assert '%.8f' % math.asinh(1) == '0.88137359'
    assert '%.8f' % math.asinh(-1) == '-0.88137359'
    assert math.isinf(math.asinh(float("inf")))

    assert '%.8f' % math.atanh(0) == '0.00000000'
    assert '%.8f' % math.atanh(0.5) == '0.54930614'
    assert '%.8f' % math.atanh(-0.5) == '-0.54930614'
    assert math.isnan(math.atanh(float("nan")))

    assert math.trunc(1.9) == 1

    assert math.copysign(1.0, -2.0) == -1.0

    assert math.floor(1.5) == 1
    assert math.ceil(1.5) == 2

    assert math.e == 2.7182818284590451
    assert math.pi == 3.1415926535897931
    assert math.tau == 6.283185307179586

    assert math.inf == float('inf')
    math.nan # also in python this is not equal to float('nan')..

    assert '%.1f' % math.cbrt(27) == '3.0'
    assert '%.1f' % math.log2(256) == '8.0'
    assert '%.1f' % math.exp2(8.7) == '415.9'

    assert math.isfinite(0.0)
    assert math.isfinite(1.0)
    assert not math.isfinite(math.inf)
    assert not math.isfinite(math.nan)
    assert not math.isfinite(float('inf'))
    assert not math.isfinite(float('nan'))

    assert math.isqrt(18) == 4
    assert math.comb(17, 14) == 680

    assert math.gcd(2*2*3, 2*2*3*4, 2*3*5*7) == 2*3
    assert math.lcm(2*2*3, 2*2*3*4, 2*3*5*7, 2*2*3*4*5, 1681) == 1680*1681

    assert math.gcd(0, 0, 0) == 0
    assert math.lcm(0, 0, 0) == 0

    assert math.gcd(1, 0) == 1
    assert math.lcm(0, 1) == 0

    assert math.gcd(15) == 15
    assert math.lcm(14) == 14

    assert math.gcd() == 0
    assert math.lcm() == 1

    assert math.perm(0) == 1
    assert math.perm(0, 0) == 1

    assert math.perm(7) == 5040

    assert math.perm(7, 7) == 5040
    assert math.perm(7, 6) == 5040
    assert math.perm(7, 3) == 210


class Bert:
    def __init__(self, x):
        self.x = x

    def __mul__(self, b):
        return Bert(self.x * b.x)


def test_prod():
    assert math.prod([2,3,4]) == 24
    assert math.prod([2,3,4], start=2) == 48

    assert '%.2f' % (math.prod([2.1,3.1,4.1])) == '26.69'

    assert '%.2f' % (math.prod([2.2,3.1,4.4], start=2.2)) == '66.02'

    assert math.prod((Bert(3), Bert(4)), start=Bert(2)).x == 24

    assert math.prod([2,3,4], start=2.0) == 48.0
    assert '%.2f' %  (math.prod([2.1,3,4], start=2)) == '50.40'


def test_isclose():
    assert math.isclose(math.inf, math.inf)
    assert not math.isclose(math.nan, math.nan)
    assert math.isclose(7.0, 7.0)
    assert not math.isclose(7.0, 7.00000001)
    assert math.isclose(7.0, 7.000000001)


def test_dist():
    assert math.dist(iter([1.0, 3.0]), (4.0, 7.0)) == 5.0
    assert math.dist(iter([1, 3]), (4, 7)) == 5.0


def test_sumprod():
    assert math.sumprod([1,2],[3,4]) == 11
    assert math.sumprod([1,2.1],[3.3,4]) == 11.7


def test_all():
    test_fsum()
    test_pow()
    test_math()
    test_prod()
    test_isclose()
    test_dist()
    test_sumprod()


if __name__ == '__main__':
    test_all()

