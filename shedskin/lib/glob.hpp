#ifndef __GLOB_HPP
#define __GLOB_HPP

#include "builtin.hpp"
#include "os/path.hpp"
#include "fnmatch.hpp"
#include "re.hpp"
#include "os/__init__.hpp"

using namespace __shedskin__;
namespace __glob__ {

extern str *const_0, *const_2, *const_3;

extern str *__name__;
extern __re__::re_object *magic_check;

list<str *> *glob(str *pathname);
__iter<str *> *iglob(str *pathname);
list<str *> *glob1(str *dirname, str *pattern);
list<str *> *glob0(str *dirname, str *basename);
__ss_bool has_magic(str *s);

void __init(void);

} // module namespace
#endif
