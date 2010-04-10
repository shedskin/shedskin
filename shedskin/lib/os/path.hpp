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
extern str *const_0, *const_1, *const_10, *const_11, *const_12, *const_13, *const_14, *const_15, *const_16, *const_17, *const_18, *const_19, *const_3, *const_4, *const_5, *const_6, *const_7, *const_8, *const_9;
#ifdef WIN32
extern __ss_int supports_unicode_filenames;
#endif

str *normcase(str *s);
__ss_bool isabs(str *s);
str *joinl(list<str *> *l);
str *join(__ss_int n, ...);
tuple2<str *, str *> *split(str *p);
tuple2<str *, str *> *splitext(str *p);
tuple2<str *, str *> *splitdrive(str *p);
str *basename(str *p);
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

#ifndef WIN32
__ss_bool samefile(str *f1, str *f2);
__ss_bool samestat(__os__::__cstat *s1, __os__::__cstat *s2);
str *_resolve_link(str *path);
#endif

#ifndef WIN32
template <class A> void *walk(str *top, void *(*func)(A, str *, list<str *> *), A arg) {
    list<str *> *__21, *names;
    __iter<str *> *__22;
    str *name;
    __ss_int __23;
    __os__::__cstat *st;

    try {
        names = __os__::listdir(top);
    } catch (__os__::error *) {
        return NULL;
    }
    func(arg, top, names);

    FOR_IN_SEQ(name,names,21,23)
        name = join(2, top, name);
        try {
            st = __os__::lstat(name);
        } catch (__os__::error *) {
            continue;
        }
        if (__stat__::__ss_S_ISDIR(st->st_mode)) {
            walk(name, func, arg);
        }
    END_FOR

    return NULL;
}

#else
template <class A> void *walk(str *top, void *(*func)(A, str *, list<str *> *), A arg) {
    list<str *> *__33, *names;
    __iter<str *> *__34;
    str *name;
    tuple2<str *, str *> *exceptions;
    __ss_int __35;

    try {
        names = __os__::listdir(top);
    } catch (__os__::error *) {
        return NULL;
    }
    func(arg, top, names);
    exceptions = (new tuple2<str *, str *>(2, const_0, const_3));

    FOR_IN_SEQ(name,names,33,35)
        if ((!exceptions->__contains__(name))) {
            name = join(2, top, name);
            if (isdir(name)) {
                walk(name, func, arg);
            }
        }
    END_FOR

    return NULL;
}
#endif

void __init();

} // module namespace
} // module namespace
#endif
