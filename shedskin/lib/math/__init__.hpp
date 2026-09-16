/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __MATH_HPP
#define __MATH_HPP

#include "builtin.hpp"
#include <math.h>
#include <numeric>
#include <limits>
#include <cstdint>
#include <cstring>
#include <vector>

#include "integer.hpp"

using namespace __shedskin__;
namespace __math__ {

extern __ss_float pi;
extern __ss_float e;
extern __ss_float tau;
extern __ss_float inf;
extern __ss_float nan;

void __init();

/* CPython-style error handling (mirrors math_1 in mathmodule.c): a nan result
 * for a non-nan argument is a domain error, an infinite result for a finite
 * argument is either a range error (can_overflow) or a singularity. msg, if
 * given, is a prefix to which the offending argument is appended. */
[[noreturn]] void __math_domain_error(const char *msg, __ss_float x);
[[noreturn]] void __math_range_error();

inline __ss_float __math_1(__ss_float x, __ss_float r, bool can_overflow, const char *msg=nullptr) {
    if(std::isnan(r) && !std::isnan(x))
        __math_domain_error(msg, x);
    if(std::isinf(r) && std::isfinite(x)) {
        if(can_overflow)
            __math_range_error();
        __math_domain_error(msg, x);
    }
    return r;
}

inline __ss_int ceil(__ss_float x) {
    return __int(std::ceil(x));
}
inline __ss_int ceil(__ss_int x) {
    return x;
}

inline __ss_float fabs(__ss_float x) {
    return std::fabs(x);
}

inline __ss_int factorial(__ss_int x) {
    return __math__::__integer__::factorial(x);
}

inline __ss_int floor(__ss_float x) {
    return __int(std::floor(x));
}
inline __ss_int floor(__ss_int x) {
    return x;
}

inline __ss_float fmod(__ss_float x, __ss_float y) {
    if(std::isinf(y) && std::isfinite(x))
        return x;
    __ss_float r = std::fmod(x, y);
    if(std::isnan(r) && !std::isnan(x) && !std::isnan(y))
        __math_domain_error(nullptr, x);
    return r;
}

inline tuple2<__ss_float, __ss_float> *modf(__ss_float x) {
    __ss_float ipart;
    __ss_float fpart = std::modf(x, &ipart);
    return (new tuple2<__ss_float, __ss_float>(2, fpart, ipart));
}

inline __ss_float ldexp(__ss_float x, __ss_int i) {
    if(x == 0.0 || !std::isfinite(x))
        return x;
    /* don't truncate the exponent to int: that could wrap it around */
    if(i > (__ss_int)std::numeric_limits<int>::max())
        __math_range_error();
    if(i < (__ss_int)std::numeric_limits<int>::min())
        return std::copysign((__ss_float)0.0, x); /* underflow */
    __ss_float r = std::ldexp(x, (int)i);
    if(std::isinf(r))
        __math_range_error();
    return r;
}

inline __ss_float exp(__ss_float x) {
    return __math_1(x, std::exp(x), true);
}

inline __ss_float exp2(__ss_float x) {
    return __math_1(x, std::exp2(x), true);
}

#define __SS_MATH_LOG_MSG "expected a positive input, got "

inline __ss_float log(__ss_float x) {
    if(x <= 0)
        __math_domain_error(__SS_MATH_LOG_MSG, x);
    return std::log(x);
}

inline __ss_float log2(__ss_float x) {
    if(x <= 0)
        __math_domain_error(__SS_MATH_LOG_MSG, x);
    return std::log2(x);
}

inline __ss_float log(__ss_float x, __ss_float base) {
    __ss_float num = log(x);
    __ss_float den = log(base);
    if(den == 0.0)
        throw new ZeroDivisionError(new str("division by zero"));
    return num / den;
}

inline __ss_float log10(__ss_float x) {
    if(x <= 0)
        __math_domain_error(__SS_MATH_LOG_MSG, x);
    return std::log10(x);
}

inline __ss_float sqrt(__ss_float x) {
    if(x < 0.0)
        throw new ValueError(__add_strs(2, new str("expected a nonnegative input, got "), __str(x)));
    return std::sqrt(x);
}

inline __ss_float cbrt(__ss_float x) {
    return std::cbrt(x);
}

inline __ss_int isqrt(__ss_float x) {
    return (__ss_int)(floor(std::sqrt(x))); // TODO optimize?
}

inline __ss_int isqrt(__ss_int n) {
    return __math__::__integer__::isqrt(n);
}

#define __SS_MATH_ARC_MSG "expected a number in range from -1 up to 1, got "

inline __ss_float acos(__ss_float x) {
    return __math_1(x, std::acos(x), false, __SS_MATH_ARC_MSG);
}

inline __ss_float asin(__ss_float x) {
    return __math_1(x, std::asin(x), false, __SS_MATH_ARC_MSG);
}

inline __ss_float atan(__ss_float x) {
    return std::atan(x);
}

inline __ss_float atan2(__ss_float x, __ss_float y) {
    return std::atan2(x, y);
}

#define __SS_MATH_FINITE_MSG "expected a finite input, got "

inline __ss_float cos(__ss_float x) {
    return __math_1(x, std::cos(x), false, __SS_MATH_FINITE_MSG);
}

/* euclidean norm of n non-negative values (the absolute coordinates).
 * scaling by a power of two is exact, so this gives the same result as the
 * naive formula, except that intermediate squares cannot overflow/underflow. */
inline __ss_float __vector_norm(const __ss_float *v, size_t n) {
    __ss_float max = 0.0;
    bool found_nan = false;
    for(size_t i = 0; i < n; i++) {
        if(std::isnan(v[i]))
            found_nan = true;
        else if(v[i] > max)
            max = v[i];
    }
    if(std::isinf(max))
        return max; /* inf wins over nan, as in CPython */
    if(found_nan)
        return std::numeric_limits<__ss_float>::quiet_NaN();
    if(max == 0.0 || n == 1)
        return max;
    int max_e;
    std::frexp(max, &max_e);
    __ss_float sumsq = 0.0;
    for(size_t i = 0; i < n; i++) {
        __ss_float s = std::ldexp(v[i], -max_e);
        sumsq += s*s;
    }
    return std::ldexp(std::sqrt(sumsq), max_e);
}

template<class ... Args> __ss_float hypot(int, __ss_float x, Args ... args) {
    const __ss_float v[] = {std::fabs(x), std::fabs((__ss_float)args)...};
    return __vector_norm(v, 1 + sizeof...(args));
}
inline __ss_float hypot(int, __ss_float x) {
    return x < 0 ? -x : x;
}
inline __ss_float hypot(int) {
    return 0.0;
}

inline __ss_float sin(__ss_float x) {
    return __math_1(x, std::sin(x), false, __SS_MATH_FINITE_MSG);
}

inline __ss_float tan(__ss_float x) {
    return __math_1(x, std::tan(x), false, __SS_MATH_FINITE_MSG);
}

inline __ss_float degrees(__ss_float x) {
    return x*(180.0/pi);
}

inline __ss_float radians(__ss_float x) {
    return x/(180.0/pi);
}

inline __ss_float cosh(__ss_float x) {
    return __math_1(x, std::cosh(x), true);
}

inline __ss_float sinh(__ss_float x) {
    return __math_1(x, std::sinh(x), true);
}

inline __ss_float tanh(__ss_float x) {
    return std::tanh(x);
}

inline __ss_float pow(__ss_float x, __ss_float y) {
    /* C99/IEEE pow already gives CPython's results for non-finite arguments
     * (e.g. pow(0.0, -inf) == inf, pow(-inf, 0.5) == inf, pow(-2.0, nan) == nan) */
    __ss_float r = std::pow(x, y);
    if(!std::isfinite(r) && std::isfinite(x) && std::isfinite(y)) {
        if(std::isnan(r) || x == 0.0) /* negative**fraction, 0**negative */
            __math_domain_error(nullptr, x);
        __math_range_error();
    }
    return r;
}

inline __ss_bool isfinite(__ss_float x) {
    return __mbool(std::isfinite(x));
}

inline __ss_bool isinf(__ss_float x) {
    return __mbool(std::isinf(x));
}

inline __ss_bool isnan(__ss_float x) {
    return __mbool(std::isnan(x));
}

inline __ss_bool signbit(__ss_float x) {
    return __mbool(std::signbit(x));
}

inline __ss_float acosh(__ss_float x) {
    return __math_1(x, ::acosh(x), false, "expected argument value not less than 1, got ");
}

inline __ss_float asinh(__ss_float x) {
    return ::asinh(x);
}

inline __ss_float atanh(__ss_float x) {
    return __math_1(x, ::atanh(x), false, "expected a number between -1 and 1, got ");
}

inline __ss_float copysign(__ss_float x, __ss_float y) {
    return ::copysign(x, y);
}

inline __ss_float erf(__ss_float x) {
    return ::erf(x);
}

inline __ss_float erfc(__ss_float x) {
    return ::erfc(x);
}

inline __ss_float expm1(__ss_float x) {
    return __math_1(x, ::expm1(x), true);
}

inline __ss_float fma(__ss_float x, __ss_float y, __ss_float z) {
    __ss_float r = ::fma(x, y, z);
    if(!std::isfinite(r)) {
        if(std::isnan(r)) {
            if(!std::isnan(x) && !std::isnan(y) && !std::isnan(z))
                throw new ValueError(new str("invalid operation in fma"));
        } else if(std::isfinite(x) && std::isfinite(y) && std::isfinite(z))
            throw new OverflowError(new str("overflow in fma"));
    }
    return r;
}

inline tuple2<__ss_float, __ss_int> *frexp(__ss_float x) {
    int n;
    __ss_float mantisa = std::frexp(x, &n);

    return (new tuple2<__ss_float, __ss_int>(2, mantisa, n));
}

#define __SS_MATH_GAMMA_MSG "expected a noninteger or positive integer, got "

inline __ss_float gamma(__ss_float x) {
    /* poles at non-positive integers (including -0.0), and -inf */
    if((std::isfinite(x) && x <= 0.0 && std::floor(x) == x) || (std::isinf(x) && x < 0.0))
        __math_domain_error(__SS_MATH_GAMMA_MSG, x);
    return __math_1(x, ::tgamma(x), true, __SS_MATH_GAMMA_MSG);
}

inline __ss_float lgamma(__ss_float x) {
    if(std::isfinite(x) && x <= 0.0 && std::floor(x) == x)
        __math_domain_error(__SS_MATH_GAMMA_MSG, x);
    return __math_1(x, ::lgamma(x), true, __SS_MATH_GAMMA_MSG);
}

inline __ss_float log1p(__ss_float x) {
    return __math_1(x, ::log1p(x), false, "expected argument value > -1, got ");
}

inline __ss_int trunc(__ss_float x) {
    return __int(::trunc(x));
}
inline __ss_int trunc(__ss_int x) {
    return x;
}

inline __ss_int comb(__ss_int n, __ss_int k) {
    return __math__::__integer__::comb(n, k);
}

/* shewchuk's algorithm with a correctly rounded final summation, as in CPython */
inline __ss_float fsum(pyiter<__ss_float> *iterable) {
    std::vector<__ss_float> p; /* partials, increasing magnitude */
    __ss_float x, y, hi, yr, lo = 0.0;
    __ss_float special_sum = 0.0, inf_sum = 0.0;

    __ss_int __2;
    pyiter<__ss_float> *__1;
    pyiter<__ss_float>::for_in_loop __3;

    FOR_IN(x,iterable,1,2,3)
        __ss_float xsave = x;
        size_t i = 0;
        for(size_t j = 0; j < p.size(); j++) {
            y = p[j];
            if(std::fabs(x) < std::fabs(y))
                std::swap(x, y);
            hi = x + y;
            yr = hi - x;
            lo = y - yr;
            if(lo != 0.0)
                p[i++] = lo;
            x = hi;
        }
        p.resize(i);
        if(x != 0.0) {
            if(!std::isfinite(x)) {
                /* a nonfinite x could arise either from an infinite or nan
                   input, or from an intermediate overflow */
                if(std::isfinite(xsave))
                    throw new OverflowError(new str("intermediate overflow in fsum"));
                if(std::isinf(xsave))
                    inf_sum += xsave;
                special_sum += xsave;
                p.clear();
            }
            else
                p.push_back(x);
        }
    END_FOR

    if(special_sum != 0.0) {
        if(std::isnan(inf_sum))
            throw new ValueError(new str("-inf + inf in fsum"));
        return special_sum;
    }

    size_t n = p.size();
    hi = 0.0;
    if(n > 0) {
        hi = p[--n];
        /* sum from the top, stopping as soon as the sum is inexact */
        while(n > 0) {
            x = hi;
            y = p[--n];
            hi = x + y;
            yr = hi - x;
            lo = y - yr;
            if(lo != 0.0)
                break;
        }
        /* make half-even rounding work across multiple partials */
        if(n > 0 && ((lo < 0.0 && p[n-1] < 0.0) || (lo > 0.0 && p[n-1] > 0.0))) {
            y = lo + lo;
            x = hi + y;
            yr = x - hi;
            if(y == yr)
                hi = x;
        }
    }
    return hi;
}

template<class ... Args> __ss_int gcd(int, __ss_int x, Args ... args) {
    return ((x = std::gcd(x, args)), ...);
}
inline __ss_int gcd(int, __ss_int x) {
    return x < 0 ? -x : x;
}
inline __ss_int gcd(int) {
    return 0;
}

template<class ... Args> __ss_int lcm(int, __ss_int x, Args ... args) {
    return ((x = std::lcm(x, args)), ...);
}
inline __ss_int lcm(int, __ss_int x) {
    return x < 0 ? -x : x;
}
inline __ss_int lcm(int) {
    return 1;
}

inline __ss_int perm(__ss_int n, __ss_int k) {
    return __math__::__integer__::perm(n, k);
}
inline __ss_int perm(__ss_int n) {
    return __math__::__integer__::perm(n);
}

template<class T> inline T __mul(T a, T b) { return a->__mul__(b); }
#ifdef __SS_LONG
template<> inline __ss_int __mul(__ss_int a, __ss_int b) { return a*b; }
#endif
template<> inline int __mul(int a, int b) { return a*b; }
template<> inline __ss_float __mul(__ss_float a, __ss_float b) { return a*b; }
// TODO complex?

template<class A> A prod(pyiter<A> *iterable, A start) {
    __ss_int __2;
    pyiter<A> *__1;
    typename pyiter<A>::for_in_loop __3;
    A x;
    A result = start;

    FOR_IN(x,iterable,1,2,3)
        result = __mul(result, x);
    END_FOR

    return result;
}

inline __ss_float prod(pyiter<__ss_float> *iterable) {
    return prod(iterable, (__ss_float)1.0);
}

inline __ss_int prod(pyiter<__ss_int> *iterable) {
    return prod(iterable, (__ss_int)1);
}

inline __ss_float prod(pyiter<__ss_float> *iterable, __ss_int start) {
    return prod(iterable, (__ss_float)start);
}

inline __ss_float prod(pyiter<__ss_int> *iterable, __ss_float start) {
    return (__ss_float)prod(iterable) * start;
}

template<class A> __ss_float dist(pyiter<A> *p, pyiter<A> *q) {
    __iter<A> *p_iter = p->__iter__();
    __iter<A> *q_iter = q->__iter__();

    A a, b;
    std::vector<__ss_float> diffs;
    size_t n_exhausted;

    for(;;) {
        n_exhausted = 0;

        try  {
            a = p_iter->__next__();
        } catch (StopIteration *) {
            n_exhausted += 1;
        }
        try  {
            b = q_iter->__next__();
        } catch (StopIteration *) {
            n_exhausted += 1;
        }
        if(n_exhausted == 2)
            break;
        else if (n_exhausted > 0)
            throw new ValueError(new str("both points must have the same number of dimensions"));

        diffs.push_back(std::fabs((__ss_float)a - (__ss_float)b));
    }

    return __vector_norm(diffs.data(), diffs.size());
}

template<class A> A sumprod(pyiter<A> *p, pyiter<A> *q) {
    __iter<A> *p_iter = p->__iter__();
    __iter<A> *q_iter = q->__iter__();

    A a, b;
    A sum = 0;
    size_t n_exhausted;

    for(;;) {
        n_exhausted = 0;

        try  {
            a = p_iter->__next__();
        } catch (StopIteration *) {
            n_exhausted += 1;
        }
        try  {
            b = q_iter->__next__();
        } catch (StopIteration *) {
            n_exhausted += 1;
        }
        if(n_exhausted == 2)
            break;
        else if (n_exhausted > 0)
            throw new ValueError(new str("Inputs are not the same length"));

        sum += a*b;
    }

    return sum;
}

inline __ss_bool isclose(__ss_float a, __ss_float b, __ss_float rel_tol=1e-09, __ss_float abs_tol=0.0) {
    if (rel_tol < 0.0 || abs_tol < 0.0)
        throw new ValueError(new str("tolerances must be non-negative"));

    if (a == b)
        return True;

    if (!std::isfinite(a) || !std::isfinite(b))
        return False;

    __ss_float diff = fabs(a - b);
    return __mbool(diff <= abs_tol || diff <= fabs(rel_tol * a) || diff <= fabs(rel_tol * b));
}


inline __ss_float fmax(__ss_float x, __ss_float y) {
    return std::fmax(x, y);
}

inline __ss_float fmin(__ss_float x, __ss_float y) {
    return std::fmin(x, y);
}

inline __ss_bool isnormal(__ss_float x) {
    return __mbool(std::isnormal(x));
}

inline __ss_bool __ss_issubnormal(__ss_float x) {
    return __mbool(std::fpclassify(x) == FP_SUBNORMAL);
}

inline __ss_float nextafter(__ss_float x, __ss_float y) {
    return std::nextafter(x, y);
}

/* math.nextafter(x, y, steps=n): the value n representable steps after x
 * towards y. Like CPython, this walks the integer representation of the
 * floats, so the cost does not depend on n. */
inline __ss_float nextafter(__ss_float x, __ss_float y, __ss_int steps) {
    /* unsigned integer type with the same width as __ss_float */
#if defined(__SS_FLOAT32)
    typedef uint32_t __bits;
#else
    typedef uint64_t __bits;
#endif
    static_assert(sizeof(__bits) == sizeof(__ss_float),
                  "nextafter assumes __ss_float has an integer counterpart of equal width");

    if(steps < 0)
        throw new ValueError(new str("steps must be a non-negative integer"));

    /* __ss_int and __bits can each be the wider type (--int128 with doubles,
     * --float32 with 64-bit ints), so saturate by detecting truncation rather
     * than by comparing the two ranges. Saturating is harmless: a step count
     * spanning the whole range lands on y either way. */
    __ss_uint nsteps = (__ss_uint)steps;
    __bits usteps = (__bits)nsteps;
    if((__ss_uint)usteps != nsteps)
        usteps = std::numeric_limits<__bits>::max();

    if(usteps == 0)
        return x;
    if(std::isnan(x))
        return x;
    if(std::isnan(y))
        return y;

    /* type-punned via memcpy, assuming __ss_float and __bits share endianness */
    __bits ix, iy;
    memcpy(&ix, &x, sizeof(__bits));
    memcpy(&iy, &y, sizeof(__bits));

    if(ix == iy)
        return x;

    const __bits sign_bit = (__bits)1 << (8 * sizeof(__bits) - 1);
    const __bits ax = (__bits)(ix & (__bits)~sign_bit);
    const __bits ay = (__bits)(iy & (__bits)~sign_bit);

    __bits result;
    if((ix ^ iy) & sign_bit) {
        /* opposite signs: ax+ay cannot overflow, as neither has its top bit set */
        if((__bits)(ax + ay) <= usteps)
            result = iy;
        /* strictly less-than, so that +0.0 and -0.0 come out right */
        else if(ax < usteps)
            result = (__bits)((iy & sign_bit) | (__bits)(usteps - ax));
        else
            result = (__bits)(ix - usteps);
    } else if(ax > ay) {
        result = ((__bits)(ax - ay) >= usteps) ? (__bits)(ix - usteps) : iy;
    } else {
        result = ((__bits)(ay - ax) >= usteps) ? (__bits)(ix + usteps) : iy;
    }

    __ss_float r;
    memcpy(&r, &result, sizeof(__bits));
    return r;
}

inline __ss_float ulp(__ss_float x) {
    if(std::isnan(x))
        return x;
    x = fabs(x);
    if(std::isinf(x))
        return x;
    __ss_float x2 = std::nextafter(x, std::numeric_limits<__ss_float>::infinity());
    if(std::isinf(x2)) {
        /* x is the largest positive representable value */
        x2 = std::nextafter(x, -std::numeric_limits<__ss_float>::infinity());
        return x - x2;
    }
    return x2 - x;
}

inline __ss_float remainder(__ss_float x, __ss_float y) {
    if(std::isnan(x) || std::isnan(y))
        return std::remainder(x, y);
    if(std::isinf(x))
        throw new ValueError(new str("math domain error"));
    if(y == 0.0)
        throw new ValueError(new str("math domain error"));
    return std::remainder(x, y);
}

} // module namespace
#endif
