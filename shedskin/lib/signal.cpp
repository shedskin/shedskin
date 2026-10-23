/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "signal.hpp"
#include <signal.h>
#include <errno.h>

namespace __signal__ {

str *__name__;
__ss_int __ss_SIGABRT, __ss_SIGALRM, __ss_SIGBUS, __ss_SIGCHLD, __ss_SIGCLD, __ss_SIGCONT, __ss_SIGFPE, __ss_SIGHUP, __ss_SIGILL, __ss_SIGINT, __ss_SIGIO, __ss_SIGIOT, __ss_SIGKILL, __ss_SIGPIPE, __ss_SIGPOLL, __ss_SIGPROF, __ss_SIGPWR, __ss_SIGQUIT, __ss_SIGRTMAX, __ss_SIGRTMIN, __ss_SIGSEGV, __ss_SIGSTOP, __ss_SIGSYS, __ss_SIGTERM, __ss_SIGTRAP, __ss_SIGTSTP, __ss_SIGTTIN, __ss_SIGTTOU, __ss_SIGURG, __ss_SIGUSR1, __ss_SIGUSR2, __ss_SIGVTALRM, __ss_SIGWINCH, __ss_SIGXCPU, __ss_SIGXFSZ, __ss_SIGBREAK; //, __ss_SIG_DFL, __ss_SIG_IGN;
#ifndef WIN32
__ss_int __ss_SIG_BLOCK, __ss_SIG_UNBLOCK, __ss_SIG_SETMASK;
#endif

void __init() {
    __name__ = new str("signal");

    /* Not every constant below is defined on every platform (e.g. most
     * POSIX signals don't exist on Windows, and SIGCLD/SIGPOLL/SIGPWR/
     * SIGRTMAX/SIGRTMIN don't exist on macOS -- nor, for that matter,
     * on several BSDs). Whichever of these are
     * left unassigned by the platform-specific blocks further down
     * must not be allowed to silently read back as 0, since 0 is the
     * real (and meaningful) null signal, not a "does not exist" marker.
     * Sentinel-initialize everything to -1 first so unsupported
     * constants fail loudly/obviously instead of behaving like signal 0. */
    __ss_SIGABRT = __ss_SIGALRM = __ss_SIGBUS = __ss_SIGCHLD = __ss_SIGCLD =
        __ss_SIGCONT = __ss_SIGFPE = __ss_SIGHUP = __ss_SIGILL = __ss_SIGINT =
        __ss_SIGIO = __ss_SIGIOT = __ss_SIGKILL = __ss_SIGPIPE = __ss_SIGPOLL =
        __ss_SIGPROF = __ss_SIGPWR = __ss_SIGQUIT = __ss_SIGRTMAX =
        __ss_SIGRTMIN = __ss_SIGSEGV = __ss_SIGSTOP = __ss_SIGSYS =
        __ss_SIGTERM = __ss_SIGTRAP = __ss_SIGTSTP = __ss_SIGTTIN =
        __ss_SIGTTOU = __ss_SIGURG = __ss_SIGUSR1 = __ss_SIGUSR2 =
        __ss_SIGVTALRM = __ss_SIGWINCH = __ss_SIGXCPU = __ss_SIGXFSZ =
        __ss_SIGBREAK = -1;

    __ss_SIGABRT = SIGABRT;
    __ss_SIGFPE = SIGFPE;
    __ss_SIGILL = SIGILL;
    __ss_SIGINT = SIGINT;
    __ss_SIGSEGV = SIGSEGV;
    __ss_SIGTERM = SIGTERM;

#ifdef WIN32
    __ss_SIGBREAK = SIGBREAK;
#else
#ifdef SIGCLD
    __ss_SIGCLD = SIGCLD;
#endif
#ifdef SIGPOLL
    __ss_SIGPOLL = SIGPOLL;
#endif
#ifdef SIGPWR
    __ss_SIGPWR = SIGPWR;
#endif
#ifdef SIGRTMAX
    __ss_SIGRTMAX = SIGRTMAX;
#endif
#ifdef SIGRTMIN
    __ss_SIGRTMIN = SIGRTMIN;
#endif
    __ss_SIGALRM = SIGALRM;
    __ss_SIGBUS = SIGBUS;
    __ss_SIGCHLD = SIGCHLD;
    __ss_SIGCONT = SIGCONT;
    __ss_SIGHUP = SIGHUP;
    __ss_SIGIO = SIGIO;
    __ss_SIGIOT = SIGIOT;
    __ss_SIGKILL = SIGKILL;
    __ss_SIGPIPE = SIGPIPE;
    __ss_SIGPROF = SIGPROF;
    __ss_SIGQUIT = SIGQUIT;
    __ss_SIGSTOP = SIGSTOP;
    __ss_SIGSYS = SIGSYS;
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
    __ss_SIG_BLOCK = SIG_BLOCK;
    __ss_SIG_UNBLOCK = SIG_UNBLOCK;
    __ss_SIG_SETMASK = SIG_SETMASK;
#endif

}

#ifndef WIN32
void __sigset_add(sigset_t *sigs, __ss_int signalnum) {
    if(signalnum < 1 || signalnum >= NSIG)
        throw new ValueError(__add_strs(5, new str("signal number "), __str(signalnum), new str(" out of range [1; "), __str(NSIG-1), new str("]")));
    sigaddset(sigs, (int)signalnum);
}

set<__ss_int> *__sigset_to_set(sigset_t *sigs) {
    set<__ss_int> *result = new set<__ss_int>();
    for(int s = 1; s < NSIG; s++)
        if(sigismember(sigs, s) == 1)
            result->add(s);
    return result;
}

set<__ss_int> *__pthread_sigmask(__ss_int how, sigset_t *mask) {
    sigset_t previous;
    int err = ::pthread_sigmask((int)how, mask, &previous);
    if(err) {
        errno = err;
        __throw_oserror();
    }
    return __sigset_to_set(&previous);
}

set<__ss_int> *sigpending() {
    sigset_t pending;
    if(::sigpending(&pending) == -1)
        __throw_oserror();
    return __sigset_to_set(&pending);
}

__ss_int __sigwait(sigset_t *sigs) {
    int signalnum;
    int err = ::sigwait(sigs, &signalnum);
    if(err) {
        errno = err;
        __throw_oserror();
    }
    return signalnum;
}
#endif

} // module namespace

