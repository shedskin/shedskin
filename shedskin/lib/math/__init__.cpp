/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#define _USE_MATH_DEFINES
#include <cmath>

#include "__init__.hpp"

namespace __math__ {

__ss_float e = M_E, pi = M_PI, tau = 2 * M_PI, inf = INFINITY, nan = NAN;

void __math_domain_error(const char *msg, __ss_float x) {
    if(msg)
        throw new ValueError(__add_strs(2, new str(msg), __str(x)));
    throw new ValueError(new str("math domain error"));
}

void __math_range_error() {
    throw new OverflowError(new str("math range error"));
}

void __init() {
}

} // module namespace

