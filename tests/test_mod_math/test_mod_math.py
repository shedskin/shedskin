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
    assert math.frexp(2) == (0.5, 2)
    assert math.gamma(2) == 1.0
    assert math.lgamma(2) == 0.0

    assert math.ldexp(float("inf"), -10 ** 20) == float("inf")

    assert math.factorial(0) == 1
    assert math.factorial(1) == 1
    assert math.factorial(2) == 2
    assert math.factorial(5) == 120
#    assert math.factorial(5.))

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
    assert "%g" % 3.0 == '3'

    assert "%g" % math.log(10) == '2.30259'
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


def test_all():
    test_fsum()
    test_pow()
    test_math()

if __name__ == '__main__':
    test_all()

