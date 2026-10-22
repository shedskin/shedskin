/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "termios.hpp"

#ifndef WIN32
#include <termios.h>
#include <sys/ioctl.h>
#include <unistd.h>
#endif

namespace __termios__ {

str *__name__;
__ss_int __ss_TCSANOW, __ss_TCSADRAIN, __ss_TCSAFLUSH, __ss_TCIFLUSH, __ss_TCOFLUSH, __ss_TCIOFLUSH, __ss_TCOOFF, __ss_TCOON, __ss_TCIOFF, __ss_TCION, __ss_IGNBRK, __ss_BRKINT, __ss_IGNPAR, __ss_PARMRK, __ss_INPCK, __ss_ISTRIP, __ss_INLCR, __ss_IGNCR, __ss_ICRNL, __ss_IUCLC, __ss_IXON, __ss_IXANY, __ss_IXOFF, __ss_IMAXBEL, __ss_IUTF8, __ss_OPOST, __ss_OLCUC, __ss_ONLCR, __ss_OCRNL, __ss_ONOCR, __ss_ONLRET, __ss_OFILL, __ss_OFDEL, __ss_NLDLY, __ss_CRDLY, __ss_TABDLY, __ss_BSDLY, __ss_VTDLY, __ss_FFDLY, __ss_NL0, __ss_NL1, __ss_CR0, __ss_CR1, __ss_CR2, __ss_CR3, __ss_TAB0, __ss_TAB1, __ss_TAB2, __ss_TAB3, __ss_XTABS, __ss_BS0, __ss_BS1, __ss_VT0, __ss_VT1, __ss_FF0, __ss_FF1, __ss_CSIZE, __ss_CS5, __ss_CS6, __ss_CS7, __ss_CS8, __ss_CSTOPB, __ss_CREAD, __ss_PARENB, __ss_PARODD, __ss_HUPCL, __ss_CLOCAL, __ss_CRTSCTS, __ss_CBAUD, __ss_CIBAUD, __ss_ISIG, __ss_ICANON, __ss_XCASE, __ss_ECHO, __ss_ECHOE, __ss_ECHOK, __ss_ECHONL, __ss_ECHOCTL, __ss_ECHOPRT, __ss_ECHOKE, __ss_FLUSHO, __ss_NOFLSH, __ss_TOSTOP, __ss_PENDIN, __ss_IEXTEN, __ss_EXTPROC, __ss_VINTR, __ss_VQUIT, __ss_VERASE, __ss_VKILL, __ss_VEOF, __ss_VTIME, __ss_VMIN, __ss_VSWTC, __ss_VSWTCH, __ss_VSTART, __ss_VSTOP, __ss_VSUSP, __ss_VEOL, __ss_VREPRINT, __ss_VDISCARD, __ss_VWERASE, __ss_VLNEXT, __ss_VEOL2, __ss_NCCS, __ss_B0, __ss_B50, __ss_B75, __ss_B110, __ss_B134, __ss_B150, __ss_B200, __ss_B300, __ss_B600, __ss_B1200, __ss_B1800, __ss_B2400, __ss_B4800, __ss_B9600, __ss_B19200, __ss_B38400, __ss_B57600, __ss_B115200, __ss_B230400, __ss_B460800, __ss_B500000, __ss_B576000, __ss_B921600, __ss_B1000000, __ss_B1152000, __ss_B1500000, __ss_B2000000, __ss_B2500000, __ss_B3000000, __ss_B3500000, __ss_B4000000;

class_ *cl_error, *cl_TermAttributes;

TermAttributes::TermAttributes() {
    this->__class__ = cl_TermAttributes;
    iflag = oflag = cflag = lflag = ispeed = ospeed = 0;
    cc = new list<__ss_int>();
}

__ss_int TermAttributes::__getitem__(__ss_int i) {
    if(i < 0)
        i += 7;
    switch(i) {
        case 0: return iflag;
        case 1: return oflag;
        case 2: return cflag;
        case 3: return lflag;
        case 4: return ispeed;
        case 5: return ospeed;
        case 6: throw new TypeError(new str("TermAttributes: use .cc for the control characters"));
    }
    throw new IndexError(new str("list index out of range"));
}

void *TermAttributes::__setitem__(__ss_int i, __ss_int value) {
    if(i < 0)
        i += 7;
    switch(i) {
        case 0: iflag = value; return NULL;
        case 1: oflag = value; return NULL;
        case 2: cflag = value; return NULL;
        case 3: lflag = value; return NULL;
        case 4: ispeed = value; return NULL;
        case 5: ospeed = value; return NULL;
        case 6: throw new TypeError(new str("TermAttributes: use .cc for the control characters"));
    }
    throw new IndexError(new str("list assignment index out of range"));
}

__ss_int TermAttributes::__len__() {
    return 7;
}

__ss_bool TermAttributes::__eq__(TermAttributes *other) {
    return __mbool(iflag == other->iflag && oflag == other->oflag && cflag == other->cflag &&
                   lflag == other->lflag && ispeed == other->ispeed && ospeed == other->ospeed &&
                   __eq(cc, other->cc));
}

TermAttributes *TermAttributes::copy() {
    TermAttributes *c = new TermAttributes();
    c->iflag = iflag; c->oflag = oflag; c->cflag = cflag; c->lflag = lflag;
    c->ispeed = ispeed; c->ospeed = ospeed;
    c->cc = new list<__ss_int>(cc);
    return c;
}

str *TermAttributes::__repr__() {
    return __mod6(new str("[%d, %d, %d, %d, %d, %d, %s]"), 7, iflag, oflag, cflag,
                  lflag, ispeed, ospeed, repr(cc));
}

#ifndef WIN32

/* like cpython: termios.error(errno, strerror) */
[[noreturn]] static void throw_error() {
    int e = errno;
    throw new error(__mod6(new str("(%d, '%s')"), 2, (__ss_int)e, new str(strerror(e))));
}

TermAttributes *tcgetattr(__ss_int fd) {
    struct termios mode;
    if(::tcgetattr((int)fd, &mode) == -1)
        throw_error();
    TermAttributes *t = new TermAttributes();
    t->iflag = mode.c_iflag;
    t->oflag = mode.c_oflag;
    t->cflag = mode.c_cflag;
    t->lflag = mode.c_lflag;
    t->ispeed = cfgetispeed(&mode);
    t->ospeed = cfgetospeed(&mode);
    for(int i = 0; i < NCCS; i++)
        t->cc->append(mode.c_cc[i]);
    return t;
}

void *tcsetattr(__ss_int fd, __ss_int when, TermAttributes *t) {
    if(len(t->cc) != NCCS)
        throw new TypeError(__mod6(new str("tcsetattr: attributes[6] must be %d element list"), 1, (__ss_int)NCCS));
    struct termios mode;
    /* like cpython: start from the current attributes, for any fields beyond posix */
    if(::tcgetattr((int)fd, &mode) == -1)
        throw_error();
    mode.c_iflag = (tcflag_t)t->iflag;
    mode.c_oflag = (tcflag_t)t->oflag;
    mode.c_cflag = (tcflag_t)t->cflag;
    mode.c_lflag = (tcflag_t)t->lflag;
    for(int i = 0; i < NCCS; i++)
        mode.c_cc[i] = (cc_t)t->cc->units[i];
    if(cfsetispeed(&mode, (speed_t)t->ispeed) == -1 || cfsetospeed(&mode, (speed_t)t->ospeed) == -1)
        throw_error();
    if(::tcsetattr((int)fd, (int)when, &mode) == -1)
        throw_error();
    return NULL;
}

void *tcsendbreak(__ss_int fd, __ss_int duration) {
    if(::tcsendbreak((int)fd, (int)duration) == -1)
        throw_error();
    return NULL;
}

void *tcdrain(__ss_int fd) {
    if(::tcdrain((int)fd) == -1)
        throw_error();
    return NULL;
}

void *tcflush(__ss_int fd, __ss_int queue) {
    if(::tcflush((int)fd, (int)queue) == -1)
        throw_error();
    return NULL;
}

void *tcflow(__ss_int fd, __ss_int action) {
    if(::tcflow((int)fd, (int)action) == -1)
        throw_error();
    return NULL;
}

tuple<__ss_int> *tcgetwinsize(__ss_int fd) {
    struct winsize w;
    if(ioctl((int)fd, TIOCGWINSZ, &w) == -1)
        throw_error();
    return new tuple<__ss_int>(2, (__ss_int)w.ws_row, (__ss_int)w.ws_col);
}

void *tcsetwinsize(__ss_int fd, tuple<__ss_int> *winsize) {
    if(len(winsize) != 2)
        throw new TypeError(new str("tcsetwinsize, arg 2: must be a two-item sequence"));
    struct winsize w;
    if(ioctl((int)fd, TIOCGWINSZ, &w) == -1)
        throw_error();
    w.ws_row = (unsigned short)winsize->__getitem__(0);
    w.ws_col = (unsigned short)winsize->__getitem__(1);
    if(ioctl((int)fd, TIOCSWINSZ, &w) == -1)
        throw_error();
    return NULL;
}

#else

[[noreturn]] static void unsupported() {
    throw new OSError(new str("termios is not available on windows"));
}
TermAttributes *tcgetattr(__ss_int) { unsupported(); }
void *tcsetattr(__ss_int, __ss_int, TermAttributes *) { unsupported(); }
void *tcsendbreak(__ss_int, __ss_int) { unsupported(); }
void *tcdrain(__ss_int) { unsupported(); }
void *tcflush(__ss_int, __ss_int) { unsupported(); }
void *tcflow(__ss_int, __ss_int) { unsupported(); }
tuple<__ss_int> *tcgetwinsize(__ss_int) { unsupported(); }
void *tcsetwinsize(__ss_int, tuple<__ss_int> *) { unsupported(); }

#endif

void __init() {
    __name__ = new str("termios");
    cl_error = new class_("error");
    cl_TermAttributes = new class_("TermAttributes");

#ifdef TCSANOW
    __ss_TCSANOW = TCSANOW;
#else
    __ss_TCSANOW = -1;
#endif
#ifdef TCSADRAIN
    __ss_TCSADRAIN = TCSADRAIN;
#else
    __ss_TCSADRAIN = -1;
#endif
#ifdef TCSAFLUSH
    __ss_TCSAFLUSH = TCSAFLUSH;
#else
    __ss_TCSAFLUSH = -1;
#endif
#ifdef TCIFLUSH
    __ss_TCIFLUSH = TCIFLUSH;
#else
    __ss_TCIFLUSH = -1;
#endif
#ifdef TCOFLUSH
    __ss_TCOFLUSH = TCOFLUSH;
#else
    __ss_TCOFLUSH = -1;
#endif
#ifdef TCIOFLUSH
    __ss_TCIOFLUSH = TCIOFLUSH;
#else
    __ss_TCIOFLUSH = -1;
#endif
#ifdef TCOOFF
    __ss_TCOOFF = TCOOFF;
#else
    __ss_TCOOFF = -1;
#endif
#ifdef TCOON
    __ss_TCOON = TCOON;
#else
    __ss_TCOON = -1;
#endif
#ifdef TCIOFF
    __ss_TCIOFF = TCIOFF;
#else
    __ss_TCIOFF = -1;
#endif
#ifdef TCION
    __ss_TCION = TCION;
#else
    __ss_TCION = -1;
#endif
#ifdef IGNBRK
    __ss_IGNBRK = IGNBRK;
#else
    __ss_IGNBRK = -1;
#endif
#ifdef BRKINT
    __ss_BRKINT = BRKINT;
#else
    __ss_BRKINT = -1;
#endif
#ifdef IGNPAR
    __ss_IGNPAR = IGNPAR;
#else
    __ss_IGNPAR = -1;
#endif
#ifdef PARMRK
    __ss_PARMRK = PARMRK;
#else
    __ss_PARMRK = -1;
#endif
#ifdef INPCK
    __ss_INPCK = INPCK;
#else
    __ss_INPCK = -1;
#endif
#ifdef ISTRIP
    __ss_ISTRIP = ISTRIP;
#else
    __ss_ISTRIP = -1;
#endif
#ifdef INLCR
    __ss_INLCR = INLCR;
#else
    __ss_INLCR = -1;
#endif
#ifdef IGNCR
    __ss_IGNCR = IGNCR;
#else
    __ss_IGNCR = -1;
#endif
#ifdef ICRNL
    __ss_ICRNL = ICRNL;
#else
    __ss_ICRNL = -1;
#endif
#ifdef IUCLC
    __ss_IUCLC = IUCLC;
#else
    __ss_IUCLC = -1;
#endif
#ifdef IXON
    __ss_IXON = IXON;
#else
    __ss_IXON = -1;
#endif
#ifdef IXANY
    __ss_IXANY = IXANY;
#else
    __ss_IXANY = -1;
#endif
#ifdef IXOFF
    __ss_IXOFF = IXOFF;
#else
    __ss_IXOFF = -1;
#endif
#ifdef IMAXBEL
    __ss_IMAXBEL = IMAXBEL;
#else
    __ss_IMAXBEL = -1;
#endif
#ifdef IUTF8
    __ss_IUTF8 = IUTF8;
#else
    __ss_IUTF8 = -1;
#endif
#ifdef OPOST
    __ss_OPOST = OPOST;
#else
    __ss_OPOST = -1;
#endif
#ifdef OLCUC
    __ss_OLCUC = OLCUC;
#else
    __ss_OLCUC = -1;
#endif
#ifdef ONLCR
    __ss_ONLCR = ONLCR;
#else
    __ss_ONLCR = -1;
#endif
#ifdef OCRNL
    __ss_OCRNL = OCRNL;
#else
    __ss_OCRNL = -1;
#endif
#ifdef ONOCR
    __ss_ONOCR = ONOCR;
#else
    __ss_ONOCR = -1;
#endif
#ifdef ONLRET
    __ss_ONLRET = ONLRET;
#else
    __ss_ONLRET = -1;
#endif
#ifdef OFILL
    __ss_OFILL = OFILL;
#else
    __ss_OFILL = -1;
#endif
#ifdef OFDEL
    __ss_OFDEL = OFDEL;
#else
    __ss_OFDEL = -1;
#endif
#ifdef NLDLY
    __ss_NLDLY = NLDLY;
#else
    __ss_NLDLY = -1;
#endif
#ifdef CRDLY
    __ss_CRDLY = CRDLY;
#else
    __ss_CRDLY = -1;
#endif
#ifdef TABDLY
    __ss_TABDLY = TABDLY;
#else
    __ss_TABDLY = -1;
#endif
#ifdef BSDLY
    __ss_BSDLY = BSDLY;
#else
    __ss_BSDLY = -1;
#endif
#ifdef VTDLY
    __ss_VTDLY = VTDLY;
#else
    __ss_VTDLY = -1;
#endif
#ifdef FFDLY
    __ss_FFDLY = FFDLY;
#else
    __ss_FFDLY = -1;
#endif
#ifdef NL0
    __ss_NL0 = NL0;
#else
    __ss_NL0 = -1;
#endif
#ifdef NL1
    __ss_NL1 = NL1;
#else
    __ss_NL1 = -1;
#endif
#ifdef CR0
    __ss_CR0 = CR0;
#else
    __ss_CR0 = -1;
#endif
#ifdef CR1
    __ss_CR1 = CR1;
#else
    __ss_CR1 = -1;
#endif
#ifdef CR2
    __ss_CR2 = CR2;
#else
    __ss_CR2 = -1;
#endif
#ifdef CR3
    __ss_CR3 = CR3;
#else
    __ss_CR3 = -1;
#endif
#ifdef TAB0
    __ss_TAB0 = TAB0;
#else
    __ss_TAB0 = -1;
#endif
#ifdef TAB1
    __ss_TAB1 = TAB1;
#else
    __ss_TAB1 = -1;
#endif
#ifdef TAB2
    __ss_TAB2 = TAB2;
#else
    __ss_TAB2 = -1;
#endif
#ifdef TAB3
    __ss_TAB3 = TAB3;
#else
    __ss_TAB3 = -1;
#endif
#ifdef XTABS
    __ss_XTABS = XTABS;
#else
    __ss_XTABS = -1;
#endif
#ifdef BS0
    __ss_BS0 = BS0;
#else
    __ss_BS0 = -1;
#endif
#ifdef BS1
    __ss_BS1 = BS1;
#else
    __ss_BS1 = -1;
#endif
#ifdef VT0
    __ss_VT0 = VT0;
#else
    __ss_VT0 = -1;
#endif
#ifdef VT1
    __ss_VT1 = VT1;
#else
    __ss_VT1 = -1;
#endif
#ifdef FF0
    __ss_FF0 = FF0;
#else
    __ss_FF0 = -1;
#endif
#ifdef FF1
    __ss_FF1 = FF1;
#else
    __ss_FF1 = -1;
#endif
#ifdef CSIZE
    __ss_CSIZE = CSIZE;
#else
    __ss_CSIZE = -1;
#endif
#ifdef CS5
    __ss_CS5 = CS5;
#else
    __ss_CS5 = -1;
#endif
#ifdef CS6
    __ss_CS6 = CS6;
#else
    __ss_CS6 = -1;
#endif
#ifdef CS7
    __ss_CS7 = CS7;
#else
    __ss_CS7 = -1;
#endif
#ifdef CS8
    __ss_CS8 = CS8;
#else
    __ss_CS8 = -1;
#endif
#ifdef CSTOPB
    __ss_CSTOPB = CSTOPB;
#else
    __ss_CSTOPB = -1;
#endif
#ifdef CREAD
    __ss_CREAD = CREAD;
#else
    __ss_CREAD = -1;
#endif
#ifdef PARENB
    __ss_PARENB = PARENB;
#else
    __ss_PARENB = -1;
#endif
#ifdef PARODD
    __ss_PARODD = PARODD;
#else
    __ss_PARODD = -1;
#endif
#ifdef HUPCL
    __ss_HUPCL = HUPCL;
#else
    __ss_HUPCL = -1;
#endif
#ifdef CLOCAL
    __ss_CLOCAL = CLOCAL;
#else
    __ss_CLOCAL = -1;
#endif
#ifdef CRTSCTS
    __ss_CRTSCTS = CRTSCTS;
#else
    __ss_CRTSCTS = -1;
#endif
#ifdef CBAUD
    __ss_CBAUD = CBAUD;
#else
    __ss_CBAUD = -1;
#endif
#ifdef CIBAUD
    __ss_CIBAUD = CIBAUD;
#else
    __ss_CIBAUD = -1;
#endif
#ifdef ISIG
    __ss_ISIG = ISIG;
#else
    __ss_ISIG = -1;
#endif
#ifdef ICANON
    __ss_ICANON = ICANON;
#else
    __ss_ICANON = -1;
#endif
#ifdef XCASE
    __ss_XCASE = XCASE;
#else
    __ss_XCASE = -1;
#endif
#ifdef ECHO
    __ss_ECHO = ECHO;
#else
    __ss_ECHO = -1;
#endif
#ifdef ECHOE
    __ss_ECHOE = ECHOE;
#else
    __ss_ECHOE = -1;
#endif
#ifdef ECHOK
    __ss_ECHOK = ECHOK;
#else
    __ss_ECHOK = -1;
#endif
#ifdef ECHONL
    __ss_ECHONL = ECHONL;
#else
    __ss_ECHONL = -1;
#endif
#ifdef ECHOCTL
    __ss_ECHOCTL = ECHOCTL;
#else
    __ss_ECHOCTL = -1;
#endif
#ifdef ECHOPRT
    __ss_ECHOPRT = ECHOPRT;
#else
    __ss_ECHOPRT = -1;
#endif
#ifdef ECHOKE
    __ss_ECHOKE = ECHOKE;
#else
    __ss_ECHOKE = -1;
#endif
#ifdef FLUSHO
    __ss_FLUSHO = FLUSHO;
#else
    __ss_FLUSHO = -1;
#endif
#ifdef NOFLSH
    __ss_NOFLSH = NOFLSH;
#else
    __ss_NOFLSH = -1;
#endif
#ifdef TOSTOP
    __ss_TOSTOP = TOSTOP;
#else
    __ss_TOSTOP = -1;
#endif
#ifdef PENDIN
    __ss_PENDIN = PENDIN;
#else
    __ss_PENDIN = -1;
#endif
#ifdef IEXTEN
    __ss_IEXTEN = IEXTEN;
#else
    __ss_IEXTEN = -1;
#endif
#ifdef EXTPROC
    __ss_EXTPROC = EXTPROC;
#else
    __ss_EXTPROC = -1;
#endif
#ifdef VINTR
    __ss_VINTR = VINTR;
#else
    __ss_VINTR = -1;
#endif
#ifdef VQUIT
    __ss_VQUIT = VQUIT;
#else
    __ss_VQUIT = -1;
#endif
#ifdef VERASE
    __ss_VERASE = VERASE;
#else
    __ss_VERASE = -1;
#endif
#ifdef VKILL
    __ss_VKILL = VKILL;
#else
    __ss_VKILL = -1;
#endif
#ifdef VEOF
    __ss_VEOF = VEOF;
#else
    __ss_VEOF = -1;
#endif
#ifdef VTIME
    __ss_VTIME = VTIME;
#else
    __ss_VTIME = -1;
#endif
#ifdef VMIN
    __ss_VMIN = VMIN;
#else
    __ss_VMIN = -1;
#endif
#ifdef VSWTC
    __ss_VSWTC = VSWTC;
#else
    __ss_VSWTC = -1;
#endif
#ifdef VSWTCH
    __ss_VSWTCH = VSWTCH;
#else
    __ss_VSWTCH = -1;
#endif
#ifdef VSTART
    __ss_VSTART = VSTART;
#else
    __ss_VSTART = -1;
#endif
#ifdef VSTOP
    __ss_VSTOP = VSTOP;
#else
    __ss_VSTOP = -1;
#endif
#ifdef VSUSP
    __ss_VSUSP = VSUSP;
#else
    __ss_VSUSP = -1;
#endif
#ifdef VEOL
    __ss_VEOL = VEOL;
#else
    __ss_VEOL = -1;
#endif
#ifdef VREPRINT
    __ss_VREPRINT = VREPRINT;
#else
    __ss_VREPRINT = -1;
#endif
#ifdef VDISCARD
    __ss_VDISCARD = VDISCARD;
#else
    __ss_VDISCARD = -1;
#endif
#ifdef VWERASE
    __ss_VWERASE = VWERASE;
#else
    __ss_VWERASE = -1;
#endif
#ifdef VLNEXT
    __ss_VLNEXT = VLNEXT;
#else
    __ss_VLNEXT = -1;
#endif
#ifdef VEOL2
    __ss_VEOL2 = VEOL2;
#else
    __ss_VEOL2 = -1;
#endif
#ifdef NCCS
    __ss_NCCS = NCCS;
#else
    __ss_NCCS = -1;
#endif
#ifdef B0
    __ss_B0 = B0;
#else
    __ss_B0 = -1;
#endif
#ifdef B50
    __ss_B50 = B50;
#else
    __ss_B50 = -1;
#endif
#ifdef B75
    __ss_B75 = B75;
#else
    __ss_B75 = -1;
#endif
#ifdef B110
    __ss_B110 = B110;
#else
    __ss_B110 = -1;
#endif
#ifdef B134
    __ss_B134 = B134;
#else
    __ss_B134 = -1;
#endif
#ifdef B150
    __ss_B150 = B150;
#else
    __ss_B150 = -1;
#endif
#ifdef B200
    __ss_B200 = B200;
#else
    __ss_B200 = -1;
#endif
#ifdef B300
    __ss_B300 = B300;
#else
    __ss_B300 = -1;
#endif
#ifdef B600
    __ss_B600 = B600;
#else
    __ss_B600 = -1;
#endif
#ifdef B1200
    __ss_B1200 = B1200;
#else
    __ss_B1200 = -1;
#endif
#ifdef B1800
    __ss_B1800 = B1800;
#else
    __ss_B1800 = -1;
#endif
#ifdef B2400
    __ss_B2400 = B2400;
#else
    __ss_B2400 = -1;
#endif
#ifdef B4800
    __ss_B4800 = B4800;
#else
    __ss_B4800 = -1;
#endif
#ifdef B9600
    __ss_B9600 = B9600;
#else
    __ss_B9600 = -1;
#endif
#ifdef B19200
    __ss_B19200 = B19200;
#else
    __ss_B19200 = -1;
#endif
#ifdef B38400
    __ss_B38400 = B38400;
#else
    __ss_B38400 = -1;
#endif
#ifdef B57600
    __ss_B57600 = B57600;
#else
    __ss_B57600 = -1;
#endif
#ifdef B115200
    __ss_B115200 = B115200;
#else
    __ss_B115200 = -1;
#endif
#ifdef B230400
    __ss_B230400 = B230400;
#else
    __ss_B230400 = -1;
#endif
#ifdef B460800
    __ss_B460800 = B460800;
#else
    __ss_B460800 = -1;
#endif
#ifdef B500000
    __ss_B500000 = B500000;
#else
    __ss_B500000 = -1;
#endif
#ifdef B576000
    __ss_B576000 = B576000;
#else
    __ss_B576000 = -1;
#endif
#ifdef B921600
    __ss_B921600 = B921600;
#else
    __ss_B921600 = -1;
#endif
#ifdef B1000000
    __ss_B1000000 = B1000000;
#else
    __ss_B1000000 = -1;
#endif
#ifdef B1152000
    __ss_B1152000 = B1152000;
#else
    __ss_B1152000 = -1;
#endif
#ifdef B1500000
    __ss_B1500000 = B1500000;
#else
    __ss_B1500000 = -1;
#endif
#ifdef B2000000
    __ss_B2000000 = B2000000;
#else
    __ss_B2000000 = -1;
#endif
#ifdef B2500000
    __ss_B2500000 = B2500000;
#else
    __ss_B2500000 = -1;
#endif
#ifdef B3000000
    __ss_B3000000 = B3000000;
#else
    __ss_B3000000 = -1;
#endif
#ifdef B3500000
    __ss_B3500000 = B3500000;
#else
    __ss_B3500000 = -1;
#endif
#ifdef B4000000
    __ss_B4000000 = B4000000;
#else
    __ss_B4000000 = -1;
#endif
}

} // module namespace
