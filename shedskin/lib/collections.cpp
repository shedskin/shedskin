/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "collections.hpp"

namespace __collections__ {

str *__name__;
class_ *cl_deque;
class_ *cl_defaultdict;
class_ *cl_counter;

void __init() {
    __name__ = new str("collections");
    cl_deque = new class_("deque");
    cl_defaultdict = new class_("defaultdict");
    cl_counter = new class_("Counter");


}

} // module namespace

