/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "sys.hpp"
#include <stdio.h>
#include <climits>
#include <limits>
#include <cfloat>

namespace __sys__ {

list<str *> *argv, *orig_argv;
str *version, *float_repr_style;

class_ *cl_float_info, *cl_implementation;
__float_info *float_info;
__implementation *implementation;

tuple2<__ss_int, __ss_int> *version_info;
str *__name__, *copyright, *platform, *byteorder;
__ss_int hexversion, maxsize, maxunicode;
str *executable;
file *__ss_stdin, *__ss_stdout, *__ss_stderr;

void __init(int c, char **v) {
    argv = new list<str *>();

#if defined( _MSC_VER )
    version = new str("Shed Skin Python-to-C++ Compiler 0.9.13\n[MSVC ");
    version = version->__add__(__str(_MSC_VER))->__add__(new str("]"));
#else
    version = new str("Shed Skin Python-to-C++ Compiler 0.9.13\n[GCC ");
    version = version->__add__(new str(__VERSION__))->__add__(new str("]"));
#endif
    version_info = new tuple2<__ss_int, __ss_int>(5, (__ss_int)3, (__ss_int)14, (__ss_int)0, (__ss_int)0, (__ss_int)0);
    hexversion = 0x030e00f0;

    copyright = new str("Copyright (c) Mark Dufour 2005-2026.\nAll Rights Reserved.");

    platform = new str("unknown");
#ifdef __linux__
    platform = new str("linux");
#endif
#ifdef __APPLE__
    platform = new str("darwin");
#endif
#ifdef WIN32
    platform = new str("win32");
#endif

    maxsize = std::numeric_limits<__ss_int>::max();
    maxunicode = 255; /* str is byte-based here; chr()/ord() are limited to range(256) */

    /* a compiled binary has no interpreter options in front of the
       program arguments, so orig_argv equals argv here */
    orig_argv = new list<str *>();
    for(int i=0; i<c; i++) {
        argv->append(new str(v[i]));
        orig_argv->append(new str(v[i]));
    }

    float_repr_style = new str("short");

    cl_float_info = new class_("float_info");
    cl_implementation = new class_("implementation");
    float_info = new __float_info();
    implementation = new __implementation();

    executable = (c > 0) ? new str(v[0]) : new str("");

    __ss_stdin = __shedskin__::__ss_stdin;
    __ss_stdout = __shedskin__::__ss_stdout;
    __ss_stderr = __shedskin__::__ss_stderr;

    int num = 1;
    if (*(char *)&num == 1)
        byteorder = new str("little");
    else
        byteorder = new str("big");
}

void __ss_exit() {
    throw new SystemExit((__ss_int)0);
}

__ss_int __recursionlimit = 1000; /* CPython's default */

void *setrecursionlimit(__ss_int limit) {
    if (limit < 1)
        throw new ValueError(new str("recursion limit must be greater or equal than 1"));
    __recursionlimit = limit;
    return NULL;
}

__ss_int getrecursionlimit() {
    return __recursionlimit;
}

str *intern(str *s) {
    return s; /* interning is a pure perf hint in CPython; identity is spec-compliant */
}

__ss_bool is_finalizing() {
    return False; /* no interpreter teardown phase in a compiled binary */
}

str *getdefaultencoding() {
    return new str("utf-8");
}

str *getfilesystemencoding() {
    return new str("utf-8");
}

str *getfilesystemencodeerrors() {
#ifdef WIN32
    return new str("surrogatepass");
#else
    return new str("surrogateescape");
#endif
}

__float_info::__float_info() {
    typedef std::numeric_limits<__ss_float> lim;
    this->__class__ = cl_float_info;
    this->max = lim::max();
    this->max_exp = lim::max_exponent;
    this->max_10_exp = lim::max_exponent10;
    this->min = lim::min();
    this->min_exp = lim::min_exponent;
    this->min_10_exp = lim::min_exponent10;
    this->dig = lim::digits10;
    this->mant_dig = lim::digits;
    this->epsilon = lim::epsilon();
    this->radix = lim::radix;
    this->rounds = FLT_ROUNDS;
}

str *__float_info::__repr__() {
    return __mod6(new str("sys.float_info(max=%s, max_exp=%d, max_10_exp=%d, min=%s, min_exp=%d, min_10_exp=%d, dig=%d, mant_dig=%d, epsilon=%s, radix=%d, rounds=%d)"), 11,
        repr(this->max), this->max_exp, this->max_10_exp,
        repr(this->min), this->min_exp, this->min_10_exp,
        this->dig, this->mant_dig, repr(this->epsilon),
        this->radix, this->rounds);
}

__implementation::__implementation() {
    this->__class__ = cl_implementation;
    this->name = new str("shedskin");
    this->version = version_info;
    this->hexversion = __sys__::hexversion;
}

str *__implementation::__repr__() {
    return __mod6(new str("namespace(name=%s, version=%s, hexversion=%d)"), 3,
        repr(this->name), repr(this->version), this->hexversion);
}

} // module namespace

