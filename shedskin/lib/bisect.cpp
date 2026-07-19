/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "bisect.hpp"

namespace __bisect__ {

str *__name__;

void __init() {
    __name__ = new str("bisect");
}

void __pos_check(__ss_int lo, __ss_int hi) {
    if(lo<0)
        throw new ValueError(new str("lo must be non-negative"));

}


} // module namespace

