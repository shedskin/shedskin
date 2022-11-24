/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __SELECT_HPP
#define __SELECT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __select__ {

extern str *__name__;

template<class A, class B, class C> tuple2<list<__ss_int> *, list<__ss_int> *> *select(A *rFDs, B *wFDs, C *xFDs, double timeout) {
    __ss_int __2, __6, __10;
    A *__0;
    typename A::for_in_unit FDa;
    typename A::for_in_loop __3;
    B *__4;
    typename B::for_in_unit FDb;
    typename B::for_in_loop __7;
    C *__8;
    typename C::for_in_unit FDc;
    typename C::for_in_loop __11;
    list<__ss_int> *rrFDs, *rwFDs, *rxFDs;
    __ss_int FD;
    fd_set lrFDs;
    fd_set lwFDs;
    fd_set lxFDs;
    int maxFD = 0;
    struct timeval ltimeout;
    FD_ZERO(&lrFDs);
    FD_ZERO(&lwFDs);
    FD_ZERO(&lxFDs);
    FOR_IN(FDa,rFDs,0,2,3)
        FD = (intptr_t)FDa;
        if(FD > -1) {
            FD_SET(FD, &lrFDs);
            if(FD > maxFD)
                maxFD = FD;
        }
    END_FOR
    FOR_IN(FDb,wFDs,4,6,7)
        FD = (intptr_t)FDb;
        if(FD > -1) {
            FD_SET(FD, &lwFDs);
            if(FD > maxFD)
                maxFD = FD;
        }
    END_FOR
    FOR_IN(FDc,xFDs,8,10,11)
        FD = (intptr_t)FDc;
        if(FD > -1) {
            FD_SET(FD, &lxFDs);
            if(FD > maxFD)
                maxFD = FD;
        }
    END_FOR
    memset(&ltimeout, 0, sizeof(ltimeout));
    ltimeout.tv_sec = timeout;
    ltimeout.tv_usec = (timeout - floor(timeout))*1E6;
    if(::select(maxFD + 1, &lrFDs, &lwFDs, &lxFDs, (timeout < 0) ? NULL : &ltimeout) == -1) {
        throw new OSError();
    }
    rrFDs = (new list<__ss_int>());
    FOR_IN(FDa,rFDs,0,2,3)
        FD = (intptr_t)FDa;
        if(FD > -1 && FD_ISSET(FD, &lrFDs))
            rrFDs->append(FD);
    END_FOR
    rwFDs = (new list<__ss_int>());
    FOR_IN(FDb,wFDs,4,6,7)
        FD = (intptr_t)FDb;
        if(FD > -1 && FD_ISSET(FD, &lwFDs))
            rwFDs->append(FD);
    END_FOR
    rxFDs = (new list<__ss_int>());
    FOR_IN(FDc,xFDs,8,10,11)
        FD = (intptr_t)FDc;
        if(FD > -1 && FD_ISSET(FD, &lxFDs))
            rxFDs->append(FD);
    END_FOR
    return (new tuple2<list<__ss_int> *, list<__ss_int> *>(3,rrFDs,rwFDs,rxFDs));
}
void __init();

} // module namespace
#endif
