#ifndef __FNMATCH_HPP
#define __FNMATCH_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __fnmatch__ {


void __init();
int fnmatch(str *f, str *p);
int fnmatchcase(str *f, str *p);

} // module namespace
#endif
