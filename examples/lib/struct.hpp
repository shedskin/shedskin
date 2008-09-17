#ifndef __STRUCT_HPP
#define __STRUCT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __struct__ {

str *pack_ints(str *fmt, pyseq<int> *s);
tuple2<int, int> *unpack_ints(str *fmt, str *s);

void __init();

} // module namespace
#endif
