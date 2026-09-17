#based on the file: pypy/module/math/test/test_math.py
#from the pypy project

import math
import math.integer


def test_fsum():
    # detect evidence of double-rounding: fsum is not always correctly
    # rounded on machines that suffer from double rounding.
    # It is a known problem with IA32 floating-point arithmetic.
    # It should work fine e.g. with x86-64.
    x, y = 1e16, 2.9999  # use temporary values to defeat peephole optimizer

    test_values = [
        ([], 0.0),
        ([0.0], 0.0),
        ([0.1] * 10, 1.0),
        ([0.1] * 100, 10.0),
        ([1e16, 1.0, -1e16, 1.0], 2.0),
        ([1e100, 1.0, -1e100, 1e-100, 1e50, -1.0, -1e50], 1e-100),
        ([1e16 - 2., 1. - 2. ** -53, -(1e16 - 2.), -(1. - 2. ** -53)], 0.0),
        # correctly-rounded final summation of the partials
        ([2.0 ** 53, -0.5, -2.0 ** -54], 2.0 ** 53 - 1.0),
        ([2.0 ** 53, 1.0, 2.0 ** -100], 2.0 ** 53 + 2.0),
        ([2.0 ** 53 + 10.0, 1.0, 2.0 ** -100], 2.0 ** 53 + 12.0),
        ([2.0 ** 53 - 4.0, 0.5, 2.0 ** -54], 2.0 ** 53 - 3.0),
        ([1e16, 1., 1e-16], 10000000000000002.0),
        # exercise code for resizing partials array
    ]

    for i, (vals, expected) in enumerate(test_values):
        assert math.fsum(vals) == expected
        # print(math.fsum(vals), expected)

    # non-finite values and intermediate overflow
    inf, nan = float('inf'), float('nan')
    assert math.fsum([inf, 1.0]) == inf
    assert math.fsum([1.0, -inf]) == -inf
    assert math.fsum([1e308, -1e308, inf]) == inf
    assert math.isnan(math.fsum([nan, 1.0]))
    assert math.isnan(math.fsum([inf, nan]))

    error = ''
    try:
        math.fsum([inf, -inf])
    except ValueError as e:
        error = str(e)
    assert error == '-inf + inf in fsum'

    error = ''
    try:
        math.fsum([1e308, 1e308, -1e308])
    except OverflowError as e:
        error = str(e)
    assert error == 'intermediate overflow in fsum'


def test_sqrt():
    assert math.sqrt(0.0) == 0.0
    assert math.sqrt(16) == 4.0

    error = ''
    try:
        math.sqrt(-1)
    except ValueError as e:
        error = str(e)
    assert error.startswith('expected a nonnegative input')


def test_pow():
    assert int(math.pow(2, 3)) == 8
    assert math.pow(2.0, 3.0) == 8.0
    assert math.pow(2, 3.0) == 8.0
    assert math.pow(2.0, 3) == 8.0
    assert math.pow(2, 3) == 8.0
    assert math.pow(1, 1000) == 1.0

    error = ''
    try:
        math.pow(-1, -0.5)
    except ValueError as e:
        error = str(e)
    assert error == 'math domain error'

    error = ''
    try:
        math.pow(0, -1)
    except ValueError as e:
        error = str(e)
    assert error == 'math domain error'

    # non-finite arguments follow C99 Annex F, as in CPython
    inf, nan = float('inf'), float('nan')
    assert math.pow(0.0, -inf) == inf
    assert math.pow(-inf, 0.5) == inf
    assert math.pow(-inf, -3.0) == -0.0
    assert math.pow(-1.0, inf) == 1.0
    assert math.pow(nan, 0.0) == 1.0
    assert math.isnan(math.pow(-2.0, nan))
    assert math.pow(1e-300, 2.0) == 0.0

    error = ''
    try:
        math.pow(10.0, 400.0)
    except OverflowError as e:
        error = str(e)
    assert error == 'math range error'


def test_errors():
    inf, nan = float('inf'), float('nan')

    # domain errors, with the argument in the message (python 3.14+)
    error = ''
    try:
        math.acos(2.0)
    except ValueError as e:
        error = str(e)
    assert error == 'expected a number in range from -1 up to 1, got 2.0'

    error = ''
    try:
        math.asin(-inf)
    except ValueError as e:
        error = str(e)
    assert error == 'expected a number in range from -1 up to 1, got -inf'

    error = ''
    try:
        math.acosh(0.5)
    except ValueError as e:
        error = str(e)
    assert error == 'expected argument value not less than 1, got 0.5'

    error = ''
    try:
        math.atanh(1.0)
    except ValueError as e:
        error = str(e)
    assert error == 'expected a number between -1 and 1, got 1.0'

    error = ''
    try:
        math.cos(inf)
    except ValueError as e:
        error = str(e)
    assert error == 'expected a finite input, got inf'

    error = ''
    try:
        math.sin(-inf)
    except ValueError as e:
        error = str(e)
    assert error == 'expected a finite input, got -inf'

    error = ''
    try:
        math.tan(inf)
    except ValueError as e:
        error = str(e)
    assert error == 'expected a finite input, got inf'

    error = ''
    try:
        math.log1p(-1.0)
    except ValueError as e:
        error = str(e)
    assert error == 'expected argument value > -1, got -1.0'

    for x in [0.0, -1.0, -inf]:
        error = ''
        try:
            math.log(x)
        except ValueError as e:
            error = str(e)
        assert error.startswith('expected a positive input, got ')

        error = ''
        try:
            math.log2(x)
        except ValueError as e:
            error = str(e)
        assert error.startswith('expected a positive input, got ')

        error = ''
        try:
            math.log10(x)
        except ValueError as e:
            error = str(e)
        assert error.startswith('expected a positive input, got ')

    assert math.isnan(math.log(nan))
    assert math.isnan(math.acos(nan))
    assert math.isnan(math.sin(nan))

    # log with a base
    assert math.log(8.0, 2.0) == 3.0
    assert math.log(2.0, 0.5) == -1.0

    error = ''
    try:
        math.log(2.0, 1.0)
    except ZeroDivisionError as e:
        error = str(e)
    assert error == 'division by zero'

    error = ''
    try:
        math.log(2.0, -2.0)
    except ValueError as e:
        error = str(e)
    assert error == 'expected a positive input, got -2.0'

    # gamma/lgamma poles
    for x in [0.0, -1.0, -1000.0]:
        error = ''
        try:
            math.gamma(x)
        except ValueError as e:
            error = str(e)
        assert error.startswith('expected a noninteger or positive integer, got ')

        error = ''
        try:
            math.lgamma(x)
        except ValueError as e:
            error = str(e)
        assert error.startswith('expected a noninteger or positive integer, got ')

    error = ''
    try:
        math.gamma(-inf)
    except ValueError as e:
        error = str(e)
    assert error == 'expected a noninteger or positive integer, got -inf'
    assert math.lgamma(-inf) == inf
    assert math.gamma(inf) == inf

    # range errors
    for x in [1000.0, 3e307]:
        error = ''
        try:
            math.exp(x)
        except OverflowError as e:
            error = str(e)
        assert error == 'math range error'

        error = ''
        try:
            math.expm1(x)
        except OverflowError as e:
            error = str(e)
        assert error == 'math range error'

        error = ''
        try:
            math.cosh(x)
        except OverflowError as e:
            error = str(e)
        assert error == 'math range error'

        error = ''
        try:
            math.sinh(x)
        except OverflowError as e:
            error = str(e)
        assert error == 'math range error'

        error = ''
        try:
            math.gamma(x)
        except OverflowError as e:
            error = str(e)
        assert error == 'math range error'


    error = ''
    try:
        math.exp2(3e307)
    except OverflowError as e:
        error = str(e)
    assert error == 'math range error'

    assert math.exp(-1000.0) == 0.0
    assert math.exp(inf) == inf

    # fmod
    assert math.fmod(1.0, inf) == 1.0
    for x, y in [(inf, 1.0), (1.0, 0.0), (inf, inf)]:
        error = ''
        try:
            math.fmod(x, y)
        except ValueError as e:
            error = str(e)
        assert error == 'math domain error'
    assert math.isnan(math.fmod(nan, 0.0))

    # fma
    error = ''
    try:
        math.fma(inf, 0.0, 1.0)
    except ValueError as e:
        error = str(e)
    assert error == 'invalid operation in fma'

    error = ''
    try:
        math.fma(1e308, 10.0, 0.0)
    except OverflowError as e:
        error = str(e)
    assert error == 'overflow in fma'
    assert math.isnan(math.fma(inf, 0.0, nan))

    # ldexp must not truncate the exponent
    assert math.ldexp(1e-320, 1070) == 126.5
    assert math.ldexp(1.0, -5000) == 0.0
    assert math.ldexp(1.0, -2**32 + 1) == 0.0
    assert math.ldexp(-1.0, -2**40) == -0.0
    assert math.ldexp(0.0, 2**40) == 0.0
    for exp in [1024, 2**32 + 1]:
        error = ''
        try:
            math.ldexp(1.0, exp)
        except OverflowError as e:
            error = str(e)
        assert error == 'math range error'

    # float to int conversion
    error = ''
    try:
        math.floor(inf)
    except OverflowError as e:
        error = str(e)
    assert error == 'cannot convert float infinity to integer'

    error = ''
    try:
        math.ceil(-inf)
    except OverflowError as e:
        error = str(e)
    assert error == 'cannot convert float infinity to integer'

    error = ''
    try:
        math.trunc(nan)
    except ValueError as e:
        error = str(e)
    assert error == 'cannot convert float NaN to integer'

    # isclose
    error = ''
    try:
        math.isclose(1.0, 1.0, rel_tol=-1.0)
    except ValueError as e:
        error = str(e)
    assert error == 'tolerances must be non-negative'

    error = ''
    try:
        math.isclose(1.0, 1.0, abs_tol=-1.0)
    except ValueError as e:
        error = str(e)
    assert error == 'tolerances must be non-negative'


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

    # floor()/ceil() must return int, not float
    assert str(math.floor(1.5)) == '1'
    assert str(math.ceil(1.5)) == '2'

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

    # no spurious intermediate overflow
    assert math.comb(100, 98) == 4950
    assert math.comb(62, 31) == 465428353255261088
    assert math.comb(3, 5) == 0
    assert math.comb(10, 0) == 1
    assert math.comb(0, 0) == 1

    error = ''
    try:
        math.comb(-1, 2)
    except ValueError as e:
        error = str(e)
    assert error == 'n must be a non-negative integer'

    error = ''
    try:
        math.comb(2, -1)
    except ValueError as e:
        error = str(e)
    assert error == 'k must be a non-negative integer'

    # floor/ceil/trunc of ints are exact (no roundtrip via float)
    assert math.floor(2**53 + 1) == 2**53 + 1
    assert math.ceil(2**53 + 1) == 2**53 + 1
    assert math.trunc(-2**53 - 1) == -2**53 - 1

    assert math.gcd(2*2*3, 2*2*3*4, 2*3*5*7) == 2*3
    assert math.lcm(2*2*3, 2*2*3*4, 2*3*5*7, 2*2*3*4*5, 1681) == 1680*1681

    assert math.gcd(0, 0, 0) == 0
    assert math.lcm(0, 0, 0) == 0

    assert math.gcd(1, 0) == 1
    assert math.lcm(0, 1) == 0

    assert math.gcd(15) == 15
    assert math.lcm(14) == 14

    assert math.gcd(-15) == 15
    assert math.lcm(-14) == 14

    assert math.gcd() == 0
    assert math.lcm() == 1

    assert math.hypot() == 0.0
    assert math.hypot(3.0) == 3.0
    assert math.hypot(-3.0) == 3.0
    assert math.hypot(3.0, 4.0) == 5.0
    assert math.hypot(3.0, 4.0, 12.0) == 13.0
    assert math.hypot(1.0, 2.0, 3.0, 4.0) == math.sqrt(30.0)

    assert math.perm(0) == 1
    assert math.perm(0, 0) == 1

    assert math.perm(7) == 5040

    assert math.perm(7, 7) == 5040
    assert math.perm(7, 6) == 5040
    assert math.perm(7, 3) == 210

    assert math.perm(3, 5) == 0

    error = ''
    try:
        math.perm(-1, 2)
    except ValueError as e:
        error = str(e)
    assert error == 'n must be a non-negative integer'

    error = ''
    try:
        math.perm(5, -2)
    except ValueError as e:
        error = str(e)
    assert error == 'k must be a non-negative integer'

    assert math.isqrt(0) == 0
    assert math.isqrt(1) == 1
    assert math.isqrt(99) == 9
    assert math.isqrt(100) == 10
    assert math.isqrt(999999999) == 31622
    assert math.isqrt(46340 * 46340) == 46340
    assert math.isqrt(46340 * 46340 + 1) == 46340
    assert math.isqrt(46340 * 46340 - 1) == 46339


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

    # no overflow/underflow of the intermediate squares
    assert math.dist([1e200], [-1e200]) == 2e200
    assert math.dist([1e200, 0.0], [0.0, 1e200]) == 1.414213562373095e+200
    assert math.isnan(math.dist([float('inf')], [float('inf')]))


def test_sumprod():
    assert math.sumprod([1,2],[3,4]) == 11
    assert math.sumprod([1,2.1],[3.3,4]) == 11.7


def test_math_integer():
    assert math.integer.perm(7) == 5040
    assert math.integer.perm(7, 7) == 5040
    assert math.integer.perm(7, 6) == 5040
    assert math.integer.perm(7, 3) == 210

    assert math.integer.comb(17, 14) == 680
    assert math.integer.comb(100, 98) == 4950

    assert math.integer.gcd(1, 0) == 1
    assert math.integer.lcm(0, 1) == 0

    assert math.integer.gcd(15) == 15
    assert math.integer.lcm(14) == 14

    assert math.integer.gcd(-15) == 15
    assert math.integer.lcm(-14) == 14

    assert math.integer.factorial(2) == 2
    assert math.integer.factorial(5) == 120

    assert math.integer.isqrt(18) == 4
    assert math.integer.isqrt(46340 * 46340) == 46340

    assert math.integer.perm(3, 5) == 0

    error = ''
    try:
        math.integer.perm(-1, 2)
    except ValueError as e:
        error = str(e)
    assert error == 'n must be a non-negative integer'

    error = ''
    try:
        math.integer.perm(5, -2)
    except ValueError as e:
        error = str(e)
    assert error == 'k must be a non-negative integer'


def test_fmax_fmin():
    # Standard comparisons
    assert math.fmax(10.5, 20.5) == 20.5
    assert math.fmax(-1.0, -2.0) == -1.0
    assert math.fmin(10.5, 20.5) == 10.5
    assert math.fmin(-1.0, -2.0) == -2.0

    # Handling NaN (fmax/fmin return the non-NaN value if one is NaN)
    nan = float('nan')
    assert math.fmax(5.0, nan) == 5.0
    assert math.fmin(5.0, nan) == 5.0

    # Both NaN should return NaN (nan != nan, so we check with isnan)
    assert math.isnan(math.fmax(nan, nan))
    assert math.isnan(math.fmin(nan, nan))


def test_classification():
    # Normal numbers
    assert math.isnormal(1.0) == True
    assert math.isnormal(-123.456) == True

    # Non-normal numbers (Zero, Inf, NaN)
    assert math.isnormal(0.0) == False
    assert math.isnormal(float('inf')) == False
    assert math.isnormal(float('nan')) == False

    # Subnormal numbers
    # Smallest normal double is ~2.22e-308
    sub = 1e-308 / 100.0
    assert math.issubnormal(sub) == True
    assert math.isnormal(sub) == False

    # Zero is NOT subnormal
    assert math.issubnormal(0.0) == False


def test_signbit():
    assert math.signbit(-1.0) == True
    assert math.signbit(1.0) == False
    assert math.signbit(0.0) == False
    assert math.signbit(math.copysign(0.0, -1.0)) == True
    assert math.signbit(float('inf')) == False
    assert math.signbit(float('-inf')) == True
    assert math.signbit(float('nan')) == False
    assert math.signbit(math.copysign(float('nan'), -1.0)) == True


def test_nextafter():
    assert math.nextafter(1.0, 1.0) == 1.0
    assert math.nextafter(0.0, math.inf) > 0.0
    assert math.nextafter(0.0, -math.inf) < 0.0
    assert math.nextafter(0.0, math.inf) == -math.nextafter(0.0, -math.inf)
    assert math.nextafter(math.inf, 0.0) < math.inf
    assert math.nextafter(-math.inf, 0.0) > -math.inf
    assert math.isnan(math.nextafter(math.nan, 1.0))
    assert math.nextafter(1.0, math.inf) > 1.0
    assert math.nextafter(1.0, -math.inf) < 1.0


def test_nextafter_steps():
    # steps=1 is the default, steps=0 leaves x alone
    assert math.nextafter(1.0, 2.0, steps=1) == math.nextafter(1.0, 2.0)
    assert math.nextafter(1.0, 2.0, steps=0) == 1.0
    assert math.nextafter(1.0, 1.0, steps=7) == 1.0

    # n steps up/down is n ulps away, in both directions
    assert math.nextafter(1.0, math.inf, steps=3) - 1.0 == 3.0 * math.ulp(1.0)
    assert 1.0 - math.nextafter(1.0, -math.inf, steps=2) == 2.0 * math.ulp(math.nextafter(1.0, -math.inf))

    # repeated single steps give the same answer
    stepped = 1.0
    for _ in range(4):
        stepped = math.nextafter(stepped, 2.0)
    assert math.nextafter(1.0, 2.0, steps=4) == stepped

    # more steps than there are floats in between: saturate at y
    close = math.nextafter(1.0, 2.0)
    assert math.nextafter(1.0, close, steps=100) == close
    assert math.nextafter(1.0, 1.0, steps=100) == 1.0

    # stepping across zero
    assert math.nextafter(0.0, -1.0, steps=2) < 0.0
    assert math.nextafter(0.0, 1.0, steps=2) > 0.0
    assert math.nextafter(math.nextafter(0.0, -1.0), 1.0, steps=2) > 0.0
    assert math.nextafter(0.0, 1.0, steps=1) == -math.nextafter(0.0, -1.0, steps=1)

    # nans propagate, as without steps
    assert math.isnan(math.nextafter(math.nan, 1.0, steps=3))
    assert math.isnan(math.nextafter(1.0, math.nan, steps=3))
    assert math.isnan(math.nextafter(math.nan, 1.0, steps=0))

    error = ''
    try:
        math.nextafter(1.0, 2.0, steps=-1)
    except ValueError as e:
        error = str(e)
    assert error.startswith('steps must be a non-negative integer')


def test_ulp():
    assert math.ulp(1.0) > 0.0
    assert math.ulp(-1.0) == math.ulp(1.0)
    assert math.ulp(0.0) > 0.0
    assert math.ulp(math.inf) == math.inf
    assert math.isnan(math.ulp(math.nan))
    assert math.nextafter(1.0, math.inf) - 1.0 == math.ulp(1.0)

    # the largest finite float: ulp should be the gap to the previous float
    largest = math.nextafter(math.inf, 0.0)
    prev = math.nextafter(largest, -math.inf)
    assert math.ulp(largest) == largest - prev


def test_modf():
    assert math.modf(1.5) == (0.5, 1.0)
    assert math.modf(-1.5) == (-0.5, -1.0)
    assert math.modf(0.0) == (0.0, 0.0)

    # values whose integer part overflows a 64-bit int must not wrap/UB
    a, b = math.modf(1e20)
    assert a == 0.0
    assert b == 1e20

    c, d = math.modf(-1e20)
    assert c == -0.0
    assert d == -1e20

    e, f = math.modf(float("inf"))
    assert e == 0.0
    assert math.isinf(f) and f > 0

    g, h = math.modf(float("-inf"))
    assert g == -0.0
    assert math.isinf(h) and h < 0

    i, j = math.modf(float("nan"))
    assert math.isnan(i)
    assert math.isnan(j)


def test_remainder():
    assert math.remainder(5.0, 3.0) == -1.0
    assert math.remainder(4.0, 2.0) == 0.0
    assert math.remainder(-4.0, 2.0) == 0.0
    assert math.remainder(1.0, math.inf) == 1.0
    assert math.remainder(-1.0, math.inf) == -1.0
    assert math.isnan(math.remainder(math.nan, 1.0))
    assert math.isnan(math.remainder(1.0, math.nan))

    error = ''
    try:
        math.remainder(1.0, 0.0)
    except ValueError as e:
        error = str(e)
    assert error == 'math domain error'

    error = ''
    try:
        math.remainder(math.inf, 1.0)
    except ValueError as e:
        error = str(e)
    assert error == 'math domain error'

    error = ''
    try:
        math.remainder(math.inf, math.inf)
    except ValueError as e:
        error = str(e)
    assert error == 'math domain error'


def test_atan2():
    assert '%.8f' % math.atan2(1.0, 1.0) == '0.78539816'
    assert '%.8f' % math.atan2(0.0, -1.0) == '3.14159265'
    assert '%.8f' % math.atan2(-1.0, 0.0) == '-1.57079633'


def test_degrees_radians():
    assert '%.8f' % math.degrees(math.pi) == '180.00000000'
    assert '%.8f' % math.degrees(math.pi / 2) == '90.00000000'
    assert '%.8f' % math.radians(180.0) == '3.14159265'
    assert '%.8f' % math.radians(90.0) == '1.57079633'


def test_fabs():
    assert math.fabs(-5.5) == 5.5
    assert math.fabs(5.5) == 5.5
    assert math.fabs(0.0) == 0.0


def test_hypot():
    assert math.hypot(3.0, 4.0) == 5.0

    # no overflow/underflow of the intermediate squares
    assert math.hypot(1e200, 1e200) == 1.414213562373095e+200
    assert math.hypot(1e-200, 1e-200) == 1.414213562373095e-200
    assert math.hypot(3.0 * 2.0 ** 700, 4.0 * 2.0 ** 700) == 5.0 * 2.0 ** 700
    assert math.hypot(1e-320, 1e-320) == 1.414e-320

    # inf wins over nan
    inf, nan = float('inf'), float('nan')
    assert math.hypot(inf, nan) == inf
    assert math.hypot(nan, -inf) == inf
    assert math.isnan(math.hypot(nan, 1.0))


def test_log10():
    assert math.log10(100.0) == 2.0
    assert math.log10(1.0) == 0.0
    assert math.log10(1000.0) == 3.0


def test_atan():
    assert math.atan(0.0) == 0.0
    assert '%.8f' % math.atan(1.0) == '0.78539816'
    assert '%.8f' % math.atan(-1.0) == '-0.78539816'
    assert '%.8f' % math.atan(0.5) == '0.46364761'
    assert '%.8f' % math.atan(10.0) == '1.47112767'
    assert math.atan(1.0) == math.pi / 4

    # int argument
    assert math.atan(1) == math.atan(1.0)

    # saturates at +-pi/2 for infinite input
    assert math.atan(math.inf) == math.pi / 2
    assert math.atan(-math.inf) == -math.pi / 2
    assert math.isnan(math.atan(math.nan))

    # sign of zero is preserved
    assert math.copysign(1.0, math.atan(-0.0)) == -1.0

    # atan is odd
    assert math.atan(-2.5) == -math.atan(2.5)


def test_tanh():
    assert math.tanh(0.0) == 0.0
    assert '%.8f' % math.tanh(1.0) == '0.76159416'
    assert '%.8f' % math.tanh(-1.0) == '-0.76159416'
    assert '%.8f' % math.tanh(0.5) == '0.46211716'
    assert '%.8f' % math.tanh(2.0) == '0.96402758'

    # int argument
    assert math.tanh(1) == math.tanh(1.0)

    # saturates at +-1
    assert math.tanh(math.inf) == 1.0
    assert math.tanh(-math.inf) == -1.0
    assert math.tanh(1000.0) == 1.0
    assert math.tanh(-1000.0) == -1.0
    assert math.isnan(math.tanh(math.nan))

    # sign of zero is preserved
    assert math.copysign(1.0, math.tanh(-0.0)) == -1.0

    # tanh is odd, and bounded by (-1, 1)
    assert math.tanh(-0.75) == -math.tanh(0.75)
    assert -1.0 < math.tanh(-5.0) < math.tanh(5.0) < 1.0


def test_all():
    test_fsum()
    test_pow()
    test_errors()
    test_sqrt()
    test_math()
    test_prod()
    test_isclose()
    test_dist()
    test_sumprod()
    test_modf()
    test_math_integer()
    test_fmax_fmin()
    test_classification()
    test_signbit()
    test_nextafter()
    test_nextafter_steps()
    test_ulp()
    test_remainder()
    test_atan2()
    test_degrees_radians()
    test_fabs()
    test_hypot()
    test_log10()
    test_atan()
    test_tanh()


if __name__ == '__main__':
    test_all()

