#include <stdio.h>
#include <climits>
#include "sys.hpp"

namespace __sys__ {

list<str *> *argv;
str *version;

file *__ss_stdin, *__ss_stdout, *__ss_stderr;

tuple2<int, int> *version_info;
str *__name__, *copyright, *platform;
int hexversion, maxint;

void __init(int c, char **v) {
    argv = new list<str *>();

    version = new str("Shed Skin Python-to-C++ Compiler 0.1.2\n[GCC ");
    version = version->__add__(new str(__VERSION__))->__add__(new str("]"));
    version_info = new tuple2<int, int>(5, 0, 1, 2, 0, 0);
    hexversion = 0x00010200;

    copyright = new str("Copyright (c) Mark Dufour 2005-2008.\nAll Rights Reserved.");
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
    __shedskin__::__exit();
}; 

template<> void __ss_exit(int x) {
    __shedskin__::__exit(x);
}

} // module namespace

