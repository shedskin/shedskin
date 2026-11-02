/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __BISECT_HPP
#define __BISECT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __bisect__ {

extern str * __name__;
void __init();

/* validate 'lo'/'hi' and resolve CPython's '-1' sentinel for 'hi' */
__ss_int __pos_check(__ss_int lo, __ss_int hi, __ss_int size);

/* out-of-line so the binary search loops stay small */
void __idx_error();

/* 'lo' and 'hi' are both non-negative whenever the loop body runs, so the
   unsigned addition below just avoids signed overflow for huge bounds
   (CPython does the same, see its issue 13496) */
static inline void __idx_check(__ss_int mid, __ss_int size) {
    if(mid >= size)
        __idx_error();
}

template <class A, class B> void *insort_left(B (*key)(A), list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid, size = len(a);
    hi = __pos_check(lo, hi, size);
    B key_x = key(x);

    while((lo<hi)) {
        mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        __idx_check(mid, size);
        if (__lt(key(a->units[mid]), key_x))
            lo = (mid+1);
        else
            hi = mid;
    }
    a->insert(lo, x);
    return NULL;
}

template <class A> void *insort_left(long int /* key = None */, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid, size = len(a);
    hi = __pos_check(lo, hi, size);

    while((lo<hi)) {
        mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        __idx_check(mid, size);
        if (__lt(a->units[mid], x)) {
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
    __ss_int mid, size = len(a);
    hi = __pos_check(lo, hi, size);
    B key_x = key(x);

    while((lo<hi)) {
        mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        __idx_check(mid, size);
        if (__lt(key_x, key(a->units[mid]))) {
            hi = mid;
        }
        else {
            lo = (mid+1);
        }
    }
    a->insert(lo, x);
    return NULL;
}

template <class A> void *insort_right(long int /* key = None */, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid, size = len(a);
    hi = __pos_check(lo, hi, size);

    while((lo<hi)) {
        mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        __idx_check(mid, size);
        if (__lt(x, a->units[mid])) {
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
    return insort_right((long int)0, a, x, lo, hi);
}

template <class A, class B> void *insort(B (*key)(A), list<A> *a, A x, __ss_int lo, __ss_int hi) {
    return insort_right(key, a, x, lo, hi);
}


template <class A, class B> __ss_int bisect_left(B (*key)(A), list<A> *a, B x, __ss_int lo, __ss_int hi) {
    __ss_int mid, size = len(a);
    hi = __pos_check(lo, hi, size);

    while((lo<hi)) {
        mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        __idx_check(mid, size);
        if (__lt(key(a->units[mid]), x))
            lo = (mid+1);
        else
            hi = mid;
    }
    return lo;
}

template <class A> __ss_int bisect_left(long int /* key = None */, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid, size = len(a);
    hi = __pos_check(lo, hi, size);

    while((lo<hi)) {
        mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        __idx_check(mid, size);
        if (__lt(a->units[mid], x))
            lo = (mid+1);
        else
            hi = mid;
    }
    return lo;
}

template <class A, class B> __ss_int bisect_right(B (*key)(A), list<A> *a, B x, __ss_int lo, __ss_int hi) {
    __ss_int mid, size = len(a);
    hi = __pos_check(lo, hi, size);

    while((lo<hi)) {
        mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        __idx_check(mid, size);
        if (__lt(x, key(a->units[mid])))
            hi = mid;
        else
            lo = (mid+1);
    }
    return lo;
}

template <class A> __ss_int bisect_right(long int /* key = None */, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    __ss_int mid, size = len(a);
    hi = __pos_check(lo, hi, size);

    while((lo<hi)) {
        mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        __idx_check(mid, size);
        if (__lt(x, a->units[mid]))
            hi = mid;
        else
            lo = (mid+1);
    }
    return lo;
}

template <class A> __ss_int bisect(__ss_int, list<A> *a, A x, __ss_int lo, __ss_int hi) {
    return bisect_right((long int)0, a, x, lo, hi);
}

template <class A, class B> __ss_int bisect(B (*key)(A), list<A> *a, B x, __ss_int lo, __ss_int hi) {
    return bisect_right(key, a, x, lo, hi);
}

/* any other sequence (tuple, str, bytes, deque, array, user classes..):
   like CPython's _bisect, only __getitem__ is needed, plus __len__ when 'hi'
   is omitted and insert() for insort. lists keep the overloads above, which
   C++ partial ordering prefers. mid is always in [lo, hi), so never negative,
   and an out-of-range 'hi' is left to __getitem__ to report, as in CPython */

/* pyobj has a catch-all virtual __len__ (returning 1), so check whether the
   class (or a base class) actually overrides it */
template <class T> __ss_int __seq_len(T *a) {
    if constexpr (!std::is_same_v<decltype(&T::__len__), decltype(&pyobj::__len__)>)
        return len(a);
    else
        throw new TypeError(__add_strs(3, new str("object of type '"), a->__class__->__name__, new str("' has no len()")));
}

/* only calls __len__ for the '-1' sentinel, and only after 'lo' is known to
   be valid (__pos_check then sees hi == size and returns it) */
template <class T> __ss_int __seq_pos_check(__ss_int lo, __ss_int hi, T *a) {
    if(hi == -1 && lo >= 0)
        hi = __seq_len(a);
    return __pos_check(lo, hi, hi);
}

template <class T, class A> __ss_int bisect_left(long int /* key = None */, T *a, A x, __ss_int lo, __ss_int hi) {
    hi = __seq_pos_check(lo, hi, a);
    while(lo < hi) {
        __ss_int mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        if(__lt(a->__getitem__(mid), x))
            lo = mid+1;
        else
            hi = mid;
    }
    return lo;
}

template <class T, class A, class B> __ss_int bisect_left(B (*key)(A), T *a, B x, __ss_int lo, __ss_int hi) {
    hi = __seq_pos_check(lo, hi, a);
    while(lo < hi) {
        __ss_int mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        if(__lt(key(a->__getitem__(mid)), x))
            lo = mid+1;
        else
            hi = mid;
    }
    return lo;
}

template <class T, class A> __ss_int bisect_right(long int /* key = None */, T *a, A x, __ss_int lo, __ss_int hi) {
    hi = __seq_pos_check(lo, hi, a);
    while(lo < hi) {
        __ss_int mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        if(__lt(x, a->__getitem__(mid)))
            hi = mid;
        else
            lo = mid+1;
    }
    return lo;
}

template <class T, class A, class B> __ss_int bisect_right(B (*key)(A), T *a, B x, __ss_int lo, __ss_int hi) {
    hi = __seq_pos_check(lo, hi, a);
    while(lo < hi) {
        __ss_int mid = (__ss_int)(((size_t)lo + (size_t)hi) / 2);
        if(__lt(x, key(a->__getitem__(mid))))
            hi = mid;
        else
            lo = mid+1;
    }
    return lo;
}

template <class T, class A> __ss_int bisect(__ss_int, T *a, A x, __ss_int lo, __ss_int hi) {
    return bisect_right((long int)0, a, x, lo, hi);
}

template <class T, class A, class B> __ss_int bisect(B (*key)(A), T *a, B x, __ss_int lo, __ss_int hi) {
    return bisect_right(key, a, x, lo, hi);
}

template <class T, class A> void *insort_left(long int /* key = None */, T *a, A x, __ss_int lo, __ss_int hi) {
    a->insert(bisect_left((long int)0, a, x, lo, hi), x);
    return NULL;
}

template <class T, class A, class B> void *insort_left(B (*key)(A), T *a, A x, __ss_int lo, __ss_int hi) {
    a->insert(bisect_left(key, a, key(x), lo, hi), x);
    return NULL;
}

template <class T, class A> void *insort_right(long int /* key = None */, T *a, A x, __ss_int lo, __ss_int hi) {
    a->insert(bisect_right((long int)0, a, x, lo, hi), x);
    return NULL;
}

template <class T, class A, class B> void *insort_right(B (*key)(A), T *a, A x, __ss_int lo, __ss_int hi) {
    a->insert(bisect_right(key, a, key(x), lo, hi), x);
    return NULL;
}

template <class T, class A> void *insort(__ss_int, T *a, A x, __ss_int lo, __ss_int hi) {
    return insort_right((long int)0, a, x, lo, hi);
}

template <class T, class A, class B> void *insort(B (*key)(A), T *a, A x, __ss_int lo, __ss_int hi) {
    return insort_right(key, a, x, lo, hi);
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
