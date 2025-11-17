/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __BISECT_HPP
#define __BISECT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __bisect__ {

extern str * __name__;
void __init();

void __pos_check(__ss_int lo, __ss_int hi);

template <class A, class B> void *insort_left(B (*key)(A), list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(key(a->units[mid]), key(x)) == -1)
            lo = (mid+1);
        else
            hi = mid;
    }
    a->insert(lo, x);
    return NULL;
}

template <class A> void *insort_left(__ss_int /* key = None */, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(a->units[mid], x) == -1) {
            lo = (mid+1);
        }
        else {
            hi = mid;
        }
    }
    a->insert(lo, x);
    return NULL;

}

template <class A, class B> void *insort_right(B (*key)(A), list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(key(x), key(a->units[mid])) == -1) {
            hi = mid;
        }
        else {
            lo = (mid+1);
        }
    }
    a->insert(lo, x);
    return NULL;
}

template <class A> void *insort_right(__ss_int /* key = None */, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(x, a->units[mid]) == -1) {
            hi = mid;
        }
        else {
            lo = (mid+1);
        }
    }
    a->insert(lo, x);
    return NULL;

}

template <class A> void *insort(__ss_int, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    return insort_right((A (*)(A))0, a, x, lo, hi);
}


template <class A, class B> __ss_int bisect_left(B (*key)(A), list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(key(a->units[mid]), x)==-1)
            lo = (mid+1);
        else
            hi = mid;
    }
    return lo;
}

template <class A> __ss_int bisect_left(__ss_int /* key = None */, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(a->units[mid], x)==-1)
            lo = (mid+1);
        else
            hi = mid;
    }
    return lo;
}

template <class A, class B> __ss_int bisect_right(B (*key)(A), list<A> *a, B x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(x, key(a->units[mid]))==-1)
            hi = mid;
        else
            lo = (mid+1);
    }
    return lo;
}

template <class A> __ss_int bisect_right(__ss_int /* key = None */, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid;
    __pos_check(lo, hi);

    while((lo<hi)) {
        mid = (lo+hi)/2;
        if (__cmp(x, a->units[mid])==-1)
            hi = mid;
        else
            lo = (mid+1);
    }
    return lo;
}

template <class A> __ss_int bisect(__ss_int, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    return bisect_right((A (*)(A))0, a, x, lo, hi);
}

template <class A, class B, class C> __ss_int bisect_left(C key, list<A> *a, B x, __ss_int lo=0) {
    return bisect_left(key, a, x, lo, len(a));
}
template <class A, class B, class C> __ss_int bisect_right(C key, list<A> *a, B x, __ss_int lo=0) {
    return bisect_right(key, a, x, lo, len(a));
}
template <class A, class B, class C> __ss_int bisect(C key, list<A> *a, B x, __ss_int lo=0) {
    return bisect_right(key, a, x, lo, len(a));
}
template <class A, class B, class C> void *insort_left(C key, list<A> *a, B x, __ss_int lo=0) {
    return insort_left(key, a, x, lo, len(a));
}
template <class A, class B, class C> void *insort_right(C key, list<A> *a, B x, __ss_int lo=0) {
    return insort_right(key, a, x, lo, len(a));
}
template <class A, class B, class C> void *insort(C key, list<A> *a, B x, __ss_int lo=0) {
    return insort_right(key, a, x, lo, len(a));
}

} // module namespace
#endif
