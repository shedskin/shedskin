/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __TERMIOS_HPP
#define __TERMIOS_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __termios__ {

extern str *__name__;
extern __ss_int __ss_TCSANOW, __ss_TCSADRAIN, __ss_TCSAFLUSH, __ss_TCIFLUSH, __ss_TCOFLUSH, __ss_TCIOFLUSH, __ss_TCOOFF, __ss_TCOON, __ss_TCIOFF, __ss_TCION, __ss_IGNBRK, __ss_BRKINT, __ss_IGNPAR, __ss_PARMRK, __ss_INPCK, __ss_ISTRIP, __ss_INLCR, __ss_IGNCR, __ss_ICRNL, __ss_IUCLC, __ss_IXON, __ss_IXANY, __ss_IXOFF, __ss_IMAXBEL, __ss_IUTF8, __ss_OPOST, __ss_OLCUC, __ss_ONLCR, __ss_OCRNL, __ss_ONOCR, __ss_ONLRET, __ss_OFILL, __ss_OFDEL, __ss_NLDLY, __ss_CRDLY, __ss_TABDLY, __ss_BSDLY, __ss_VTDLY, __ss_FFDLY, __ss_NL0, __ss_NL1, __ss_CR0, __ss_CR1, __ss_CR2, __ss_CR3, __ss_TAB0, __ss_TAB1, __ss_TAB2, __ss_TAB3, __ss_XTABS, __ss_BS0, __ss_BS1, __ss_VT0, __ss_VT1, __ss_FF0, __ss_FF1, __ss_CSIZE, __ss_CS5, __ss_CS6, __ss_CS7, __ss_CS8, __ss_CSTOPB, __ss_CREAD, __ss_PARENB, __ss_PARODD, __ss_HUPCL, __ss_CLOCAL, __ss_CRTSCTS, __ss_CBAUD, __ss_CIBAUD, __ss_ISIG, __ss_ICANON, __ss_XCASE, __ss_ECHO, __ss_ECHOE, __ss_ECHOK, __ss_ECHONL, __ss_ECHOCTL, __ss_ECHOPRT, __ss_ECHOKE, __ss_FLUSHO, __ss_NOFLSH, __ss_TOSTOP, __ss_PENDIN, __ss_IEXTEN, __ss_EXTPROC, __ss_VINTR, __ss_VQUIT, __ss_VERASE, __ss_VKILL, __ss_VEOF, __ss_VTIME, __ss_VMIN, __ss_VSWTC, __ss_VSWTCH, __ss_VSTART, __ss_VSTOP, __ss_VSUSP, __ss_VEOL, __ss_VREPRINT, __ss_VDISCARD, __ss_VWERASE, __ss_VLNEXT, __ss_VEOL2, __ss_NCCS, __ss_B0, __ss_B50, __ss_B75, __ss_B110, __ss_B134, __ss_B150, __ss_B200, __ss_B300, __ss_B600, __ss_B1200, __ss_B1800, __ss_B2400, __ss_B4800, __ss_B9600, __ss_B19200, __ss_B38400, __ss_B57600, __ss_B115200, __ss_B230400, __ss_B460800, __ss_B500000, __ss_B576000, __ss_B921600, __ss_B1000000, __ss_B1152000, __ss_B1500000, __ss_B2000000, __ss_B2500000, __ss_B3000000, __ss_B3500000, __ss_B4000000;

extern class_ *cl_error;
class error : public Exception {
public:
    error(str *msg=0) : Exception(msg) {
        this->__class__ = cl_error;
    }
};

/* what tcgetattr returns: like cpython's list [iflag, oflag, cflag, lflag,
   ispeed, ospeed, cc], but with the items of cc as ints */
extern class_ *cl_TermAttributes;
class TermAttributes : public pyobj {
public:
    __ss_int iflag, oflag, cflag, lflag, ispeed, ospeed;
    list<__ss_int> *cc;

    TermAttributes();

    __ss_int __getitem__(__ss_int i);
    void *__setitem__(__ss_int i, __ss_int value);
    __ss_int __len__();
    __ss_bool __eq__(TermAttributes *other);
    TermAttributes *copy();
    str *__repr__();
};

TermAttributes *tcgetattr(__ss_int fd);
void *tcsetattr(__ss_int fd, __ss_int when, TermAttributes *attributes);
void *tcsendbreak(__ss_int fd, __ss_int duration);
void *tcdrain(__ss_int fd);
void *tcflush(__ss_int fd, __ss_int queue);
void *tcflow(__ss_int fd, __ss_int action);
tuple<__ss_int> *tcgetwinsize(__ss_int fd);
void *tcsetwinsize(__ss_int fd, tuple<__ss_int> *winsize);

void __init();

} // module namespace
#endif
