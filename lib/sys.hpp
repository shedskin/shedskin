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

void __ss_exit();
template<class T> void __ss_exit(T x) {
    if(x == 0)
        __shedskin__::__exit();
    print(__ss_stderr, "%s\n", __str(x)); 
    __shedskin__::__exit(1);
}
template<> void __ss_exit(int x);

void *setrecursionlimit(int limit);

} // module namespace
#endif
