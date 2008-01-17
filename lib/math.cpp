#include <stdio.h>
#include "math.hpp"

namespace __math__ {

double e, pi;

void __init() {
    e = 2.71828182846;
    pi = 3.14159265359;
}

double ceil(double x) {
    return std::ceil(x);
}

double fabs(double x) {
    return std::fabs(x);
}

double floor(double x) {
    return std::floor(x);
}

double fmod(double x, double y) {
    return std::fmod(x, y);
}

tuple2<double, double> *modf(double x) {
    return (new tuple2<double, double>(2, x-(int)x, (double)(int)x));
}

double ldexp(double x, int i) {
    return std::ldexp(x, i);
}

double exp(double x) {
    return std::exp(x);
}

double log(double x) {
    return std::log(x);
}

double log(double x, double base) {
    return std::log(x) / std::log(base);
}

double log10(double x) {
    return std::log10(x);
}

double sqrt(double x) {
    return std::sqrt(x);
}

double acos(double x) {
    return std::acos(x);
}

double asin(double x) {
    return std::asin(x);
}

double atan(double x) {
    return std::atan(x);
}

double atan2(double x, double y) {
    return std::atan2(x, y);
}

double cos(double x) {
    return std::cos(x);
}

double hypot(double x, double y) {
    return sqrt(x*x+y*y);
}

double sin(double x) {
    return std::sin(x);
}

double tan(double x) {
    return std::tan(x);
}

double degrees(double x) {
    return x*(180.0/pi);
}

double radians(double x) {
    return x/(180.0/pi);
}

double cosh(double x) {
    return std::cosh(x);
}

double sinh(double x) {
    return std::sinh(x);
}

double tanh(double x) {
    return std::tanh(x);
}

double pow(double x, double y) {
    return std::pow(x,y);
}

} // module namespace

