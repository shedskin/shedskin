#ifndef __FNMATCH_HPP
#define __FNMATCH_HPP

#include "builtin.hpp"
#include "os/path.hpp"
#include "os/__init__.hpp"
#include "re.hpp"

using namespace __shedskin__;
namespace __fnmatch__ {

extern str *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_5, *const_6, *const_7, *const_8, *const_9;

extern dict<str *, __re__::re_object *> *_cache;
extern str *__name__;

__ss_bool fnmatch(str *name, str *pat);
list<str *> *filter(list<str *> *names, str *pat);
__ss_bool fnmatchcase(str *name, str *pat);
str *translate(str *pat);

void __init(void);

} // module namespace
#endif
