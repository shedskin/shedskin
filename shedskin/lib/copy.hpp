/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef COPY_HPP
#define COPY_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __copy__ {

extern class_ *cl_Error;

class Error : public Exception {
public:

    Error() {}
    Error(str *msg) : Exception(msg) {
        this->__class__ = cl_Error;
    }
};

template<class T> T deepcopy(T t) {
    return __deepcopy(t);
}
template<class T> T copy(T t) {
    return __copy(t);
}

void __init();

} // module namespace
#endif

