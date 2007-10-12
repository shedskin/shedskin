#ifndef __PATH_HPP
#define __PATH_HPP

#include "builtin.hpp"
#include "os/__init__.hpp"
#include "stat.hpp"

using namespace __shedskin__;
namespace __os__ {
namespace __path__ {


void __init();
tuple2<str *, str *> *split(str *p);
tuple2<str *, str *> *splitext(str *p);
int isdir(str *path);
int exists(str *path);
int islink(str *path);
int isfile(str *path);

} // module namespace
} // module namespace
#endif
