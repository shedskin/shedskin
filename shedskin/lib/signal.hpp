#ifndef __SIGNAL_HPP
#define __SIGNAL_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __signal__ {

extern str *__name__;
extern __ss_int __ss_SIGABRT, __ss_SIGALRM, __ss_SIGBUS, __ss_SIGCHLD, __ss_SIGCLD, __ss_SIGCONT, __ss_SIGFPE, __ss_SIGHUP, __ss_SIGILL, __ss_SIGINT, __ss_SIGIO, __ss_SIGIOT, __ss_SIGKILL, __ss_SIGPIPE, __ss_SIGPOLL, __ss_SIGPROF, __ss_SIGPWR, __ss_SIGQUIT, __ss_SIGRTMAX, __ss_SIGRTMIN, __ss_SIGSEGV, __ss_SIGSTOP, __ss_SIGSYS, __ss_SIGTERM, __ss_SIGTRAP, __ss_SIGTSTP, __ss_SIGTTIN, __ss_SIGTTOU, __ss_SIGURG, __ss_SIGUSR1, __ss_SIGUSR2, __ss_SIGVTALRM, __ss_SIGWINCH, __ss_SIGXCPU, __ss_SIGXFSZ; //, __ss_SIG_DFL, __ss_SIG_IGN;

void __init();

} // module namespace
#endif
