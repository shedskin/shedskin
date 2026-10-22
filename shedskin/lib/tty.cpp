/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "tty.hpp"

namespace __tty__ {

str *__name__;
__ss_int IFLAG, OFLAG, CFLAG, LFLAG, ISPEED, OSPEED, CC;

void __init() {
    __name__ = new str("tty");

    IFLAG = 0;
    OFLAG = 1;
    CFLAG = 2;
    LFLAG = 3;
    ISPEED = 4;
    OSPEED = 5;
    CC = 6;
}

} // module namespace
