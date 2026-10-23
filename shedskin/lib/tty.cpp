/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "tty.hpp"

namespace __tty__ {

str *__name__;
__ss_int IFLAG, OFLAG, CFLAG, LFLAG, ISPEED, OSPEED, CC;

/* the control characters are copied, as with 'mode[CC] = list(mode[CC])' in
   CPython, so a shallow copy of mode does not change the original */
static void __setmin(tcattrs *mode) {
    mode->cc = mode->cc->__copy__();
    mode->cc->cc[VMIN] = 1;
    mode->cc->cc[VTIME] = 0;
}

void *cfmakeraw(tcattrs *mode) {
    /* clear all POSIX.1-2017 input mode flags */
    mode->flags[0] &= ~(__ss_int)(IGNBRK | BRKINT | IGNPAR | PARMRK | INPCK | ISTRIP |
                                  INLCR | IGNCR | ICRNL | IXON | IXANY | IXOFF);
    /* do not post-process output */
    mode->flags[1] &= ~(__ss_int)OPOST;
    /* disable parity generation and detection; character size 8 bits */
    mode->flags[2] &= ~(__ss_int)(PARENB | CSIZE);
    mode->flags[2] |= (__ss_int)CS8;
    /* clear all POSIX.1-2017 local mode flags */
    mode->flags[3] &= ~(__ss_int)(ECHO | ECHOE | ECHOK | ECHONL | ICANON |
                                  IEXTEN | ISIG | NOFLSH | TOSTOP);
    __setmin(mode);
    return NULL;
}

void *cfmakecbreak(tcattrs *mode) {
    /* do not echo characters; disable canonical input */
    mode->flags[3] &= ~(__ss_int)(ECHO | ICANON);
    __setmin(mode);
    return NULL;
}

/* returns the original mode, like CPython 3.12+ */
tcattrs *__setmode(int fd, __ss_int when, bool raw) {
    tcattrs *mode = __termios__::__tcgetattr(fd);
    tcattrs *n = mode->__copy__();
    if(raw)
        cfmakeraw(n);
    else
        cfmakecbreak(n);
    __termios__::__tcsetattr(fd, when, n);
    return mode;
}

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
