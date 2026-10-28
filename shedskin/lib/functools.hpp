/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __FUNCTOOLS_HPP
#define __FUNCTOOLS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __functools__ {

extern str * __name__;
void __init();

/* reduce */

/* the accumulator (A) and element (E) types may differ, as may the return
   type of func (R); initial is converted to the accumulator type, so that
   e.g. None (NULL) or an int can be used to start a str or float reduction */

template<class R, class A, class E, class B> A reduce(R (*func)(A, E), B *iter, std::type_identity_t<A> initial) {
    A result = initial;
    typename B::for_in_loop __7 = iter->for_in_init();
    while(iter->for_in_has_next(__7))
        result = (*func)(result, iter->for_in_next(__7));
    return result;
}

template<class R, class A, class E, class B> A reduce(R (*func)(A, E), B *iter) {
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
        throw new TypeError(new str("reduce() of empty iterable with no initial value"));
    return result;
}

} // module namespace
#endif
