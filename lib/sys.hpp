#ifndef __SYS_HPP
#define __SYS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __sys__ {

void __init(int argc, char **argv);

extern list<str *> *argv;
extern str *version;
extern tuple2<int, int> *version_info;
extern str *__name__, *copyright, *platform;
extern int hexversion, maxint;
extern file *__ss_stdin, *__ss_stdout, *__ss_stderr;

void exit();
template<class T> void exit(T x) {
    if(x == 0)
        std::exit(0);
    print(__ss_stderr, "%s\n", __str(x)); 
    std::exit(1);
}
template<> void exit(int x);

} // module namespace
#endif
