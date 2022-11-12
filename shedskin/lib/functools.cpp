/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "functools.hpp"

namespace __functools__ {

str *__name__;

void __init() {
    __name__ = new str("functools");
}

} // module namespace

