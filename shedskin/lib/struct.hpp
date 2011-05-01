#ifndef __STRUCT_HPP
#define __STRUCT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __struct__ {

__ss_int unpack_int(char o, char c, int d, str *data, __ss_int *pos);
str * unpack_str(char o, char c, int d, str *data, __ss_int *pos);
__ss_int unpack(); /* unused */

__ss_int calcsize(str *fmt);

void __init();

} // module namespace
#endif
