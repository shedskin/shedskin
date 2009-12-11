#include "collections.hpp"

namespace __collections__ {

str *__name__;
class_ *cl_deque;

void __init() {
    __name__ = new str("collections");
    cl_deque = new class_("deque", 1, 1);


}

} // module namespace

