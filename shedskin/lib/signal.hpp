/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __SIGNAL_HPP
#define __SIGNAL_HPP

#include "builtin.hpp"
#include <signal.h>

using namespace __shedskin__;
namespace __signal__ {

extern str *__name__;
extern __ss_int __ss_SIGABRT, __ss_SIGALRM, __ss_SIGBUS, __ss_SIGCHLD, __ss_SIGCLD, __ss_SIGCONT, __ss_SIGFPE, __ss_SIGHUP, __ss_SIGILL, __ss_SIGINT, __ss_SIGIO, __ss_SIGIOT, __ss_SIGKILL, __ss_SIGPIPE, __ss_SIGPOLL, __ss_SIGPROF, __ss_SIGPWR, __ss_SIGQUIT, __ss_SIGRTMAX, __ss_SIGRTMIN, __ss_SIGSEGV, __ss_SIGSTOP, __ss_SIGSYS, __ss_SIGTERM, __ss_SIGTRAP, __ss_SIGTSTP, __ss_SIGTTIN, __ss_SIGTTOU, __ss_SIGURG, __ss_SIGUSR1, __ss_SIGUSR2, __ss_SIGVTALRM, __ss_SIGWINCH, __ss_SIGXCPU, __ss_SIGXFSZ, __ss_SIGBREAK; //, __ss_SIG_DFL, __ss_SIG_IGN;

void __init();

#ifndef WIN32
extern __ss_int __ss_SIG_BLOCK, __ss_SIG_UNBLOCK, __ss_SIG_SETMASK;

/* like CPython, a signal set is given as any iterable of signal numbers,
   and returned as a set */
void __sigset_add(sigset_t *sigs, __ss_int signalnum);
set<__ss_int> *__sigset_to_set(sigset_t *sigs);

template<class A> void __to_sigset(A *signals, sigset_t *sigs) {
    sigemptyset(sigs);
    if constexpr (!std::is_same_v<typename A::for_in_unit, void *>) { /* empty list */
        A *__0;
        __ss_int __1;
        typename A::for_in_loop __2;
        typename A::for_in_unit s;
        FOR_IN(s,signals,0,1,2)
            __sigset_add(sigs, s);
        END_FOR
    }
}

set<__ss_int> *__pthread_sigmask(__ss_int how, sigset_t *mask);

template<class A> set<__ss_int> *pthread_sigmask(__ss_int how, A *mask) {
    sigset_t sigs;
    __to_sigset(mask, &sigs);
    return __pthread_sigmask(how, &sigs);
}

set<__ss_int> *sigpending();

__ss_int __sigwait(sigset_t *sigs);

template<class A> __ss_int sigwait(A *sigset) {
    sigset_t sigs;
    __to_sigset(sigset, &sigs);
    return __sigwait(&sigs);
}
#endif

} // module namespace
#endif
