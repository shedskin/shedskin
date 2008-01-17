#ifndef __BISECT_HPP
#define __BISECT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __bisect__ {

extern str * __name__;
void __init();

void __pos_check(int lo, int hi);

template <class A> int insort_right(list<A> *a, A x, int lo, int hi) {
    int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__lt(x, a->units[mid])) {
            hi = mid;
        }
        else {
            lo = (mid+1);
        }
    }
    a->insert(lo, x);
    return 0;
}

template <class A> int insort(list<A> *a, A x, int lo, int hi) {
    
    insort_right(a, x, lo, hi);
    return 0;
}

template <class A> int bisect_right(list<A> *a, A x, int lo, int hi) {
    int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__lt(x, a->units[mid])) {
            hi = mid;
        }
        else {
            lo = (mid+1);
        }
    }
    return lo;
}

template <class A> int bisect(list<A> *a, A x, int lo, int hi) {
    
    return bisect_right(a, x, lo, hi);
}

template <class A> int insort_left(list<A> *a, A x, int lo, int hi) {
    int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__lt(a->units[mid], x)) {
            lo = (mid+1);
        }
        else {
            hi = mid;
        }
    }
    a->insert(lo, x);
    return 0;
}

template <class A> int bisect_left(list<A> *a, A x, int lo, int hi) {
    int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = __divs((lo+hi), 2);
        if (__lt(a->units[mid], x)) {
            lo = (mid+1);
        }
        else {
            hi = mid;
        }
    }
    return lo;
}

template <class A> int bisect_left(list<A> *a, A x, int lo=0) {
    return bisect_left(a, x, lo, len(a));
}
template <class A> int bisect_right(list<A> *a, A x, int lo=0) {
    return bisect_right(a, x, lo, len(a));
}
template <class A> int bisect(list<A> *a, A x, int lo=0) {
    return bisect_right(a, x, lo, len(a));
}
template <class A> int insort_left(list<A> *a, A x, int lo=0) {
    return insort_left(a, x, lo, len(a));
}
template <class A> int insort_right(list<A> *a, A x, int lo=0) {
    return insort_right(a, x, lo, len(a));
}
template <class A> int insort(list<A> *a, A x, int lo=0) {
    return insort_right(a, x, lo, len(a));
}

} // module namespace
#endif
