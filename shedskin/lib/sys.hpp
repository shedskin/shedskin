#ifndef __SYS_HPP
#define __SYS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __sys__ {

void __init(int argc, char **argv);

extern list<str *> *argv;
extern str *version;
extern tuple2<__ss_int, __ss_int> *version_info;
extern str *__name__, *copyright, *platform;
extern __ss_int hexversion, maxint;
extern file *__ss_stdin, *__ss_stdout, *__ss_stderr;

void __ss_exit();
template<class T> void __ss_exit(T x) {
    throw new SystemExit(x);
}

void *setrecursionlimit(__ss_int limit);

} // module namespace
#endif
