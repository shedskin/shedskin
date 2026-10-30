/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __TERMIOS_HPP
#define __TERMIOS_HPP

#include "builtin.hpp"

#include <termios.h>
#include <sys/ioctl.h>
#include <unistd.h>

using namespace __shedskin__;
namespace __termios__ {

extern str *__name__;
extern class_ *cl_error, *cl_cclist, *cl_tcattrs;

extern __ss_int __ss_B0, __ss_B1000000, __ss_B110, __ss_B115200, __ss_B1152000, __ss_B1200,
    __ss_B134, __ss_B150, __ss_B1500000, __ss_B1800, __ss_B19200, __ss_B200, __ss_B2000000,
    __ss_B230400, __ss_B2400, __ss_B2500000, __ss_B300, __ss_B3000000, __ss_B3500000, __ss_B38400,
    __ss_B4000000, __ss_B460800, __ss_B4800, __ss_B50, __ss_B500000, __ss_B57600, __ss_B576000,
    __ss_B600, __ss_B75, __ss_B921600, __ss_B9600, __ss_BRKINT, __ss_BS0, __ss_BS1, __ss_BSDLY,
    __ss_CBAUD, __ss_CBAUDEX, __ss_CDSUSP, __ss_CEOF, __ss_CEOL, __ss_CEOT, __ss_CERASE,
    __ss_CFLUSH, __ss_CIBAUD, __ss_CINTR, __ss_CKILL, __ss_CLNEXT, __ss_CLOCAL, __ss_CQUIT,
    __ss_CR0, __ss_CR1, __ss_CR2, __ss_CR3, __ss_CRDLY, __ss_CREAD, __ss_CRPRNT, __ss_CRTSCTS,
    __ss_CS5, __ss_CS6, __ss_CS7, __ss_CS8, __ss_CSIZE, __ss_CSTART, __ss_CSTOP, __ss_CSTOPB,
    __ss_CSUSP, __ss_CWERASE, __ss_ECHO, __ss_ECHOCTL, __ss_ECHOE, __ss_ECHOK, __ss_ECHOKE,
    __ss_ECHONL, __ss_ECHOPRT, __ss_EXTA, __ss_EXTB, __ss_EXTPROC, __ss_FF0, __ss_FF1, __ss_FFDLY,
    __ss_FIOASYNC, __ss_FIOCLEX, __ss_FIONBIO, __ss_FIONCLEX, __ss_FIONREAD, __ss_FLUSHO,
    __ss_HUPCL, __ss_ICANON, __ss_ICRNL, __ss_IEXTEN, __ss_IGNBRK, __ss_IGNCR, __ss_IGNPAR,
    __ss_IMAXBEL, __ss_INLCR, __ss_INPCK, __ss_IOCSIZE_MASK, __ss_IOCSIZE_SHIFT, __ss_ISIG,
    __ss_ISTRIP, __ss_IUCLC, __ss_IUTF8, __ss_IXANY, __ss_IXOFF, __ss_IXON, __ss_NCC, __ss_NCCS,
    __ss_NL0, __ss_NL1, __ss_NLDLY, __ss_NOFLSH, __ss_N_MOUSE, __ss_N_PPP, __ss_N_SLIP,
    __ss_N_STRIP, __ss_N_TTY, __ss_OCRNL, __ss_OFDEL, __ss_OFILL, __ss_OLCUC, __ss_ONLCR,
    __ss_ONLRET, __ss_ONOCR, __ss_OPOST, __ss_PARENB, __ss_PARMRK, __ss_PARODD, __ss_PENDIN,
    __ss_TAB0, __ss_TAB1, __ss_TAB2, __ss_TAB3, __ss_TABDLY, __ss_TCFLSH, __ss_TCGETA, __ss_TCGETS,
    __ss_TCIFLUSH, __ss_TCIOFF, __ss_TCIOFLUSH, __ss_TCION, __ss_TCOFLUSH, __ss_TCOOFF, __ss_TCOON,
    __ss_TCSADRAIN, __ss_TCSAFLUSH, __ss_TCSANOW, __ss_TCSBRK, __ss_TCSBRKP, __ss_TCSETA,
    __ss_TCSETAF, __ss_TCSETAW, __ss_TCSETS, __ss_TCSETSF, __ss_TCSETSW, __ss_TCXONC, __ss_TIOCCONS,
    __ss_TIOCEXCL, __ss_TIOCGETD, __ss_TIOCGICOUNT, __ss_TIOCGLCKTRMIOS, __ss_TIOCGPGRP,
    __ss_TIOCGSERIAL, __ss_TIOCGSOFTCAR, __ss_TIOCGWINSZ, __ss_TIOCINQ, __ss_TIOCLINUX,
    __ss_TIOCMBIC, __ss_TIOCMBIS, __ss_TIOCMGET, __ss_TIOCMIWAIT, __ss_TIOCMSET, __ss_TIOCM_CAR,
    __ss_TIOCM_CD, __ss_TIOCM_CTS, __ss_TIOCM_DSR, __ss_TIOCM_DTR, __ss_TIOCM_LE, __ss_TIOCM_RI,
    __ss_TIOCM_RNG, __ss_TIOCM_RTS, __ss_TIOCM_SR, __ss_TIOCM_ST, __ss_TIOCNOTTY, __ss_TIOCNXCL,
    __ss_TIOCOUTQ, __ss_TIOCPKT, __ss_TIOCPKT_DATA, __ss_TIOCPKT_DOSTOP, __ss_TIOCPKT_FLUSHREAD,
    __ss_TIOCPKT_FLUSHWRITE, __ss_TIOCPKT_NOSTOP, __ss_TIOCPKT_START, __ss_TIOCPKT_STOP,
    __ss_TIOCSCTTY, __ss_TIOCSERCONFIG, __ss_TIOCSERGETLSR, __ss_TIOCSERGETMULTI,
    __ss_TIOCSERGSTRUCT, __ss_TIOCSERGWILD, __ss_TIOCSERSETMULTI, __ss_TIOCSERSWILD,
    __ss_TIOCSER_TEMT, __ss_TIOCSETD, __ss_TIOCSLCKTRMIOS, __ss_TIOCSPGRP, __ss_TIOCSSERIAL,
    __ss_TIOCSSOFTCAR, __ss_TIOCSTI, __ss_TIOCSWINSZ, __ss_TOSTOP, __ss_VDISCARD, __ss_VEOF,
    __ss_VEOL, __ss_VEOL2, __ss_VERASE, __ss_VINTR, __ss_VKILL, __ss_VLNEXT, __ss_VMIN, __ss_VQUIT,
    __ss_VREPRINT, __ss_VSTART, __ss_VSTOP, __ss_VSUSP, __ss_VSWTC, __ss_VSWTCH, __ss_VT0, __ss_VT1,
    __ss_VTDLY, __ss_VTIME, __ss_VWERASE, __ss_XCASE, __ss_XTABS, __ss__POSIX_VDISABLE;

class error : public Exception {
public:
    error(str *msg=0) : Exception(msg) {
        __class__ = cl_error;
    }
};

/* the control characters of a termios attribute list: 1-byte bytes objects
   when read, ints or 1-byte bytes objects when written (like CPython) */
class cclist : public pyseq<bytes *> {
public:
    cc_t cc[NCCS];

    cclist() {
        __class__ = cl_cclist;
        memset(cc, 0, sizeof(cc));
    }

    __ss_int __len__();
    bytes *__getitem__(__ss_int i);
    void *__setitem__(__ss_int i, __ss_int v);
    void *__setitem__(__ss_int i, bytes *v);
    __ss_bool __eq__(pyobj *p);
    __ss_bool __ne__(pyobj *p);
    str *__repr__();
    cclist *__copy__();
    cclist *__deepcopy__(dict<void *, pyobj *> *memo);
};

/* a termios attribute list: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc].
   attrs[6], attrs[CC] and attrs[tty.CC] translate to __getcc__ */
class tcattrs : public pyobj {
public:
    __ss_int flags[6]; /* iflag, oflag, cflag, lflag, ispeed, ospeed */
    cclist *cc;

    tcattrs() {
        __class__ = cl_tcattrs;
        memset(flags, 0, sizeof(flags));
        cc = new cclist();
    }

    __ss_int __len__();
    __ss_int __getitem__(__ss_int i);
    cclist *__getcc__();
    void *__setitem__(__ss_int i, __ss_int v);
    void *__setitem__(__ss_int i, cclist *v);
    __ss_bool __eq__(pyobj *p);
    __ss_bool __ne__(pyobj *p);
    str *__repr__();
    tcattrs *__copy__();
    tcattrs *__deepcopy__(dict<void *, pyobj *> *memo);
};

/* like CPython, fd is a file descriptor or an object with a fileno() method */
template<class T> inline int __tc_fd(T fd) {
    __ss_int f;
    if constexpr (std::is_pointer_v<T>)
        f = fd->__ss_fileno();
    else
        f = fd;
    int c = __ss_cint(f);
    if(c < 0)
        throw new ValueError(__add_strs(3, new str("file descriptor cannot be a negative integer ("), __str(f), new str(")")));
    return c;
}

tcattrs *__tcgetattr(int fd);
void *__tcsetattr(int fd, __ss_int when, tcattrs *attributes);
void *__tcsendbreak(int fd, __ss_int duration);
void *__tcdrain(int fd);
void *__tcflush(int fd, __ss_int queue);
void *__tcflow(int fd, __ss_int action);
tuple<__ss_int> *__tcgetwinsize(int fd);
void *__tcsetwinsize(int fd, __ss_int rows, __ss_int cols);

template<class T> tcattrs *tcgetattr(T fd) {
    return __tcgetattr(__tc_fd(fd));
}

template<class T> void *tcsetattr(T fd, __ss_int when, tcattrs *attributes) {
    return __tcsetattr(__tc_fd(fd), when, attributes);
}

template<class T> void *tcsendbreak(T fd, __ss_int duration) {
    return __tcsendbreak(__tc_fd(fd), duration);
}

template<class T> void *tcdrain(T fd) {
    return __tcdrain(__tc_fd(fd));
}

template<class T> void *tcflush(T fd, __ss_int queue) {
    return __tcflush(__tc_fd(fd), queue);
}

template<class T> void *tcflow(T fd, __ss_int action) {
    return __tcflow(__tc_fd(fd), action);
}

template<class T> tuple<__ss_int> *tcgetwinsize(T fd) {
    return __tcgetwinsize(__tc_fd(fd));
}

/* winsize: a two-item sequence of ints, such as a tuple or list */
template<class T, class W> void *tcsetwinsize(T fd, W *winsize) {
    int f = __tc_fd(fd);
    if(winsize->__len__() != 2)
        throw new TypeError(new str("tcsetwinsize, arg 2: must be a two-item sequence"));
    return __tcsetwinsize(f, winsize->__getitem__(0), winsize->__getitem__(1));
}

void __init();

} // module namespace
#endif
