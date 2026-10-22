/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __TTY_HPP
#define __TTY_HPP

#include "builtin.hpp"
#include "termios.hpp"

using namespace __shedskin__;
namespace __tty__ {

/* like CPython, tty re-exports everything from termios ('from termios import *') */
using __termios__::error;
using __termios__::cl_error;
using __termios__::cclist;
using __termios__::cl_cclist;
using __termios__::tcattrs;
using __termios__::cl_tcattrs;

using __termios__::tcgetattr;
using __termios__::tcsetattr;
using __termios__::tcsendbreak;
using __termios__::tcdrain;
using __termios__::tcflush;
using __termios__::tcflow;
using __termios__::tcgetwinsize;
using __termios__::tcsetwinsize;

using __termios__::__ss_B0;
using __termios__::__ss_B1000000;
using __termios__::__ss_B110;
using __termios__::__ss_B115200;
using __termios__::__ss_B1152000;
using __termios__::__ss_B1200;
using __termios__::__ss_B134;
using __termios__::__ss_B150;
using __termios__::__ss_B1500000;
using __termios__::__ss_B1800;
using __termios__::__ss_B19200;
using __termios__::__ss_B200;
using __termios__::__ss_B2000000;
using __termios__::__ss_B230400;
using __termios__::__ss_B2400;
using __termios__::__ss_B2500000;
using __termios__::__ss_B300;
using __termios__::__ss_B3000000;
using __termios__::__ss_B3500000;
using __termios__::__ss_B38400;
using __termios__::__ss_B4000000;
using __termios__::__ss_B460800;
using __termios__::__ss_B4800;
using __termios__::__ss_B50;
using __termios__::__ss_B500000;
using __termios__::__ss_B57600;
using __termios__::__ss_B576000;
using __termios__::__ss_B600;
using __termios__::__ss_B75;
using __termios__::__ss_B921600;
using __termios__::__ss_B9600;
using __termios__::__ss_BRKINT;
using __termios__::__ss_BS0;
using __termios__::__ss_BS1;
using __termios__::__ss_BSDLY;
using __termios__::__ss_CBAUD;
using __termios__::__ss_CBAUDEX;
using __termios__::__ss_CDSUSP;
using __termios__::__ss_CEOF;
using __termios__::__ss_CEOL;
using __termios__::__ss_CEOT;
using __termios__::__ss_CERASE;
using __termios__::__ss_CFLUSH;
using __termios__::__ss_CIBAUD;
using __termios__::__ss_CINTR;
using __termios__::__ss_CKILL;
using __termios__::__ss_CLNEXT;
using __termios__::__ss_CLOCAL;
using __termios__::__ss_CQUIT;
using __termios__::__ss_CR0;
using __termios__::__ss_CR1;
using __termios__::__ss_CR2;
using __termios__::__ss_CR3;
using __termios__::__ss_CRDLY;
using __termios__::__ss_CREAD;
using __termios__::__ss_CRPRNT;
using __termios__::__ss_CRTSCTS;
using __termios__::__ss_CS5;
using __termios__::__ss_CS6;
using __termios__::__ss_CS7;
using __termios__::__ss_CS8;
using __termios__::__ss_CSIZE;
using __termios__::__ss_CSTART;
using __termios__::__ss_CSTOP;
using __termios__::__ss_CSTOPB;
using __termios__::__ss_CSUSP;
using __termios__::__ss_CWERASE;
using __termios__::__ss_ECHO;
using __termios__::__ss_ECHOCTL;
using __termios__::__ss_ECHOE;
using __termios__::__ss_ECHOK;
using __termios__::__ss_ECHOKE;
using __termios__::__ss_ECHONL;
using __termios__::__ss_ECHOPRT;
using __termios__::__ss_EXTA;
using __termios__::__ss_EXTB;
using __termios__::__ss_EXTPROC;
using __termios__::__ss_FF0;
using __termios__::__ss_FF1;
using __termios__::__ss_FFDLY;
using __termios__::__ss_FIOASYNC;
using __termios__::__ss_FIOCLEX;
using __termios__::__ss_FIONBIO;
using __termios__::__ss_FIONCLEX;
using __termios__::__ss_FIONREAD;
using __termios__::__ss_FLUSHO;
using __termios__::__ss_HUPCL;
using __termios__::__ss_ICANON;
using __termios__::__ss_ICRNL;
using __termios__::__ss_IEXTEN;
using __termios__::__ss_IGNBRK;
using __termios__::__ss_IGNCR;
using __termios__::__ss_IGNPAR;
using __termios__::__ss_IMAXBEL;
using __termios__::__ss_INLCR;
using __termios__::__ss_INPCK;
using __termios__::__ss_IOCSIZE_MASK;
using __termios__::__ss_IOCSIZE_SHIFT;
using __termios__::__ss_ISIG;
using __termios__::__ss_ISTRIP;
using __termios__::__ss_IUCLC;
using __termios__::__ss_IUTF8;
using __termios__::__ss_IXANY;
using __termios__::__ss_IXOFF;
using __termios__::__ss_IXON;
using __termios__::__ss_NCC;
using __termios__::__ss_NCCS;
using __termios__::__ss_NL0;
using __termios__::__ss_NL1;
using __termios__::__ss_NLDLY;
using __termios__::__ss_NOFLSH;
using __termios__::__ss_N_MOUSE;
using __termios__::__ss_N_PPP;
using __termios__::__ss_N_SLIP;
using __termios__::__ss_N_STRIP;
using __termios__::__ss_N_TTY;
using __termios__::__ss_OCRNL;
using __termios__::__ss_OFDEL;
using __termios__::__ss_OFILL;
using __termios__::__ss_OLCUC;
using __termios__::__ss_ONLCR;
using __termios__::__ss_ONLRET;
using __termios__::__ss_ONOCR;
using __termios__::__ss_OPOST;
using __termios__::__ss_PARENB;
using __termios__::__ss_PARMRK;
using __termios__::__ss_PARODD;
using __termios__::__ss_PENDIN;
using __termios__::__ss_TAB0;
using __termios__::__ss_TAB1;
using __termios__::__ss_TAB2;
using __termios__::__ss_TAB3;
using __termios__::__ss_TABDLY;
using __termios__::__ss_TCFLSH;
using __termios__::__ss_TCGETA;
using __termios__::__ss_TCGETS;
using __termios__::__ss_TCIFLUSH;
using __termios__::__ss_TCIOFF;
using __termios__::__ss_TCIOFLUSH;
using __termios__::__ss_TCION;
using __termios__::__ss_TCOFLUSH;
using __termios__::__ss_TCOOFF;
using __termios__::__ss_TCOON;
using __termios__::__ss_TCSADRAIN;
using __termios__::__ss_TCSAFLUSH;
using __termios__::__ss_TCSANOW;
using __termios__::__ss_TCSBRK;
using __termios__::__ss_TCSBRKP;
using __termios__::__ss_TCSETA;
using __termios__::__ss_TCSETAF;
using __termios__::__ss_TCSETAW;
using __termios__::__ss_TCSETS;
using __termios__::__ss_TCSETSF;
using __termios__::__ss_TCSETSW;
using __termios__::__ss_TCXONC;
using __termios__::__ss_TIOCCONS;
using __termios__::__ss_TIOCEXCL;
using __termios__::__ss_TIOCGETD;
using __termios__::__ss_TIOCGICOUNT;
using __termios__::__ss_TIOCGLCKTRMIOS;
using __termios__::__ss_TIOCGPGRP;
using __termios__::__ss_TIOCGSERIAL;
using __termios__::__ss_TIOCGSOFTCAR;
using __termios__::__ss_TIOCGWINSZ;
using __termios__::__ss_TIOCINQ;
using __termios__::__ss_TIOCLINUX;
using __termios__::__ss_TIOCMBIC;
using __termios__::__ss_TIOCMBIS;
using __termios__::__ss_TIOCMGET;
using __termios__::__ss_TIOCMIWAIT;
using __termios__::__ss_TIOCMSET;
using __termios__::__ss_TIOCM_CAR;
using __termios__::__ss_TIOCM_CD;
using __termios__::__ss_TIOCM_CTS;
using __termios__::__ss_TIOCM_DSR;
using __termios__::__ss_TIOCM_DTR;
using __termios__::__ss_TIOCM_LE;
using __termios__::__ss_TIOCM_RI;
using __termios__::__ss_TIOCM_RNG;
using __termios__::__ss_TIOCM_RTS;
using __termios__::__ss_TIOCM_SR;
using __termios__::__ss_TIOCM_ST;
using __termios__::__ss_TIOCNOTTY;
using __termios__::__ss_TIOCNXCL;
using __termios__::__ss_TIOCOUTQ;
using __termios__::__ss_TIOCPKT;
using __termios__::__ss_TIOCPKT_DATA;
using __termios__::__ss_TIOCPKT_DOSTOP;
using __termios__::__ss_TIOCPKT_FLUSHREAD;
using __termios__::__ss_TIOCPKT_FLUSHWRITE;
using __termios__::__ss_TIOCPKT_NOSTOP;
using __termios__::__ss_TIOCPKT_START;
using __termios__::__ss_TIOCPKT_STOP;
using __termios__::__ss_TIOCSCTTY;
using __termios__::__ss_TIOCSERCONFIG;
using __termios__::__ss_TIOCSERGETLSR;
using __termios__::__ss_TIOCSERGETMULTI;
using __termios__::__ss_TIOCSERGSTRUCT;
using __termios__::__ss_TIOCSERGWILD;
using __termios__::__ss_TIOCSERSETMULTI;
using __termios__::__ss_TIOCSERSWILD;
using __termios__::__ss_TIOCSER_TEMT;
using __termios__::__ss_TIOCSETD;
using __termios__::__ss_TIOCSLCKTRMIOS;
using __termios__::__ss_TIOCSPGRP;
using __termios__::__ss_TIOCSSERIAL;
using __termios__::__ss_TIOCSSOFTCAR;
using __termios__::__ss_TIOCSTI;
using __termios__::__ss_TIOCSWINSZ;
using __termios__::__ss_TOSTOP;
using __termios__::__ss_VDISCARD;
using __termios__::__ss_VEOF;
using __termios__::__ss_VEOL;
using __termios__::__ss_VEOL2;
using __termios__::__ss_VERASE;
using __termios__::__ss_VINTR;
using __termios__::__ss_VKILL;
using __termios__::__ss_VLNEXT;
using __termios__::__ss_VMIN;
using __termios__::__ss_VQUIT;
using __termios__::__ss_VREPRINT;
using __termios__::__ss_VSTART;
using __termios__::__ss_VSTOP;
using __termios__::__ss_VSUSP;
using __termios__::__ss_VSWTC;
using __termios__::__ss_VSWTCH;
using __termios__::__ss_VT0;
using __termios__::__ss_VT1;
using __termios__::__ss_VTDLY;
using __termios__::__ss_VTIME;
using __termios__::__ss_VWERASE;
using __termios__::__ss_XCASE;
using __termios__::__ss_XTABS;
using __termios__::__ss__POSIX_VDISABLE;

extern str *__name__;
extern __ss_int IFLAG, OFLAG, CFLAG, LFLAG, ISPEED, OSPEED, CC;

void *cfmakeraw(tcattrs *mode);
void *cfmakecbreak(tcattrs *mode);

tcattrs *__setmode(int fd, __ss_int when, bool raw);

/* when defaults to TCSAFLUSH */
template<class W> inline __ss_int __when(W when) {
    if constexpr (std::is_same_v<W, __ss_void_struct>)
        return TCSAFLUSH;
    else
        return when;
}

template<class T, class W> tcattrs *setraw(T fd, W when) {
    return __setmode(__termios__::__tc_fd(fd), __when(when), true);
}

template<class T, class W> tcattrs *setcbreak(T fd, W when) {
    return __setmode(__termios__::__tc_fd(fd), __when(when), false);
}

void __init();

} // module namespace
#endif
