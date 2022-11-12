/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __FUNCTOOLS_HPP
#define __FUNCTOOLS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __functools__ {

extern str * __name__;
void __init();

/* reduce */

template<class A, class B, class C> A reduce(A (*func)(A, A), B *iter, C initial) {
    A result = initial;
    typename B::for_in_loop __7 = iter->for_in_init();
    while(iter->for_in_has_next(__7))
        result = (*func)(result, iter->for_in_next(__7));
    return result;
}

template<class A, class B> A reduce(A (*func)(A, A), B *iter) {
    A result;
    typename B::for_in_loop __7 = iter->for_in_init();
    int first = 1;
    while(iter->for_in_has_next(__7)) {
        if(first) {
            result = iter->for_in_next(__7);
            first = 0;
        } else
            result = (*func)(result, iter->for_in_next(__7));
    }
    if(first) 
        throw new TypeError(new str("reduce() of empty sequence with no initial value"));
    return result;
}

} // module namespace
#endif
