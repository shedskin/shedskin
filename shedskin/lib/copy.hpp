#ifndef COPY_HPP
#define COPY_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __copy__ {

template<class T> T deepcopy(T t) {
    return __deepcopy(t);
}
template<class T> T copy(T t) {
    return __copy(t);
}

void __init();

} // module namespace
#endif

