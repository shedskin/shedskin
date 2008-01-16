#ifndef TIME_HPP
#define TIME_HPP

#include "builtin.hpp"
#include <ctime>
#include <sys/time.h>

#ifdef WIN32
#include <sys/timeb.h>
#endif

using namespace __shedskin__;
namespace __time__ {

double clock();
double time();
void sleep(double s);
void __init();

} // module namespace
#endif
