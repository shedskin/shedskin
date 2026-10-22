/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __TTY_HPP
#define __TTY_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __tty__ {

extern str *__name__;
extern __ss_int IFLAG, OFLAG, CFLAG, LFLAG, ISPEED, OSPEED, CC;

void __init();

} // module namespace
#endif
