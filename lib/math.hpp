#ifndef __MATH_HPP
#define __MATH_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __math__ {

extern double pi;
extern double e;

double ceil(double x);
double fabs(double x);
double floor(double x);
double fmod(double x, double y);
double ldexp(double x, int i);
tuple2<double, double> *modf(double x);
double exp(double x);
double log(double x);
double log(double x, double base);
double log10(double x);
double pow(double x, double y);
double sqrt(double x);
double acos(double x);
double asin(double x);
double atan(double x);
double atan2(double y, double x);
double cos(double x);
double hypot(double x, double y);
double sin(double x);
double tan(double x);
double degrees(double x);
double radians(double x);
double cosh(double x);
double sinh(double x);
double tanh(double x);

void __init();

} // module namespace
#endif
