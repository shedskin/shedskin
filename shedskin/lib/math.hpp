/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __MATH_HPP
#define __MATH_HPP

#include "builtin.hpp"
#include <math.h>

using namespace __shedskin__;
namespace __math__ {

extern double pi;
extern double e;

void __init();

inline double ceil(double x) {
    return std::ceil(x);
}

inline double fabs(double x) {
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

inline double floor(double x) {
    return std::floor(x);
}

inline double fmod(double x, double y) {
    return std::fmod(x, y);
}

inline tuple2<double, double> *modf(double x) {
    return (new tuple2<double, double>(2, x-(__ss_int)x, (double)(__ss_int)x));
}

inline double ldexp(double x, __ss_int i) {
    return std::ldexp(x, i);
}

inline double exp(double x) {
    return std::exp(x);
}

inline double log(double x) {
    return std::log(x);
}

inline double log(double x, double base) {
    return std::log(x) / std::log(base);
}

inline double log10(double x) {
    return std::log10(x);
}

inline double sqrt(double x) {
    return std::sqrt(x);
}

inline double acos(double x) {
    return std::acos(x);
}

inline double asin(double x) {
    return std::asin(x);
}

inline double atan(double x) {
    return std::atan(x);
}

inline double atan2(double x, double y) {
    return std::atan2(x, y);
}

inline double cos(double x) {
    return std::cos(x);
}

inline double hypot(double x, double y) {
    return sqrt(x*x+y*y);
}

inline double sin(double x) {
    return std::sin(x);
}

inline double tan(double x) {
    return std::tan(x);
}

inline double degrees(double x) {
    return x*(180.0/pi);
}

inline double radians(double x) {
    return x/(180.0/pi);
}

inline double cosh(double x) {
    return std::cosh(x);
}

inline double sinh(double x) {
    return std::sinh(x);
}

inline double tanh(double x) {
    return std::tanh(x);
}

inline double pow(double x, double y) {
    return std::pow(x,y);
}

inline __ss_bool isinf(double x) {
    return __mbool(std::isinf(x));
}

inline __ss_bool isnan(double x) {
    return __mbool(std::isnan(x));
}

inline double acosh(double x) {
    return ::acosh(x);
}

inline double asinh(double x) {
    return ::asinh(x);
}

inline double atanh(double x) {
    return ::atanh(x);
}

inline double copysign(double x, double y) {
    return ::copysign(x, y);
}

inline double erf(double x) {
    return ::erf(x);
}

inline double erfc(double x) {
    return ::erfc(x);
}

inline double expm1(double x) {
    return ::expm1(x);
}

inline tuple2<double, __ss_int> *frexp(double x) {
    __ss_int n;
    double mantisa = std::frexp(x, &n);

    return (new tuple2<double, __ss_int>(2, mantisa, n));
}

inline double gamma(double x) {
    return ::tgamma(x);
}

inline double lgamma(double x) {
    return ::lgamma(x);
}

inline double log1p(double x) {
    return ::log1p(x);
}

inline __ss_int trunc(double x) {
    return ::trunc(x);
}

inline double fsum(pyiter<double> *iterable) {
    list<double> *partials;
    double hi, lo, x, y;
    __ss_int i;

    __ss_int __2;
    pyiter<double> *__1;
    pyiter<double>::for_in_loop __3;

    partials = (new list<double>());

    FOR_IN(x,iterable,1,2,3)
        i = 0;
        for(__ss_int j=0; j<partials->__len__(); j++) {
            y = partials->__getitem__(i);
            if ((__abs(x)<__abs(y))) {
                double swap = y;
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

        (partials)->__setslice__(1,i,0,0,(new list<double>(1,x)));
    END_FOR

    return __sum(partials);
}

} // module namespace
#endif
