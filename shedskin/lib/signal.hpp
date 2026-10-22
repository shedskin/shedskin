/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __SIGNAL_HPP
#define __SIGNAL_HPP

#include "builtin.hpp"
#include <functional>

using namespace __shedskin__;
namespace __signal__ {

extern str *__name__;
extern __ss_int __ss_SIGABRT, __ss_SIGALRM, __ss_SIGBUS, __ss_SIGCHLD, __ss_SIGCLD, __ss_SIGCONT, __ss_SIGFPE, __ss_SIGHUP, __ss_SIGILL, __ss_SIGINT, __ss_SIGIO, __ss_SIGIOT, __ss_SIGKILL, __ss_SIGPIPE, __ss_SIGPOLL, __ss_SIGPROF, __ss_SIGPWR, __ss_SIGQUIT, __ss_SIGRTMAX, __ss_SIGRTMIN, __ss_SIGSEGV, __ss_SIGSTOP, __ss_SIGSYS, __ss_SIGTERM, __ss_SIGTRAP, __ss_SIGTSTP, __ss_SIGTTIN, __ss_SIGTTOU, __ss_SIGURG, __ss_SIGUSR1, __ss_SIGUSR2, __ss_SIGVTALRM, __ss_SIGWINCH, __ss_SIGXCPU, __ss_SIGXFSZ, __ss_SIGBREAK; //, __ss_SIG_DFL, __ss_SIG_IGN;

void __init();

/* signal(): the handler runs at the next signal check, see builtin.hpp */

typedef std::function<void(__ss_int)> __handler;
void __set_handler(__ss_int signalnum, __handler *handler);

template<class F> void *signal(__ss_int signalnum, F handler) {
    __set_handler(signalnum, new __handler([handler](__ss_int s) { handler(s, NULL); }));
    return NULL;
}

void *raise_signal(__ss_int signalnum);
str *strsignal(__ss_int signalnum);

} // module namespace
#endif
