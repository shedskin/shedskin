/* Copyright 2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __MATH_INTEGER_HPP
#define __MATH_INTEGER_HPP

#include "builtin.hpp"
#include <math.h>
#include <numeric>

using namespace __shedskin__;
namespace __math__ {
namespace __integer__ {

/* gcd */
template<class ... Args> __ss_int gcd(int, __ss_int x, Args ... args) {
    return ((x = std::gcd(x, args)), ...);
}
inline __ss_int gcd(int, __ss_int x) {
    return x;
}
inline __ss_int gcd(int) {
    return 0;
}

/* lcm */

template<class ... Args> __ss_int lcm(int, __ss_int x, Args ... args) {
    return ((x = std::lcm(x, args)), ...);
}
inline __ss_int lcm(int, __ss_int x) {
    return x;
}
inline __ss_int lcm(int) {
    return 1;
}

/* factorial */

inline __ss_int factorial(__ss_int x) {
    if (x < 0)
        throw new ValueError(new str("factorial() not defined for negative values"));

    __ss_int result = 1;
    for (__ss_int i = 1; i <= x; ++i) {
        result *= i;
    }

    return result;
}

/* perm */

inline __ss_int perm(__ss_int n, __ss_int k) {
    __ss_int result = 1;
    for(__ss_int i = n-k+1; i <= n; i++)
        result *= i;
    return result;
}
inline __ss_int perm(__ss_int n) {
    return factorial(n);
}

/* comb */

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

/* isqrt */

inline __ss_int isqrt(__ss_float x) {
    return (__ss_int)(floor(std::sqrt(x))); // TODO optimize?
}

void __init();

} // __integer__
} // __math__
#endif
