#ifndef __MATH_HPP
#define __MATH_HPP

#include "builtin.hpp"

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

} // module namespace
#endif
