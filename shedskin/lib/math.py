# Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE)

e = pi = tau = inf = nan = 1.0

def isfinite(x): return True
def isinf(x): return True
def isnan(x): return True

def degrees(x): return 1.0
def radians(x): return 1.0
def acos(x): return 1.0
def asin(x): return 1.0
def atan(x): return 1.0
def cos(x): return 1.0
def sin(x): return 1.0
def tan(x): return 1.0
def cosh(x): return 1.0
def sinh(x): return 1.0
def tanh(x): return 1.0
def acosh(x): return 1.0
def asinh(x): return 1.0
def atanh(x): return 1.0
def atan2(x, y): return 1.0

def copysign(x, y): return 1.0

def erf(x): return 1.0
def erfc(x): return 1.0

def expm1(x): return 1.0
def fma(x, y, z): return 1.0

def exp(x): return 1.0
def exp2(x): return 1.0
def frexp(x): return (1.0, 1)
def ldexp(x, y): return 1.0

def gamma(x): return 1.0
def lgamma(x): return 1.0

def log(x, base=1): return 1.0
def log1p(x): return 1.0
def log2(x): return 1.0
def log10(x): return 1.0

def trunc(x): return 1
def fsum(x): return 1.0

def sqrt(x): return 1.0
def cbrt(x): return 1.0
def isqrt(x): return 1

def fabs(x): return 1.0
def fmod(x, y): return 1.0
def modf(x): return (1.0, 1.0)

def factorial(x): return 1

def floor(x): return 1
def ceil(x): return 1

def pow(x, y): return 1.0
def hypot(x, y): return 1.0

def comb(n, k): return 1
def perm(n, k=None): return 1

def gcd(*args): return 1
def lcm(*args): return 1

def prod(iterable, start=1):
    elem = iter(iterable).__next__()
    elem.__mul__(elem)
    return elem

def dist(p, q):
    return 1.0

def sumprod(p, q):
    return iter(p).__next__()

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return True
