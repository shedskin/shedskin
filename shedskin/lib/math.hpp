/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __MATH_HPP
#define __MATH_HPP

#include "builtin.hpp"
#include <math.h>
#include <numeric>

using namespace __shedskin__;
namespace __math__ {

extern __ss_float pi;
extern __ss_float e;
extern __ss_float tau;
extern __ss_float inf;
extern __ss_float nan;

void __init();

inline __ss_float ceil(__ss_float x) {
    return std::ceil(x);
}

inline __ss_float fabs(__ss_float x) {
    return std::fabs(x);
}

inline __ss_int factorial(__ss_int x) {
    if (x < 0) 
        throw new ValueError(new str("factorial() not defined for negative values"));

    __ss_int result = 1;
    for (__ss_int i = 1; i <= x; ++i) {
        result *= i;
    }

    return result;
}

inline __ss_float floor(__ss_float x) {
    return std::floor(x);
}

inline __ss_float fmod(__ss_float x, __ss_float y) {
    return std::fmod(x, y);
}

inline tuple2<__ss_float, __ss_float> *modf(__ss_float x) {
    return (new tuple2<__ss_float, __ss_float>(2, x-(__ss_int)x, (__ss_float)(__ss_int)x));
}

inline __ss_float ldexp(__ss_float x, __ss_int i) {
    return std::ldexp(x, i);
}

inline __ss_float exp(__ss_float x) {
    return std::exp(x);
}

inline __ss_float exp2(__ss_float x) {
    return std::exp2(x);
}

inline __ss_float log(__ss_float x) {
    return std::log(x);
}

inline __ss_float log2(__ss_float x) {
    return std::log2(x);
}

inline __ss_float log(__ss_float x, __ss_float base) {
    return std::log(x) / std::log(base);
}

inline __ss_float log10(__ss_float x) {
    return std::log10(x);
}

inline __ss_float sqrt(__ss_float x) {
    return std::sqrt(x);
}
inline __ss_float cbrt(__ss_float x) {
    return std::cbrt(x);
}

inline __ss_int isqrt(__ss_float x) {
    return floor(std::sqrt(x)); // TODO optimize?
}

inline __ss_float acos(__ss_float x) {
    return std::acos(x);
}

inline __ss_float asin(__ss_float x) {
    return std::asin(x);
}

inline __ss_float atan(__ss_float x) {
    return std::atan(x);
}

inline __ss_float atan2(__ss_float x, __ss_float y) {
    return std::atan2(x, y);
}

inline __ss_float cos(__ss_float x) {
    return std::cos(x);
}

inline __ss_float hypot(__ss_float x, __ss_float y) {
    return sqrt(x*x+y*y);
}

inline __ss_float sin(__ss_float x) {
    return std::sin(x);
}

inline __ss_float tan(__ss_float x) {
    return std::tan(x);
}

inline __ss_float degrees(__ss_float x) {
    return x*(180.0/pi);
}

inline __ss_float radians(__ss_float x) {
    return x/(180.0/pi);
}

inline __ss_float cosh(__ss_float x) {
    return std::cosh(x);
}

inline __ss_float sinh(__ss_float x) {
    return std::sinh(x);
}

inline __ss_float tanh(__ss_float x) {
    return std::tanh(x);
}

inline __ss_float pow(__ss_float x, __ss_float y) {
    return std::pow(x,y);
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

inline __ss_float acosh(__ss_float x) {
    return ::acosh(x);
}

inline __ss_float asinh(__ss_float x) {
    return ::asinh(x);
}

inline __ss_float atanh(__ss_float x) {
    return ::atanh(x);
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
    return ::expm1(x);
}

inline tuple2<__ss_float, __ss_int> *frexp(__ss_float x) {
    int n;
    __ss_float mantisa = std::frexp(x, &n);

    return (new tuple2<__ss_float, __ss_int>(2, mantisa, n));
}

inline __ss_float gamma(__ss_float x) {
    return ::tgamma(x);
}

inline __ss_float lgamma(__ss_float x) {
    return ::lgamma(x);
}

inline __ss_float log1p(__ss_float x) {
    return ::log1p(x);
}

inline __ss_int trunc(__ss_float x) {
    return (__ss_int)::trunc(x);
}

inline __ss_int comb(__ss_int n, __ss_int k) { // TODO faster/std version?
    if(n < 0)
        throw new ValueError(new str("n must be a non-negative number"));
    if(k < 0)
        throw new ValueError(new str("k must be a non-negative number"));
    __ss_int b=1;
    for(int p=1; p<=k; p++) {
        b = b*(n+1-p)/p;
    }
    return b;
}

inline __ss_float fsum(pyiter<__ss_float> *iterable) {
    list<__ss_float> *partials;
    __ss_float hi, lo, x, y;
    __ss_int i;

    __ss_int __2;
    pyiter<__ss_float> *__1;
    pyiter<__ss_float>::for_in_loop __3;

    partials = (new list<__ss_float>());

    FOR_IN(x,iterable,1,2,3)
        i = 0;
        for(__ss_int j=0; j<partials->__len__(); j++) {
            y = partials->__getitem__(i);
            if ((__abs(x)<__abs(y))) {
                __ss_float swap = y;
                y = x;
                x = swap;
            }
            hi = (x+y);
            lo = (y-(hi-x));
            if (___bool(lo)) {
                partials->__setitem__(i, lo);
                i = (i+1);
            }
            x = hi;
        }

        (partials)->__setslice__(1,i,0,0,(new list<__ss_float>(1,x)));
    END_FOR

    return __sum(partials);
}

template<class ... Args> __ss_int gcd(int, __ss_int x, Args ... args) {
    return ((x = std::gcd(x, args)), ...);
}
inline __ss_int gcd(int, __ss_int x) {
    return x;
}
inline __ss_int gcd(int) {
    return 0;
}

template<class ... Args> __ss_int lcm(int, __ss_int x, Args ... args) {
    return ((x = std::lcm(x, args)), ...);
}
inline __ss_int lcm(int, __ss_int x) {
    return x;
}
inline __ss_int lcm(int) {
    return 1;
}

inline __ss_int perm(__ss_int n, __ss_int k) {
    __ss_int result = 1;
    for(__ss_int i = n-k+1; i <= n; i++)
        result *= i;
    return result;
}
inline __ss_int perm(__ss_int n) {
    return factorial(n);
}


} // module namespace
#endif
