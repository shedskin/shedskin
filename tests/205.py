import math

#based on the file: pypy/module/math/test/test_math.py
#from the pypy project


if __name__ == '__main__':
    print math.isinf(float("inf"))
    print math.isnan(float("nan"))
    print math.cosh(2)
    print math.erf(2)
    print math.erfc(2)
    print math.expm1(2)
    print math.frexp(2)
    print math.gamma(2)
    print math.lgamma(2)

    print math.ldexp(float("inf"), -10 ** 20)

    print math.factorial(0)
    print math.factorial(1)
    print math.factorial(2)
    print math.factorial(5)
    print math.factorial(5.)

    print math.log1p(1 / math.e - 1) + 0.5
    print math.log1p(0)
    print math.log1p(math.e - 1) + 0.5
    print math.log1p(1)

    print math.acosh(1)
    print math.acosh(2)
    print math.isinf(math.asinh(float("inf")))

    print math.asinh(0)
    print math.asinh(1)
    print math.asinh(-1)
    print math.isinf(math.asinh(float("inf")))

    print math.atanh(0)
    print math.atanh(0.5)
    print math.atanh(-0.5)
    print math.isnan(math.atanh(float("nan")))

    print math.trunc(1.9)

    print math.copysign(1.0, -2.0)
