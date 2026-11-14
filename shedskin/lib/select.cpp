/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "builtin.hpp"
#include "select.hpp"

#include <stdio.h>
#include <math.h>
#include <errno.h>

#ifndef WIN32
#include <sys/select.h>
#else
#include <winsock2.h>
#endif

namespace __select__ {

str *__name__;
class_ *cl_error;

void __init() {
    __name__ = new str("select");
    cl_error = cl_oserror; /* select.error is OSError */
}

/* as CPython: on windows, the winsock code (e.g. WSAENOTSOCK) is the errno,
   except for the six that are errno values + 10000 (winerror_to_errno) */
void __throw_select_error() {
#ifdef WIN32
    int e = WSAGetLastError();
    int value = e;
    if (e == 10004 || e == 10009 || e == 10013 || e == 10014 || e == 10022 || e == 10024)
        value = e - 10000;
    __throw_oserror_errno(value, value, __add_strs(2, new str("socket error "), __str(e)));
#else
    __throw_oserror();
#endif
}

} // module namespace

