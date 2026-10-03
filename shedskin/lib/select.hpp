/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __SELECT_HPP
#define __SELECT_HPP

#include "builtin.hpp"

/* the select() template below is instantiated in user code, so the
   platform headers that provide fd_set/select must be included here,
   not just in select.cpp */
#ifndef WIN32
#include <sys/select.h>
#else
#include <winsock2.h>
#endif

using namespace __shedskin__;
namespace __select__ {

extern str *__name__;

/* like CPython, select() takes file descriptors or objects with a fileno()
   method (sockets, files..), and returns the ready elements themselves */
template<class T> inline __ss_int __select_fd(T x) {
    if constexpr (std::is_same_v<T, void *>)
        return -1; /* element type of an empty list: never reached */
    else if constexpr (std::is_pointer_v<T>)
        return x->__ss_fileno();
    else
        return (__ss_int)x;
}

template<class A> void __select_add(A *fds, fd_set *set, int *maxFD) {
    A *__0;
    __ss_int __1;
    typename A::for_in_loop __2;
    typename A::for_in_unit e;
    FOR_IN(e,fds,0,1,2)
        __ss_int FD = __select_fd(e);
        if(FD < 0)
            throw new ValueError(__add_strs(3, new str("file descriptor cannot be a negative integer ("), __str(FD), new str(")")));
#ifdef WIN32
        /* winsock fd_set holds up to FD_SETSIZE sockets; handle values
           themselves can be arbitrarily large, so limit the count instead */
        if(set->fd_count >= FD_SETSIZE)
            throw new ValueError(new str("too many file descriptors in select()"));
        FD_SET((SOCKET)FD, set);
#else
        if(FD >= FD_SETSIZE)
            throw new ValueError(new str("filedescriptor out of range in select()"));
        FD_SET(FD, set);
#endif
        if(FD > *maxFD)
            *maxFD = (int)FD;
    END_FOR
}

template<class A> list<typename A::for_in_unit> *__select_ready(A *fds, fd_set *set) {
    A *__0;
    __ss_int __1;
    typename A::for_in_loop __2;
    typename A::for_in_unit e;
    list<typename A::for_in_unit> *result = new list<typename A::for_in_unit>();
    FOR_IN(e,fds,0,1,2)
        if(FD_ISSET(__select_fd(e), set))
            result->append(e);
    END_FOR
    return result;
}

/* the result type, as inferred for the select.py model: a homogeneous tuple
   when the three element types are the same, else a tuple3 */
template<class A, class B, class C> using __select_result = std::conditional_t<
    std::is_same_v<A, B> && std::is_same_v<B, C>,
    tuple2<list<A> *, list<A> *>,
    tuple3<list<A> *, list<B> *, list<C> *>>;

template<class A, class B, class C, class D> __select_result<typename A::for_in_unit, typename B::for_in_unit, typename C::for_in_unit> *select(A *rFDs, B *wFDs, C *xFDs, D timeout_) {
    fd_set lrFDs;
    fd_set lwFDs;
    fd_set lxFDs;
    int maxFD = 0;
    struct timeval ltimeout;
    bool has_timeout;
    double timeout;

    if constexpr (std::is_same_v<D, __ss_void_struct>) {
        has_timeout = false;                       // timeout omitted -> block indefinitely
        timeout = 0.0;
    } else {
        has_timeout = true;
        timeout = (double)timeout_;
        if(timeout < 0)
            throw new ValueError(new str("timeout must be non-negative"));
    }

    FD_ZERO(&lrFDs);
    FD_ZERO(&lwFDs);
    FD_ZERO(&lxFDs);
    __select_add(rFDs, &lrFDs, &maxFD);
    __select_add(wFDs, &lwFDs, &maxFD);
    __select_add(xFDs, &lxFDs, &maxFD);

    memset(&ltimeout, 0, sizeof(ltimeout));
    ltimeout.tv_sec = timeout;
    ltimeout.tv_usec = (timeout - floor(timeout))*1E6;

    if(::select(maxFD + 1, &lrFDs, &lwFDs, &lxFDs, has_timeout ? &ltimeout : NULL) == -1) {
#ifdef WIN32
        throw new OSError(); /* winsock: WSAGetLastError(), not errno */
#else
        __throw_oserror(); /* e.g. EINTR -> InterruptedError */
#endif
    }

    return new __select_result<typename A::for_in_unit, typename B::for_in_unit, typename C::for_in_unit>(3,
        __select_ready(rFDs, &lrFDs), __select_ready(wFDs, &lwFDs), __select_ready(xFDs, &lxFDs));
}
void __init();

} // module namespace
#endif
