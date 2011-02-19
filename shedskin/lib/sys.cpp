#include "sys.hpp"
#include <stdio.h>
#include <climits>

namespace __sys__ {

list<str *> *argv;
str *version;

tuple2<__ss_int, __ss_int> *version_info;
str *__name__, *copyright, *platform;
__ss_int hexversion, maxint;
file *__ss_stdin, *__ss_stdout, *__ss_stderr;

void __init(int c, char **v) {
    argv = new list<str *>();

#if defined( _MSC_VER )
    version = new str("Shed Skin Python-to-C++ Compiler 0.7.1\n[MSVC ");
    version = version->__add__(__str(_MSC_VER))->__add__(new str("]"));
#else
    version = new str("Shed Skin Python-to-C++ Compiler 0.7.1\n[GCC ");
    version = version->__add__(new str(__VERSION__))->__add__(new str("]"));
#endif
    version_info = new tuple2<__ss_int, __ss_int>(5, (__ss_int)0, (__ss_int)7, (__ss_int)1, (__ss_int)0, (__ss_int)0);
    hexversion = 0x00070100;

    copyright = new str("Copyright (c) Mark Dufour 2005-2010.\nAll Rights Reserved.");
    platform = new str("shedskin");

    maxint = INT_MAX;

    for(int i=0; i<c; i++)
        argv->append(new str(v[i]));

    __ss_stdin = __shedskin__::__ss_stdin;
    __ss_stdout = __shedskin__::__ss_stdout;
    __ss_stderr = __shedskin__::__ss_stderr;
}

void __ss_exit() {
    throw new SystemExit((__ss_int)0);
};

void *setrecursionlimit(__ss_int limit) {
    return NULL;
}

} // module namespace

