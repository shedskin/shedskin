#ifndef __BISECT_HPP
#define __BISECT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __bisect__ {

extern str * __name__;
void __init();

void __pos_check(__ss_int lo, __ss_int hi);

template <class A> void *insort_right(list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(x, a->units[mid])==-1) {
            hi = mid;
        }
        else {
            lo = (mid+1);
        }
    }
    a->insert(lo, x);
    return NULL;
}

template <class A> void *insort(list<A> *a, A x, __ss_int lo, __ss_int hi) {

    insort_right(a, x, lo, hi);
    return NULL;
}

template <class A> __ss_int bisect_right(list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(x, a->units[mid])==-1) {
            hi = mid;
        }
        else {
            lo = (mid+1);
        }
    }
    return lo;
}

template <class A> __ss_int bisect(list<A> *a, A x, __ss_int lo, __ss_int hi) {

    return bisect_right(a, x, lo, hi);
}

template <class A> void *insort_left(list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(a->units[mid], x)==-1) {
            lo = (mid+1);
        }
        else {
            hi = mid;
        }
    }
    a->insert(lo, x);
    return NULL;
}

template <class A> __ss_int bisect_left(list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(a->units[mid], x)==-1) {
            lo = (mid+1);
        }
        else {
            hi = mid;
        }
    }
    return lo;
}

template <class A> __ss_int bisect_left(list<A> *a, A x, __ss_int lo=0) {
    return bisect_left(a, x, lo, len(a));
}
template <class A> __ss_int bisect_right(list<A> *a, A x, __ss_int lo=0) {
    return bisect_right(a, x, lo, len(a));
}
template <class A> __ss_int bisect(list<A> *a, A x, __ss_int lo=0) {
    return bisect_right(a, x, lo, len(a));
}
template <class A> void *insort_left(list<A> *a, A x, __ss_int lo=0) {
    return insort_left(a, x, lo, len(a));
}
template <class A> void *insort_right(list<A> *a, A x, __ss_int lo=0) {
    return insort_right(a, x, lo, len(a));
}
template <class A> void *insort(list<A> *a, A x, __ss_int lo=0) {
    return insort_right(a, x, lo, len(a));
}

} // module namespace
#endif
