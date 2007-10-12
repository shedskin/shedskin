#include <stdio.h>
#include "sys.hpp"

namespace __sys__ {

list<str *> *argv;
str *version;

file *_stdin, *_stdout, *_stderr;

void __init(int c, char **v) {
    argv = new list<str *>();
    version = new str("Shed Skin Python-to-C++ Compiler 0.0.25");

    for(int i=0; i<c; i++)
        argv->append(new str(v[i]));

    _stdin = new file(stdin);
    _stdout = new file(stdout); 
    _stderr = new file(stderr); 
}


void exit(int code) {
    std::exit(code);
};

} // module namespace

