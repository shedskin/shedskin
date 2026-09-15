/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "bisect.hpp"

namespace __bisect__ {

str *__name__;

void __init() {
    __name__ = new str("bisect");
}

__ss_int __pos_check(__ss_int lo, __ss_int hi, __ss_int size) {
    if(lo<0)
        throw new ValueError(new str("lo must be non-negative"));
    /* CPython's _bisect uses -1 as the in-band 'hi is None' sentinel: its
       argument clinic wrapper initializes hi to -1 and leaves it alone for
       None, so an explicitly passed -1 is indistinguishable and means
       len(a) as well. Other negative values just give an empty range.
       Note this is a leak rather than a designed feature -- the pure
       python bisect.py fallback returns an empty range for -1 -- so if
       CPython ever tightens it, follow the C module. */
    if(hi==-1)
        return size;
    return hi;
}

void __idx_error() {
    throw new IndexError(new str("list index out of range"));
}


} // module namespace

