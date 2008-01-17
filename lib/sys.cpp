#include <stdio.h>
#include "sys.hpp"

namespace __sys__ {

list<str *> *argv;
str *version;

file *_stdin, *_stdout, *_stderr;
tuple2<int, int> *version_info;
str *__name__, *copyright, *platform;
int hexversion, maxint;

void __init(int c, char **v) {
    argv = new list<str *>();

    version = new str("Shed Skin Python-to-C++ Compiler 0.0.26\n[GCC ");
    version = version->__add__(new str(__VERSION__))->__add__(new str("]"));
    version_info = new tuple2<int, int>(5, 0, 0, 26, 0, 0);
    hexversion = 0x0001900;

    copyright = new str("Copyright (c) Mark Dufour 2005-2008.\nAll Rights Reserved.");
    platform = new str("linux2");

    maxint = INT_MAX;

    for(int i=0; i<c; i++)
        argv->append(new str(v[i]));

    _stdin = new file(stdin);
    _stdout = new file(stdout); 
    _stderr = new file(stderr); 
}

void exit() {
    std::exit(0);
}; 

template<> void exit(int x) {
    std::exit(x);
}

} // module namespace

