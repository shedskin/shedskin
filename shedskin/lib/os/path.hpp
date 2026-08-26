/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __PATH_HPP
#define __PATH_HPP

#include "builtin.hpp"
#include "os/__init__.hpp"
#include "stat.hpp"

using namespace __shedskin__;

namespace __os__ {
namespace __path__ {

extern str *__name__, *altsep, *curdir, *defpath, *devnull, *extsep, *pardir, *pathsep, *sep;
extern tuple2<str *, str *> *const_2;
extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_20, *const_21, *const_22, *const_23, *const_24, *const_25, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;
#ifdef WIN32
extern __ss_int supports_unicode_filenames;
#endif

str *normcase(str *s);
__ss_bool isabs(str *s);
str *joinl(list<str *> *l);

template <class ... Args> str *join(__ss_int, Args ... args) {
    list<str *> *p = new list<str *>();
    (p->append(args), ...);
    return joinl(p);
}

tuple2<str *, str *> *split(str *p);
tuple2<str *, str *> *splitext(str *p);
tuple2<str *, str *> *splitdrive(str *p);
str *basename(str *p);
bytes *basename(bytes *p); /* TODO ugh, support bytes everywhere..? */
str *dirname(str *p);
str *commonprefix(list<str *> *m);
__ss_int getsize(str *filename);
double getmtime(str *filename);
double getatime(str *filename);
double getctime(str *filename);
__ss_bool islink(str *path);
__ss_bool exists(str *path);
__ss_bool lexists(str *path);
__ss_bool isdir(str *path);
__ss_bool isfile(str *path);
str *normpath(str *path);
str *abspath(str *path);
str *realpath(str *filename);
str *relpath(str *path, str *start=0);
str *expanduser(str *path);
str *expandvars(str *path);
str *commonpath(list<str *> *paths);

__ss_bool samefile(str *f1, str *f2);
__ss_bool samestat(__os__::__cstat *s1, __os__::__cstat *s2);
__ss_bool ismount(str *path);
str *_resolve_link(str *path);

void __init();

} // module namespace
} // module namespace
#endif
