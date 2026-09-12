/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __SYS_HPP
#define __SYS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __sys__ {

void __init(int argc, char **argv);

extern list<str *> *argv;
extern str *version;
extern tuple2<__ss_int, __ss_int> *version_info;
extern str *__name__, *copyright, *platform, *byteorder;
extern __ss_int hexversion, maxsize, maxunicode;
extern str *executable;
extern file *__ss_stdin, *__ss_stdout, *__ss_stderr;

void __ss_exit();
template<class T> void __ss_exit(T x) {
    throw new SystemExit(x);
}

extern __ss_int __recursionlimit;

void *setrecursionlimit(__ss_int limit);
__ss_int getrecursionlimit();

str *intern(str *s);
__ss_bool is_finalizing();
str *getdefaultencoding();
str *getfilesystemencoding();
str *getfilesystemencodeerrors();

extern str *float_repr_style;
extern list<str *> *orig_argv;

extern class_ *cl_float_info, *cl_implementation;

/* describes __ss_float, so it stays honest under --float32 */
class __float_info : public pyobj {
public:
    __ss_float max, min, epsilon;
    __ss_int max_exp, max_10_exp, min_exp, min_10_exp, dig, mant_dig, radix, rounds;

    __float_info();
    str *__repr__();
};

class __implementation : public pyobj {
public:
    str *name;
    tuple2<__ss_int, __ss_int> *version;
    __ss_int hexversion;

    __implementation();
    str *__repr__();
};

extern __float_info *float_info;
extern __implementation *implementation;

} // module namespace
#endif
