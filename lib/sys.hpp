#ifndef __SYS_HPP
#define __SYS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __sys__ {

void __init(int argc, char **argv);

extern list<str *> *argv;
extern str *version;
extern file *_stdin, *_stdout, *_stderr;
void exit(int code=0);

} // module namespace
#endif
