/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "collections.hpp"

namespace __collections__ {

str *__name__;
class_ *cl_deque;

void __init() {
    __name__ = new str("collections");
    cl_deque = new class_("deque");


}

} // module namespace

