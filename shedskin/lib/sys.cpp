#include "sys.hpp"
#include <stdio.h>
#include <climits>

namespace __sys__ {

list<str *> *argv;
str *version;

file *__ss_stdin, *__ss_stdout, *__ss_stderr;

tuple2<__ss_int, __ss_int> *version_info;
str *__name__, *copyright, *platform;
__ss_int hexversion, maxint;

void __init(int c, char **v) {
    argv = new list<str *>();

#if defined( _MSC_VER )
    version = new str("Shed Skin Python-to-C++ Compiler 0.5\n[MSVC ");
    version = version->__add__(__str(_MSC_VER))->__add__(new str("]"));
#else
    version = new str("Shed Skin Python-to-C++ Compiler 0.5\n[GCC ");
    version = version->__add__(new str(__VERSION__))->__add__(new str("]"));
#endif
    version_info = new tuple2<__ss_int, __ss_int>(5, (__ss_int)0, (__ss_int)5, (__ss_int)0, (__ss_int)0, (__ss_int)0);
    hexversion = 0x00050000;

    copyright = new str("Copyright (c) Mark Dufour 2005-2010.\nAll Rights Reserved.");
    platform = new str("shedskin");

    maxint = INT_MAX;

    for(int i=0; i<c; i++)
        argv->append(new str(v[i]));

    __ss_stdin = new file(stdin);
    __ss_stdin->name = new str("<stdin>");
    __ss_stdout = new file(stdout);
    __ss_stdout->name = new str("<stdout>");
    __ss_stderr = new file(stderr);
    __ss_stderr->name = new str("<stderr>");
}

void __ss_exit() {
    throw new SystemExit((__ss_int)0);
};

void *setrecursionlimit(__ss_int limit) {
    return NULL;
}

} // module namespace

