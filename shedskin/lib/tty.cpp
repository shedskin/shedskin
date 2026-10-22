/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "tty.hpp"

/* as cpython's tty.py */

namespace __tty__ {

using namespace __termios__;

str *__name__;
__ss_int IFLAG, OFLAG, CFLAG, LFLAG, ISPEED, OSPEED, CC;

void *cfmakeraw(TermAttributes *mode) {
    /* clear all POSIX.1-2017 input mode flags */
    mode->iflag &= ~(__ss_IGNBRK | __ss_BRKINT | __ss_IGNPAR | __ss_PARMRK | __ss_INPCK | __ss_ISTRIP |
                     __ss_INLCR | __ss_IGNCR | __ss_ICRNL | __ss_IXON | __ss_IXANY | __ss_IXOFF);
    /* do not post-process output */
    mode->oflag &= ~__ss_OPOST;
    /* disable parity generation and detection; 8-bit characters */
    mode->cflag &= ~(__ss_PARENB | __ss_CSIZE);
    mode->cflag |= __ss_CS8;
    /* clear all POSIX.1-2017 local mode flags */
    mode->lflag &= ~(__ss_ECHO | __ss_ECHOE | __ss_ECHOK | __ss_ECHONL | __ss_ICANON |
                     __ss_IEXTEN | __ss_ISIG | __ss_NOFLSH | __ss_TOSTOP);
    /* a read blocks until 1 byte is received, or a signal */
    mode->cc->__setitem__(__ss_VMIN, 1);
    mode->cc->__setitem__(__ss_VTIME, 0);
    return NULL;
}

void *cfmakecbreak(TermAttributes *mode) {
    /* do not echo characters; disable canonical input */
    mode->lflag &= ~(__ss_ECHO | __ss_ICANON);
    mode->cc->__setitem__(__ss_VMIN, 1);
    mode->cc->__setitem__(__ss_VTIME, 0);
    return NULL;
}

/* when=-2 is the TCSAFLUSH default, which is not a constant expression */

TermAttributes *setraw(__ss_int fd, __ss_int when) {
    TermAttributes *mode = tcgetattr(fd);
    TermAttributes *mode2 = mode->copy();
    cfmakeraw(mode2);
    tcsetattr(fd, when == -2 ? __ss_TCSAFLUSH : when, mode2);
    return mode;
}

TermAttributes *setcbreak(__ss_int fd, __ss_int when) {
    TermAttributes *mode = tcgetattr(fd);
    TermAttributes *mode2 = mode->copy();
    cfmakecbreak(mode2);
    tcsetattr(fd, when == -2 ? __ss_TCSAFLUSH : when, mode2);
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
