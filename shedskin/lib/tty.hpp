/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __TTY_HPP
#define __TTY_HPP

#include "builtin.hpp"
#include "termios.hpp"

using namespace __shedskin__;
namespace __tty__ {

extern str *__name__;
extern __ss_int IFLAG, OFLAG, CFLAG, LFLAG, ISPEED, OSPEED, CC;

void *cfmakeraw(__termios__::TermAttributes *mode);
void *cfmakecbreak(__termios__::TermAttributes *mode);
__termios__::TermAttributes *setraw(__ss_int fd, __ss_int when=-2);
__termios__::TermAttributes *setcbreak(__ss_int fd, __ss_int when=-2);

void __init();

} // module namespace
#endif
