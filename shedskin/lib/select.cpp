/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include <stdio.h>
#include <math.h>
#include <errno.h>
#include "builtin.hpp"
#include "select.hpp"

#ifndef WIN32
#include <sys/select.h>
#else
#include <winsock2.h>
#endif

namespace __select__ {

str *__name__;

void __init() {
    __name__ = new str("select");
}

} // module namespace

