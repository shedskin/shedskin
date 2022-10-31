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
        ([1e100, 1.0, -1e100, 1e-100, 1e50, -1.0, -1e50], 1e-100),
        ([2.0 ** 53, -0.5, -2.0 ** -54], 2.0 ** 53 - 1.0),
        ([2.0 ** 53, 1.0, 2.0 ** -100], 2.0 ** 53 + 2.0),
        ([2.0 ** 53 + 10.0, 1.0, 2.0 ** -100], 2.0 ** 53 + 12.0),
        ([2.0 ** 53 - 4.0, 0.5, 2.0 ** -54], 2.0 ** 53 - 3.0),
        ([1e16, 1., 1e-16], 10000000000000002.0),
        ([1e16 - 2., 1. - 2. ** -53, -(1e16 - 2.), -(1. - 2. ** -53)], 0.0),
        # exercise code for resizing partials array
    ]

    for i, (vals, expected) in enumerate(test_values):
        print(math.fsum(vals), expected)


if __name__ == '__main__':
    #test_fsum()

    print(math.isinf(float("inf")))
    print(math.isnan(float("nan")))
    print(math.cosh(2))
    print(math.erf(2))
    print(math.erfc(2))
    print(math.expm1(2))
    print(math.frexp(2))
    print(math.gamma(2))
    print(math.lgamma(2))

    print(math.ldexp(float("inf"), -10 ** 20))

    print(math.factorial(0))
    print(math.factorial(1))
    print(math.factorial(2))
    print(math.factorial(5))
    print(math.factorial(5.))

    print(math.log1p(1 / math.e - 1) + 0.5)
    print(math.log1p(0))
    print(math.log1p(math.e - 1) + 0.5)
    print(math.log1p(1))

    print(math.acosh(1))
    print(math.acosh(2))
    print(math.isinf(math.asinh(float("inf"))))

    print(math.asinh(0))
    print(math.asinh(1))
    print(math.asinh(-1))
    print(math.isinf(math.asinh(float("inf"))))

    print(math.atanh(0))
    print(math.atanh(0.5))
    print(math.atanh(-0.5))
    print(math.isnan(math.atanh(float("nan"))))

    print(math.trunc(1.9))

    print(math.copysign(1.0, -2.0))
