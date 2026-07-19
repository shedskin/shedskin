/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "sys.hpp"
#include <stdio.h>
#include <climits>

namespace __sys__ {

list<str *> *argv;
str *version;

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

    maxsize = INT_MAX;
    maxunicode = 255; /* str is byte-based here; chr()/ord() are limited to range(256) */

    for(int i=0; i<c; i++)
        argv->append(new str(v[i]));

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

} // module namespace

