/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "termios.hpp"

#include <errno.h>
#include <string.h>
#include <limits.h>

namespace __termios__ {

str *__name__;
class_ *cl_error, *cl_cclist, *cl_tcattrs;

__ss_int __ss_B0, __ss_B1000000, __ss_B110, __ss_B115200, __ss_B1152000, __ss_B1200, __ss_B134,
    __ss_B150, __ss_B1500000, __ss_B1800, __ss_B19200, __ss_B200, __ss_B2000000, __ss_B230400,
    __ss_B2400, __ss_B2500000, __ss_B300, __ss_B3000000, __ss_B3500000, __ss_B38400, __ss_B4000000,
    __ss_B460800, __ss_B4800, __ss_B50, __ss_B500000, __ss_B57600, __ss_B576000, __ss_B600,
    __ss_B75, __ss_B921600, __ss_B9600, __ss_BRKINT, __ss_BS0, __ss_BS1, __ss_BSDLY, __ss_CBAUD,
    __ss_CBAUDEX, __ss_CDSUSP, __ss_CEOF, __ss_CEOL, __ss_CEOT, __ss_CERASE, __ss_CFLUSH,
    __ss_CIBAUD, __ss_CINTR, __ss_CKILL, __ss_CLNEXT, __ss_CLOCAL, __ss_CQUIT, __ss_CR0, __ss_CR1,
    __ss_CR2, __ss_CR3, __ss_CRDLY, __ss_CREAD, __ss_CRPRNT, __ss_CRTSCTS, __ss_CS5, __ss_CS6,
    __ss_CS7, __ss_CS8, __ss_CSIZE, __ss_CSTART, __ss_CSTOP, __ss_CSTOPB, __ss_CSUSP, __ss_CWERASE,
    __ss_ECHO, __ss_ECHOCTL, __ss_ECHOE, __ss_ECHOK, __ss_ECHOKE, __ss_ECHONL, __ss_ECHOPRT,
    __ss_EXTA, __ss_EXTB, __ss_EXTPROC, __ss_FF0, __ss_FF1, __ss_FFDLY, __ss_FIOASYNC, __ss_FIOCLEX,
    __ss_FIONBIO, __ss_FIONCLEX, __ss_FIONREAD, __ss_FLUSHO, __ss_HUPCL, __ss_ICANON, __ss_ICRNL,
    __ss_IEXTEN, __ss_IGNBRK, __ss_IGNCR, __ss_IGNPAR, __ss_IMAXBEL, __ss_INLCR, __ss_INPCK,
    __ss_IOCSIZE_MASK, __ss_IOCSIZE_SHIFT, __ss_ISIG, __ss_ISTRIP, __ss_IUCLC, __ss_IUTF8,
    __ss_IXANY, __ss_IXOFF, __ss_IXON, __ss_NCC, __ss_NCCS, __ss_NL0, __ss_NL1, __ss_NLDLY,
    __ss_NOFLSH, __ss_N_MOUSE, __ss_N_PPP, __ss_N_SLIP, __ss_N_STRIP, __ss_N_TTY, __ss_OCRNL,
    __ss_OFDEL, __ss_OFILL, __ss_OLCUC, __ss_ONLCR, __ss_ONLRET, __ss_ONOCR, __ss_OPOST,
    __ss_PARENB, __ss_PARMRK, __ss_PARODD, __ss_PENDIN, __ss_TAB0, __ss_TAB1, __ss_TAB2, __ss_TAB3,
    __ss_TABDLY, __ss_TCFLSH, __ss_TCGETA, __ss_TCGETS, __ss_TCIFLUSH, __ss_TCIOFF, __ss_TCIOFLUSH,
    __ss_TCION, __ss_TCOFLUSH, __ss_TCOOFF, __ss_TCOON, __ss_TCSADRAIN, __ss_TCSAFLUSH,
    __ss_TCSANOW, __ss_TCSBRK, __ss_TCSBRKP, __ss_TCSETA, __ss_TCSETAF, __ss_TCSETAW, __ss_TCSETS,
    __ss_TCSETSF, __ss_TCSETSW, __ss_TCXONC, __ss_TIOCCONS, __ss_TIOCEXCL, __ss_TIOCGETD,
    __ss_TIOCGICOUNT, __ss_TIOCGLCKTRMIOS, __ss_TIOCGPGRP, __ss_TIOCGSERIAL, __ss_TIOCGSOFTCAR,
    __ss_TIOCGWINSZ, __ss_TIOCINQ, __ss_TIOCLINUX, __ss_TIOCMBIC, __ss_TIOCMBIS, __ss_TIOCMGET,
    __ss_TIOCMIWAIT, __ss_TIOCMSET, __ss_TIOCM_CAR, __ss_TIOCM_CD, __ss_TIOCM_CTS, __ss_TIOCM_DSR,
    __ss_TIOCM_DTR, __ss_TIOCM_LE, __ss_TIOCM_RI, __ss_TIOCM_RNG, __ss_TIOCM_RTS, __ss_TIOCM_SR,
    __ss_TIOCM_ST, __ss_TIOCNOTTY, __ss_TIOCNXCL, __ss_TIOCOUTQ, __ss_TIOCPKT, __ss_TIOCPKT_DATA,
    __ss_TIOCPKT_DOSTOP, __ss_TIOCPKT_FLUSHREAD, __ss_TIOCPKT_FLUSHWRITE, __ss_TIOCPKT_NOSTOP,
    __ss_TIOCPKT_START, __ss_TIOCPKT_STOP, __ss_TIOCSCTTY, __ss_TIOCSERCONFIG, __ss_TIOCSERGETLSR,
    __ss_TIOCSERGETMULTI, __ss_TIOCSERGSTRUCT, __ss_TIOCSERGWILD, __ss_TIOCSERSETMULTI,
    __ss_TIOCSERSWILD, __ss_TIOCSER_TEMT, __ss_TIOCSETD, __ss_TIOCSLCKTRMIOS, __ss_TIOCSPGRP,
    __ss_TIOCSSERIAL, __ss_TIOCSSOFTCAR, __ss_TIOCSTI, __ss_TIOCSWINSZ, __ss_TOSTOP, __ss_VDISCARD,
    __ss_VEOF, __ss_VEOL, __ss_VEOL2, __ss_VERASE, __ss_VINTR, __ss_VKILL, __ss_VLNEXT, __ss_VMIN,
    __ss_VQUIT, __ss_VREPRINT, __ss_VSTART, __ss_VSTOP, __ss_VSUSP, __ss_VSWTC, __ss_VSWTCH,
    __ss_VT0, __ss_VT1, __ss_VTDLY, __ss_VTIME, __ss_VWERASE, __ss_XCASE, __ss_XTABS,
    __ss__POSIX_VDISABLE;

/* like CPython, str(error) is '(errno, strerror)' */
static void __throw_error() {
    int e = errno;
    throw new error(__add_strs(5, new str("("), __str(e), new str(", "), repr(new str(strerror(e))), new str(")")));
}

/* cclist */

__ss_int cclist::__len__() {
    return NCCS;
}

bytes *cclist::__getitem__(__ss_int i) {
    i = __wrap(this, i, "list index out of range");
    return __byte_cache[cc[i]];
}

void *cclist::__setitem__(__ss_int i, __ss_int v) {
    i = __wrap(this, i, "list assignment index out of range");
    cc[i] = (cc_t)v; /* like CPython: no range check */
    return NULL;
}

void *cclist::__setitem__(__ss_int i, bytes *v) {
    i = __wrap(this, i, "list assignment index out of range");
    if(v->__len__() != 1)
        throw new TypeError(new str("tcsetattr: elements of attributes must be characters or integers"));
    cc[i] = (cc_t)v->unit[0];
    return NULL;
}

__ss_bool cclist::__eq__(pyobj *p) {
    if(!p || p->__class__ != cl_cclist)
        return False;
    return __mbool(memcmp(cc, ((cclist *)p)->cc, sizeof(cc)) == 0);
}

__ss_bool cclist::__ne__(pyobj *p) {
    return __mbool(!__eq__(p));
}

str *cclist::__repr__() {
    str *r = new str("[");
    for(int i = 0; i < NCCS; i++) {
        if(i)
            r = r->__add__(new str(", "));
        r = r->__add__(repr(__byte_cache[cc[i]]));
    }
    return r->__add__(new str("]"));
}

cclist *cclist::__copy__() {
    cclist *c = new cclist();
    memcpy(c->cc, cc, sizeof(cc));
    return c;
}

cclist *cclist::__deepcopy__(dict<void *, pyobj *> *memo) {
    cclist *c = __copy__();
    memo->__setitem__(this, c);
    return c;
}

/* tcattrs */

__ss_int tcattrs::__len__() {
    return 7;
}

__ss_int tcattrs::__getitem__(__ss_int i) {
    i = __wrap(this, i, "list index out of range");
    if(i == 6)
        throw new TypeError(new str("termios attributes: index 6 holds the control characters; use a literal 6, CC or tty.CC as index"));
    return flags[i];
}

cclist *tcattrs::__getcc__() {
    return cc;
}

void *tcattrs::__setitem__(__ss_int i, __ss_int v) {
    i = __wrap(this, i, "list assignment index out of range");
    if(i == 6)
        throw new TypeError(new str("termios attributes: index 6 holds the control characters"));
    flags[i] = v;
    return NULL;
}

void *tcattrs::__setitem__(__ss_int i, cclist *v) {
    i = __wrap(this, i, "list assignment index out of range");
    if(i != 6)
        throw new TypeError(new str("termios attributes: only index 6 holds the control characters"));
    cc = v;
    return NULL;
}

__ss_bool tcattrs::__eq__(pyobj *p) {
    if(!p || p->__class__ != cl_tcattrs)
        return False;
    tcattrs *b = (tcattrs *)p;
    for(int i = 0; i < 6; i++)
        if(flags[i] != b->flags[i])
            return False;
    return cc->__eq__(b->cc);
}

__ss_bool tcattrs::__ne__(pyobj *p) {
    return __mbool(!__eq__(p));
}

str *tcattrs::__repr__() {
    str *r = new str("[");
    for(int i = 0; i < 6; i++)
        r = r->__add__(__str(flags[i]))->__add__(new str(", "));
    return r->__add__(repr(cc))->__add__(new str("]"));
}

tcattrs *tcattrs::__copy__() {
    tcattrs *c = new tcattrs();
    memcpy(c->flags, flags, sizeof(flags));
    c->cc = cc; /* shallow, like copy.copy of a CPython list */
    return c;
}

tcattrs *tcattrs::__deepcopy__(dict<void *, pyobj *> *memo) {
    tcattrs *c = new tcattrs();
    memo->__setitem__(this, c);
    memcpy(c->flags, flags, sizeof(flags));
    c->cc = __deepcopy(cc, memo);
    return c;
}

/* functions */

tcattrs *__tcgetattr(int fd) {
    struct termios mode;
    if(::tcgetattr(fd, &mode) == -1)
        __throw_error();
    tcattrs *a = new tcattrs();
    a->flags[0] = (__ss_int)mode.c_iflag;
    a->flags[1] = (__ss_int)mode.c_oflag;
    a->flags[2] = (__ss_int)mode.c_cflag;
    a->flags[3] = (__ss_int)mode.c_lflag;
    a->flags[4] = (__ss_int)cfgetispeed(&mode);
    a->flags[5] = (__ss_int)cfgetospeed(&mode);
    memcpy(a->cc->cc, mode.c_cc, sizeof(mode.c_cc));
    return a;
}

void *__tcsetattr(int fd, __ss_int when, tcattrs *attributes) {
    struct termios mode;
    if(::tcgetattr(fd, &mode) == -1) /* fill in fields we don't expose */
        __throw_error();
    mode.c_iflag = (tcflag_t)attributes->flags[0];
    mode.c_oflag = (tcflag_t)attributes->flags[1];
    mode.c_cflag = (tcflag_t)attributes->flags[2];
    mode.c_lflag = (tcflag_t)attributes->flags[3];
    memcpy(mode.c_cc, attributes->cc->cc, sizeof(mode.c_cc));
    if(cfsetispeed(&mode, (speed_t)attributes->flags[4]) == -1)
        __throw_error();
    if(cfsetospeed(&mode, (speed_t)attributes->flags[5]) == -1)
        __throw_error();
    if(::tcsetattr(fd, (int)when, &mode) == -1)
        __throw_error();
    return NULL;
}

void *__tcsendbreak(int fd, __ss_int duration) {
    if(::tcsendbreak(fd, (int)duration) == -1)
        __throw_error();
    return NULL;
}

void *__tcdrain(int fd) {
    if(::tcdrain(fd) == -1)
        __throw_error();
    return NULL;
}

void *__tcflush(int fd, __ss_int queue) {
    if(::tcflush(fd, (int)queue) == -1)
        __throw_error();
    return NULL;
}

void *__tcflow(int fd, __ss_int action) {
    if(::tcflow(fd, (int)action) == -1)
        __throw_error();
    return NULL;
}

tuple<__ss_int> *__tcgetwinsize(int fd) {
    struct winsize w;
    if(ioctl(fd, TIOCGWINSZ, &w) == -1)
        __throw_error();
    return new tuple<__ss_int>(2, (__ss_int)w.ws_row, (__ss_int)w.ws_col);
}

void *__tcsetwinsize(int fd, __ss_int rows, __ss_int cols) {
    struct winsize w;
    if(ioctl(fd, TIOCGWINSZ, &w) == -1) /* keep ws_xpixel, ws_ypixel */
        __throw_error();
    if(rows < 0 || rows > USHRT_MAX || cols < 0 || cols > USHRT_MAX)
        throw new OverflowError(new str("winsize value(s) out of range."));
    w.ws_row = (unsigned short)rows;
    w.ws_col = (unsigned short)cols;
    if(ioctl(fd, TIOCSWINSZ, &w) == -1)
        __throw_error();
    return NULL;
}

void __init() {
    __name__ = new str("termios");
    cl_error = new class_("error");
    cl_cclist = new class_("list");
    cl_tcattrs = new class_("list");

    /* constants that the platform does not define are left at -1 */
    __ss_B0 = __ss_B1000000 = __ss_B110 = __ss_B115200 = __ss_B1152000 = __ss_B1200 = __ss_B134 =
        __ss_B150 = __ss_B1500000 = __ss_B1800 = __ss_B19200 = __ss_B200 = __ss_B2000000 =
        __ss_B230400 = __ss_B2400 = __ss_B2500000 = __ss_B300 = __ss_B3000000 = __ss_B3500000 =
        __ss_B38400 = __ss_B4000000 = __ss_B460800 = __ss_B4800 = __ss_B50 = __ss_B500000 =
        __ss_B57600 = __ss_B576000 = __ss_B600 = __ss_B75 = __ss_B921600 = __ss_B9600 =
        __ss_BRKINT = __ss_BS0 = __ss_BS1 = __ss_BSDLY = __ss_CBAUD = __ss_CBAUDEX = __ss_CDSUSP =
        __ss_CEOF = __ss_CEOL = __ss_CEOT = __ss_CERASE = __ss_CFLUSH = __ss_CIBAUD = __ss_CINTR =
        __ss_CKILL = __ss_CLNEXT = __ss_CLOCAL = __ss_CQUIT = __ss_CR0 = __ss_CR1 = __ss_CR2 =
        __ss_CR3 = __ss_CRDLY = __ss_CREAD = __ss_CRPRNT = __ss_CRTSCTS = __ss_CS5 = __ss_CS6 =
        __ss_CS7 = __ss_CS8 = __ss_CSIZE = __ss_CSTART = __ss_CSTOP = __ss_CSTOPB = __ss_CSUSP =
        __ss_CWERASE = __ss_ECHO = __ss_ECHOCTL = __ss_ECHOE = __ss_ECHOK = __ss_ECHOKE =
        __ss_ECHONL = __ss_ECHOPRT = __ss_EXTA = __ss_EXTB = __ss_EXTPROC = __ss_FF0 = __ss_FF1 =
        __ss_FFDLY = __ss_FIOASYNC = __ss_FIOCLEX = __ss_FIONBIO = __ss_FIONCLEX = __ss_FIONREAD =
        __ss_FLUSHO = __ss_HUPCL = __ss_ICANON = __ss_ICRNL = __ss_IEXTEN = __ss_IGNBRK =
        __ss_IGNCR = __ss_IGNPAR = __ss_IMAXBEL = __ss_INLCR = __ss_INPCK = __ss_IOCSIZE_MASK =
        __ss_IOCSIZE_SHIFT = __ss_ISIG = __ss_ISTRIP = __ss_IUCLC = __ss_IUTF8 = __ss_IXANY =
        __ss_IXOFF = __ss_IXON = __ss_NCC = __ss_NCCS = __ss_NL0 = __ss_NL1 = __ss_NLDLY =
        __ss_NOFLSH = __ss_N_MOUSE = __ss_N_PPP = __ss_N_SLIP = __ss_N_STRIP = __ss_N_TTY =
        __ss_OCRNL = __ss_OFDEL = __ss_OFILL = __ss_OLCUC = __ss_ONLCR = __ss_ONLRET = __ss_ONOCR =
        __ss_OPOST = __ss_PARENB = __ss_PARMRK = __ss_PARODD = __ss_PENDIN = __ss_TAB0 = __ss_TAB1 =
        __ss_TAB2 = __ss_TAB3 = __ss_TABDLY = __ss_TCFLSH = __ss_TCGETA = __ss_TCGETS =
        __ss_TCIFLUSH = __ss_TCIOFF = __ss_TCIOFLUSH = __ss_TCION = __ss_TCOFLUSH = __ss_TCOOFF =
        __ss_TCOON = __ss_TCSADRAIN = __ss_TCSAFLUSH = __ss_TCSANOW = __ss_TCSBRK = __ss_TCSBRKP =
        __ss_TCSETA = __ss_TCSETAF = __ss_TCSETAW = __ss_TCSETS = __ss_TCSETSF = __ss_TCSETSW =
        __ss_TCXONC = __ss_TIOCCONS = __ss_TIOCEXCL = __ss_TIOCGETD = __ss_TIOCGICOUNT =
        __ss_TIOCGLCKTRMIOS = __ss_TIOCGPGRP = __ss_TIOCGSERIAL = __ss_TIOCGSOFTCAR =
        __ss_TIOCGWINSZ = __ss_TIOCINQ = __ss_TIOCLINUX = __ss_TIOCMBIC = __ss_TIOCMBIS =
        __ss_TIOCMGET = __ss_TIOCMIWAIT = __ss_TIOCMSET = __ss_TIOCM_CAR = __ss_TIOCM_CD =
        __ss_TIOCM_CTS = __ss_TIOCM_DSR = __ss_TIOCM_DTR = __ss_TIOCM_LE = __ss_TIOCM_RI =
        __ss_TIOCM_RNG = __ss_TIOCM_RTS = __ss_TIOCM_SR = __ss_TIOCM_ST = __ss_TIOCNOTTY =
        __ss_TIOCNXCL = __ss_TIOCOUTQ = __ss_TIOCPKT = __ss_TIOCPKT_DATA = __ss_TIOCPKT_DOSTOP =
        __ss_TIOCPKT_FLUSHREAD = __ss_TIOCPKT_FLUSHWRITE = __ss_TIOCPKT_NOSTOP =
        __ss_TIOCPKT_START = __ss_TIOCPKT_STOP = __ss_TIOCSCTTY = __ss_TIOCSERCONFIG =
        __ss_TIOCSERGETLSR = __ss_TIOCSERGETMULTI = __ss_TIOCSERGSTRUCT = __ss_TIOCSERGWILD =
        __ss_TIOCSERSETMULTI = __ss_TIOCSERSWILD = __ss_TIOCSER_TEMT = __ss_TIOCSETD =
        __ss_TIOCSLCKTRMIOS = __ss_TIOCSPGRP = __ss_TIOCSSERIAL = __ss_TIOCSSOFTCAR = __ss_TIOCSTI =
        __ss_TIOCSWINSZ = __ss_TOSTOP = __ss_VDISCARD = __ss_VEOF = __ss_VEOL = __ss_VEOL2 =
        __ss_VERASE = __ss_VINTR = __ss_VKILL = __ss_VLNEXT = __ss_VMIN = __ss_VQUIT =
        __ss_VREPRINT = __ss_VSTART = __ss_VSTOP = __ss_VSUSP = __ss_VSWTC = __ss_VSWTCH =
        __ss_VT0 = __ss_VT1 = __ss_VTDLY = __ss_VTIME = __ss_VWERASE = __ss_XCASE = __ss_XTABS =
        __ss__POSIX_VDISABLE = -1;

#ifdef B0
    __ss_B0 = B0;
#endif
#ifdef B1000000
    __ss_B1000000 = B1000000;
#endif
#ifdef B110
    __ss_B110 = B110;
#endif
#ifdef B115200
    __ss_B115200 = B115200;
#endif
#ifdef B1152000
    __ss_B1152000 = B1152000;
#endif
#ifdef B1200
    __ss_B1200 = B1200;
#endif
#ifdef B134
    __ss_B134 = B134;
#endif
#ifdef B150
    __ss_B150 = B150;
#endif
#ifdef B1500000
    __ss_B1500000 = B1500000;
#endif
#ifdef B1800
    __ss_B1800 = B1800;
#endif
#ifdef B19200
    __ss_B19200 = B19200;
#endif
#ifdef B200
    __ss_B200 = B200;
#endif
#ifdef B2000000
    __ss_B2000000 = B2000000;
#endif
#ifdef B230400
    __ss_B230400 = B230400;
#endif
#ifdef B2400
    __ss_B2400 = B2400;
#endif
#ifdef B2500000
    __ss_B2500000 = B2500000;
#endif
#ifdef B300
    __ss_B300 = B300;
#endif
#ifdef B3000000
    __ss_B3000000 = B3000000;
#endif
#ifdef B3500000
    __ss_B3500000 = B3500000;
#endif
#ifdef B38400
    __ss_B38400 = B38400;
#endif
#ifdef B4000000
    __ss_B4000000 = B4000000;
#endif
#ifdef B460800
    __ss_B460800 = B460800;
#endif
#ifdef B4800
    __ss_B4800 = B4800;
#endif
#ifdef B50
    __ss_B50 = B50;
#endif
#ifdef B500000
    __ss_B500000 = B500000;
#endif
#ifdef B57600
    __ss_B57600 = B57600;
#endif
#ifdef B576000
    __ss_B576000 = B576000;
#endif
#ifdef B600
    __ss_B600 = B600;
#endif
#ifdef B75
    __ss_B75 = B75;
#endif
#ifdef B921600
    __ss_B921600 = B921600;
#endif
#ifdef B9600
    __ss_B9600 = B9600;
#endif
#ifdef BRKINT
    __ss_BRKINT = BRKINT;
#endif
#ifdef BS0
    __ss_BS0 = BS0;
#endif
#ifdef BS1
    __ss_BS1 = BS1;
#endif
#ifdef BSDLY
    __ss_BSDLY = BSDLY;
#endif
#ifdef CBAUD
    __ss_CBAUD = CBAUD;
#endif
#ifdef CBAUDEX
    __ss_CBAUDEX = CBAUDEX;
#endif
#ifdef CDSUSP
    __ss_CDSUSP = CDSUSP;
#endif
#ifdef CEOF
    __ss_CEOF = CEOF;
#endif
#ifdef CEOL
    __ss_CEOL = CEOL;
#endif
#ifdef CEOT
    __ss_CEOT = CEOT;
#endif
#ifdef CERASE
    __ss_CERASE = CERASE;
#endif
#ifdef CFLUSH
    __ss_CFLUSH = CFLUSH;
#endif
#ifdef CIBAUD
    __ss_CIBAUD = CIBAUD;
#endif
#ifdef CINTR
    __ss_CINTR = CINTR;
#endif
#ifdef CKILL
    __ss_CKILL = CKILL;
#endif
#ifdef CLNEXT
    __ss_CLNEXT = CLNEXT;
#endif
#ifdef CLOCAL
    __ss_CLOCAL = CLOCAL;
#endif
#ifdef CQUIT
    __ss_CQUIT = CQUIT;
#endif
#ifdef CR0
    __ss_CR0 = CR0;
#endif
#ifdef CR1
    __ss_CR1 = CR1;
#endif
#ifdef CR2
    __ss_CR2 = CR2;
#endif
#ifdef CR3
    __ss_CR3 = CR3;
#endif
#ifdef CRDLY
    __ss_CRDLY = CRDLY;
#endif
#ifdef CREAD
    __ss_CREAD = CREAD;
#endif
#ifdef CRPRNT
    __ss_CRPRNT = CRPRNT;
#endif
#ifdef CRTSCTS
    __ss_CRTSCTS = CRTSCTS;
#endif
#ifdef CS5
    __ss_CS5 = CS5;
#endif
#ifdef CS6
    __ss_CS6 = CS6;
#endif
#ifdef CS7
    __ss_CS7 = CS7;
#endif
#ifdef CS8
    __ss_CS8 = CS8;
#endif
#ifdef CSIZE
    __ss_CSIZE = CSIZE;
#endif
#ifdef CSTART
    __ss_CSTART = CSTART;
#endif
#ifdef CSTOP
    __ss_CSTOP = CSTOP;
#endif
#ifdef CSTOPB
    __ss_CSTOPB = CSTOPB;
#endif
#ifdef CSUSP
    __ss_CSUSP = CSUSP;
#endif
#ifdef CWERASE
    __ss_CWERASE = CWERASE;
#endif
#ifdef ECHO
    __ss_ECHO = ECHO;
#endif
#ifdef ECHOCTL
    __ss_ECHOCTL = ECHOCTL;
#endif
#ifdef ECHOE
    __ss_ECHOE = ECHOE;
#endif
#ifdef ECHOK
    __ss_ECHOK = ECHOK;
#endif
#ifdef ECHOKE
    __ss_ECHOKE = ECHOKE;
#endif
#ifdef ECHONL
    __ss_ECHONL = ECHONL;
#endif
#ifdef ECHOPRT
    __ss_ECHOPRT = ECHOPRT;
#endif
#ifdef EXTA
    __ss_EXTA = EXTA;
#endif
#ifdef EXTB
    __ss_EXTB = EXTB;
#endif
#ifdef EXTPROC
    __ss_EXTPROC = EXTPROC;
#endif
#ifdef FF0
    __ss_FF0 = FF0;
#endif
#ifdef FF1
    __ss_FF1 = FF1;
#endif
#ifdef FFDLY
    __ss_FFDLY = FFDLY;
#endif
#ifdef FIOASYNC
    __ss_FIOASYNC = FIOASYNC;
#endif
#ifdef FIOCLEX
    __ss_FIOCLEX = FIOCLEX;
#endif
#ifdef FIONBIO
    __ss_FIONBIO = FIONBIO;
#endif
#ifdef FIONCLEX
    __ss_FIONCLEX = FIONCLEX;
#endif
#ifdef FIONREAD
    __ss_FIONREAD = FIONREAD;
#endif
#ifdef FLUSHO
    __ss_FLUSHO = FLUSHO;
#endif
#ifdef HUPCL
    __ss_HUPCL = HUPCL;
#endif
#ifdef ICANON
    __ss_ICANON = ICANON;
#endif
#ifdef ICRNL
    __ss_ICRNL = ICRNL;
#endif
#ifdef IEXTEN
    __ss_IEXTEN = IEXTEN;
#endif
#ifdef IGNBRK
    __ss_IGNBRK = IGNBRK;
#endif
#ifdef IGNCR
    __ss_IGNCR = IGNCR;
#endif
#ifdef IGNPAR
    __ss_IGNPAR = IGNPAR;
#endif
#ifdef IMAXBEL
    __ss_IMAXBEL = IMAXBEL;
#endif
#ifdef INLCR
    __ss_INLCR = INLCR;
#endif
#ifdef INPCK
    __ss_INPCK = INPCK;
#endif
#ifdef IOCSIZE_MASK
    __ss_IOCSIZE_MASK = IOCSIZE_MASK;
#endif
#ifdef IOCSIZE_SHIFT
    __ss_IOCSIZE_SHIFT = IOCSIZE_SHIFT;
#endif
#ifdef ISIG
    __ss_ISIG = ISIG;
#endif
#ifdef ISTRIP
    __ss_ISTRIP = ISTRIP;
#endif
#ifdef IUCLC
    __ss_IUCLC = IUCLC;
#endif
#ifdef IUTF8
    __ss_IUTF8 = IUTF8;
#endif
#ifdef IXANY
    __ss_IXANY = IXANY;
#endif
#ifdef IXOFF
    __ss_IXOFF = IXOFF;
#endif
#ifdef IXON
    __ss_IXON = IXON;
#endif
#ifdef NCC
    __ss_NCC = NCC;
#endif
#ifdef NCCS
    __ss_NCCS = NCCS;
#endif
#ifdef NL0
    __ss_NL0 = NL0;
#endif
#ifdef NL1
    __ss_NL1 = NL1;
#endif
#ifdef NLDLY
    __ss_NLDLY = NLDLY;
#endif
#ifdef NOFLSH
    __ss_NOFLSH = NOFLSH;
#endif
#ifdef N_MOUSE
    __ss_N_MOUSE = N_MOUSE;
#endif
#ifdef N_PPP
    __ss_N_PPP = N_PPP;
#endif
#ifdef N_SLIP
    __ss_N_SLIP = N_SLIP;
#endif
#ifdef N_STRIP
    __ss_N_STRIP = N_STRIP;
#endif
#ifdef N_TTY
    __ss_N_TTY = N_TTY;
#endif
#ifdef OCRNL
    __ss_OCRNL = OCRNL;
#endif
#ifdef OFDEL
    __ss_OFDEL = OFDEL;
#endif
#ifdef OFILL
    __ss_OFILL = OFILL;
#endif
#ifdef OLCUC
    __ss_OLCUC = OLCUC;
#endif
#ifdef ONLCR
    __ss_ONLCR = ONLCR;
#endif
#ifdef ONLRET
    __ss_ONLRET = ONLRET;
#endif
#ifdef ONOCR
    __ss_ONOCR = ONOCR;
#endif
#ifdef OPOST
    __ss_OPOST = OPOST;
#endif
#ifdef PARENB
    __ss_PARENB = PARENB;
#endif
#ifdef PARMRK
    __ss_PARMRK = PARMRK;
#endif
#ifdef PARODD
    __ss_PARODD = PARODD;
#endif
#ifdef PENDIN
    __ss_PENDIN = PENDIN;
#endif
#ifdef TAB0
    __ss_TAB0 = TAB0;
#endif
#ifdef TAB1
    __ss_TAB1 = TAB1;
#endif
#ifdef TAB2
    __ss_TAB2 = TAB2;
#endif
#ifdef TAB3
    __ss_TAB3 = TAB3;
#endif
#ifdef TABDLY
    __ss_TABDLY = TABDLY;
#endif
#ifdef TCFLSH
    __ss_TCFLSH = TCFLSH;
#endif
#ifdef TCGETA
    __ss_TCGETA = TCGETA;
#endif
#ifdef TCGETS
    __ss_TCGETS = TCGETS;
#endif
#ifdef TCIFLUSH
    __ss_TCIFLUSH = TCIFLUSH;
#endif
#ifdef TCIOFF
    __ss_TCIOFF = TCIOFF;
#endif
#ifdef TCIOFLUSH
    __ss_TCIOFLUSH = TCIOFLUSH;
#endif
#ifdef TCION
    __ss_TCION = TCION;
#endif
#ifdef TCOFLUSH
    __ss_TCOFLUSH = TCOFLUSH;
#endif
#ifdef TCOOFF
    __ss_TCOOFF = TCOOFF;
#endif
#ifdef TCOON
    __ss_TCOON = TCOON;
#endif
#ifdef TCSADRAIN
    __ss_TCSADRAIN = TCSADRAIN;
#endif
#ifdef TCSAFLUSH
    __ss_TCSAFLUSH = TCSAFLUSH;
#endif
#ifdef TCSANOW
    __ss_TCSANOW = TCSANOW;
#endif
#ifdef TCSBRK
    __ss_TCSBRK = TCSBRK;
#endif
#ifdef TCSBRKP
    __ss_TCSBRKP = TCSBRKP;
#endif
#ifdef TCSETA
    __ss_TCSETA = TCSETA;
#endif
#ifdef TCSETAF
    __ss_TCSETAF = TCSETAF;
#endif
#ifdef TCSETAW
    __ss_TCSETAW = TCSETAW;
#endif
#ifdef TCSETS
    __ss_TCSETS = TCSETS;
#endif
#ifdef TCSETSF
    __ss_TCSETSF = TCSETSF;
#endif
#ifdef TCSETSW
    __ss_TCSETSW = TCSETSW;
#endif
#ifdef TCXONC
    __ss_TCXONC = TCXONC;
#endif
#ifdef TIOCCONS
    __ss_TIOCCONS = TIOCCONS;
#endif
#ifdef TIOCEXCL
    __ss_TIOCEXCL = TIOCEXCL;
#endif
#ifdef TIOCGETD
    __ss_TIOCGETD = TIOCGETD;
#endif
#ifdef TIOCGICOUNT
    __ss_TIOCGICOUNT = TIOCGICOUNT;
#endif
#ifdef TIOCGLCKTRMIOS
    __ss_TIOCGLCKTRMIOS = TIOCGLCKTRMIOS;
#endif
#ifdef TIOCGPGRP
    __ss_TIOCGPGRP = TIOCGPGRP;
#endif
#ifdef TIOCGSERIAL
    __ss_TIOCGSERIAL = TIOCGSERIAL;
#endif
#ifdef TIOCGSOFTCAR
    __ss_TIOCGSOFTCAR = TIOCGSOFTCAR;
#endif
#ifdef TIOCGWINSZ
    __ss_TIOCGWINSZ = TIOCGWINSZ;
#endif
#ifdef TIOCINQ
    __ss_TIOCINQ = TIOCINQ;
#endif
#ifdef TIOCLINUX
    __ss_TIOCLINUX = TIOCLINUX;
#endif
#ifdef TIOCMBIC
    __ss_TIOCMBIC = TIOCMBIC;
#endif
#ifdef TIOCMBIS
    __ss_TIOCMBIS = TIOCMBIS;
#endif
#ifdef TIOCMGET
    __ss_TIOCMGET = TIOCMGET;
#endif
#ifdef TIOCMIWAIT
    __ss_TIOCMIWAIT = TIOCMIWAIT;
#endif
#ifdef TIOCMSET
    __ss_TIOCMSET = TIOCMSET;
#endif
#ifdef TIOCM_CAR
    __ss_TIOCM_CAR = TIOCM_CAR;
#endif
#ifdef TIOCM_CD
    __ss_TIOCM_CD = TIOCM_CD;
#endif
#ifdef TIOCM_CTS
    __ss_TIOCM_CTS = TIOCM_CTS;
#endif
#ifdef TIOCM_DSR
    __ss_TIOCM_DSR = TIOCM_DSR;
#endif
#ifdef TIOCM_DTR
    __ss_TIOCM_DTR = TIOCM_DTR;
#endif
#ifdef TIOCM_LE
    __ss_TIOCM_LE = TIOCM_LE;
#endif
#ifdef TIOCM_RI
    __ss_TIOCM_RI = TIOCM_RI;
#endif
#ifdef TIOCM_RNG
    __ss_TIOCM_RNG = TIOCM_RNG;
#endif
#ifdef TIOCM_RTS
    __ss_TIOCM_RTS = TIOCM_RTS;
#endif
#ifdef TIOCM_SR
    __ss_TIOCM_SR = TIOCM_SR;
#endif
#ifdef TIOCM_ST
    __ss_TIOCM_ST = TIOCM_ST;
#endif
#ifdef TIOCNOTTY
    __ss_TIOCNOTTY = TIOCNOTTY;
#endif
#ifdef TIOCNXCL
    __ss_TIOCNXCL = TIOCNXCL;
#endif
#ifdef TIOCOUTQ
    __ss_TIOCOUTQ = TIOCOUTQ;
#endif
#ifdef TIOCPKT
    __ss_TIOCPKT = TIOCPKT;
#endif
#ifdef TIOCPKT_DATA
    __ss_TIOCPKT_DATA = TIOCPKT_DATA;
#endif
#ifdef TIOCPKT_DOSTOP
    __ss_TIOCPKT_DOSTOP = TIOCPKT_DOSTOP;
#endif
#ifdef TIOCPKT_FLUSHREAD
    __ss_TIOCPKT_FLUSHREAD = TIOCPKT_FLUSHREAD;
#endif
#ifdef TIOCPKT_FLUSHWRITE
    __ss_TIOCPKT_FLUSHWRITE = TIOCPKT_FLUSHWRITE;
#endif
#ifdef TIOCPKT_NOSTOP
    __ss_TIOCPKT_NOSTOP = TIOCPKT_NOSTOP;
#endif
#ifdef TIOCPKT_START
    __ss_TIOCPKT_START = TIOCPKT_START;
#endif
#ifdef TIOCPKT_STOP
    __ss_TIOCPKT_STOP = TIOCPKT_STOP;
#endif
#ifdef TIOCSCTTY
    __ss_TIOCSCTTY = TIOCSCTTY;
#endif
#ifdef TIOCSERCONFIG
    __ss_TIOCSERCONFIG = TIOCSERCONFIG;
#endif
#ifdef TIOCSERGETLSR
    __ss_TIOCSERGETLSR = TIOCSERGETLSR;
#endif
#ifdef TIOCSERGETMULTI
    __ss_TIOCSERGETMULTI = TIOCSERGETMULTI;
#endif
#ifdef TIOCSERGSTRUCT
    __ss_TIOCSERGSTRUCT = TIOCSERGSTRUCT;
#endif
#ifdef TIOCSERGWILD
    __ss_TIOCSERGWILD = TIOCSERGWILD;
#endif
#ifdef TIOCSERSETMULTI
    __ss_TIOCSERSETMULTI = TIOCSERSETMULTI;
#endif
#ifdef TIOCSERSWILD
    __ss_TIOCSERSWILD = TIOCSERSWILD;
#endif
#ifdef TIOCSER_TEMT
    __ss_TIOCSER_TEMT = TIOCSER_TEMT;
#endif
#ifdef TIOCSETD
    __ss_TIOCSETD = TIOCSETD;
#endif
#ifdef TIOCSLCKTRMIOS
    __ss_TIOCSLCKTRMIOS = TIOCSLCKTRMIOS;
#endif
#ifdef TIOCSPGRP
    __ss_TIOCSPGRP = TIOCSPGRP;
#endif
#ifdef TIOCSSERIAL
    __ss_TIOCSSERIAL = TIOCSSERIAL;
#endif
#ifdef TIOCSSOFTCAR
    __ss_TIOCSSOFTCAR = TIOCSSOFTCAR;
#endif
#ifdef TIOCSTI
    __ss_TIOCSTI = TIOCSTI;
#endif
#ifdef TIOCSWINSZ
    __ss_TIOCSWINSZ = TIOCSWINSZ;
#endif
#ifdef TOSTOP
    __ss_TOSTOP = TOSTOP;
#endif
#ifdef VDISCARD
    __ss_VDISCARD = VDISCARD;
#endif
#ifdef VEOF
    __ss_VEOF = VEOF;
#endif
#ifdef VEOL
    __ss_VEOL = VEOL;
#endif
#ifdef VEOL2
    __ss_VEOL2 = VEOL2;
#endif
#ifdef VERASE
    __ss_VERASE = VERASE;
#endif
#ifdef VINTR
    __ss_VINTR = VINTR;
#endif
#ifdef VKILL
    __ss_VKILL = VKILL;
#endif
#ifdef VLNEXT
    __ss_VLNEXT = VLNEXT;
#endif
#ifdef VMIN
    __ss_VMIN = VMIN;
#endif
#ifdef VQUIT
    __ss_VQUIT = VQUIT;
#endif
#ifdef VREPRINT
    __ss_VREPRINT = VREPRINT;
#endif
#ifdef VSTART
    __ss_VSTART = VSTART;
#endif
#ifdef VSTOP
    __ss_VSTOP = VSTOP;
#endif
#ifdef VSUSP
    __ss_VSUSP = VSUSP;
#endif
#ifdef VSWTC
    __ss_VSWTC = VSWTC;
#endif
#if defined(VSWTCH)
    __ss_VSWTCH = VSWTCH;
#elif defined(VSWTC)
    __ss_VSWTCH = VSWTC; /* like CPython */
#endif
#ifdef VT0
    __ss_VT0 = VT0;
#endif
#ifdef VT1
    __ss_VT1 = VT1;
#endif
#ifdef VTDLY
    __ss_VTDLY = VTDLY;
#endif
#ifdef VTIME
    __ss_VTIME = VTIME;
#endif
#ifdef VWERASE
    __ss_VWERASE = VWERASE;
#endif
#ifdef XCASE
    __ss_XCASE = XCASE;
#endif
#ifdef XTABS
    __ss_XTABS = XTABS;
#endif
#ifdef _POSIX_VDISABLE
    __ss__POSIX_VDISABLE = _POSIX_VDISABLE;
#endif
}

} // module namespace
