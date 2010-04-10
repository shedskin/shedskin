#include "signal.hpp"
#include <signal.h>

namespace __signal__ {

str *__name__;
__ss_int __ss_SIGABRT, __ss_SIGALRM, __ss_SIGBUS, __ss_SIGCHLD, __ss_SIGCLD, __ss_SIGCONT, __ss_SIGFPE, __ss_SIGHUP, __ss_SIGILL, __ss_SIGINT, __ss_SIGIO, __ss_SIGIOT, __ss_SIGKILL, __ss_SIGPIPE, __ss_SIGPOLL, __ss_SIGPROF, __ss_SIGPWR, __ss_SIGQUIT, __ss_SIGRTMAX, __ss_SIGRTMIN, __ss_SIGSEGV, __ss_SIGSTOP, __ss_SIGSYS, __ss_SIGTERM, __ss_SIGTRAP, __ss_SIGTSTP, __ss_SIGTTIN, __ss_SIGTTOU, __ss_SIGURG, __ss_SIGUSR1, __ss_SIGUSR2, __ss_SIGVTALRM, __ss_SIGWINCH, __ss_SIGXCPU, __ss_SIGXFSZ; //, __ss_SIG_DFL, __ss_SIG_IGN;

void __init() {
    __name__ = new str("signal");

#ifndef __APPLE__
    __ss_SIGCLD = SIGCLD;
    __ss_SIGPOLL = SIGPOLL;
    __ss_SIGPWR = SIGPWR;
    __ss_SIGRTMAX = SIGRTMAX;
    __ss_SIGRTMIN = SIGRTMIN;
#endif

    __ss_SIGABRT = SIGABRT;
    __ss_SIGALRM = SIGALRM;
    __ss_SIGBUS = SIGBUS;
    __ss_SIGCHLD = SIGCHLD;
    __ss_SIGCONT = SIGCONT;
    __ss_SIGFPE = SIGFPE;
    __ss_SIGHUP = SIGHUP;
    __ss_SIGILL = SIGILL;
    __ss_SIGINT = SIGINT;
    __ss_SIGIO = SIGIO;
    __ss_SIGIOT = SIGIOT;
    __ss_SIGKILL = SIGKILL;
    __ss_SIGPIPE = SIGPIPE;
    __ss_SIGPROF = SIGPROF;
    __ss_SIGQUIT = SIGQUIT;
    __ss_SIGSEGV = SIGSEGV;
    __ss_SIGSTOP = SIGSTOP;
    __ss_SIGSYS = SIGSYS;
    __ss_SIGTERM = SIGTERM;
    __ss_SIGTRAP = SIGTRAP;
    __ss_SIGTSTP = SIGTSTP;
    __ss_SIGTTIN = SIGTTIN;
    __ss_SIGTTOU = SIGTTOU;
    __ss_SIGURG = SIGURG;
    __ss_SIGUSR1 = SIGUSR1;
    __ss_SIGUSR2 = SIGUSR2;
    __ss_SIGVTALRM = SIGVTALRM;
    __ss_SIGWINCH = SIGWINCH;
    __ss_SIGXCPU = SIGXCPU;
    __ss_SIGXFSZ = SIGXFSZ;
//    __ss_SIG_DFL = SIG_DFL;
//    __ss_SIG_IGN = SIG_IGN;

}

} // module namespace

