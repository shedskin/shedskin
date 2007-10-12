#ifndef __SETS_HPP
#define __SETS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __sets__ {

template<class T> set<T> *Set(pyiter<T> *x) { return new set<T>(x); }

void __init();

} // module namespace
#endif
