/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "termios.hpp"

#include <errno.h>
#include <string.h>

namespace __termios__ {

str *__name__;
class_ *cl_error, *cl_cclist, *cl_tcattrs;

__ss_int __ss_TCSANOW, __ss_TCSADRAIN, __ss_TCSAFLUSH, __ss_NCCS, __ss_VMIN, __ss_VTIME, __ss_ECHO, __ss_ICANON;

static void __throw_error() {
    throw new error(new str(strerror(errno)));
}

/* cclist */

__ss_int cclist::__len__() {
    return NCCS;
}

bytes *cclist::__getitem__(__ss_int i) {
    i = __wrap(this, i, "list index out of range");
    return __byte_cache[cc[i]];
}

void *cclist::__setitem__(__ss_int i, __ss_int v) {
    i = __wrap(this, i, "list assignment index out of range");
    cc[i] = (cc_t)v; /* like CPython: no range check */
    return NULL;
}

void *cclist::__setitem__(__ss_int i, bytes *v) {
    i = __wrap(this, i, "list assignment index out of range");
    if(v->__len__() != 1)
        throw new TypeError(new str("tcsetattr: elements of attributes must be characters or integers"));
    cc[i] = (cc_t)v->unit[0];
    return NULL;
}

__ss_bool cclist::__eq__(pyobj *p) {
    if(!p || p->__class__ != cl_cclist)
        return False;
    return __mbool(memcmp(cc, ((cclist *)p)->cc, sizeof(cc)) == 0);
}

__ss_bool cclist::__ne__(pyobj *p) {
    return __mbool(!__eq__(p));
}

str *cclist::__repr__() {
    str *r = new str("[");
    for(int i = 0; i < NCCS; i++) {
        if(i)
            r = r->__add__(new str(", "));
        r = r->__add__(repr(__byte_cache[cc[i]]));
    }
    return r->__add__(new str("]"));
}

cclist *cclist::__copy__() {
    cclist *c = new cclist();
    memcpy(c->cc, cc, sizeof(cc));
    return c;
}

cclist *cclist::__deepcopy__(dict<void *, pyobj *> *memo) {
    cclist *c = __copy__();
    memo->__setitem__(this, c);
    return c;
}

/* tcattrs */

__ss_int tcattrs::__len__() {
    return 7;
}

__ss_int tcattrs::__getitem__(__ss_int i) {
    i = __wrap(this, i, "list index out of range");
    if(i == 6)
        throw new TypeError(new str("termios attributes: index 6 holds the control characters; use a literal 6, CC or tty.CC as index"));
    return flags[i];
}

cclist *tcattrs::__getcc__() {
    return cc;
}

void *tcattrs::__setitem__(__ss_int i, __ss_int v) {
    i = __wrap(this, i, "list assignment index out of range");
    if(i == 6)
        throw new TypeError(new str("termios attributes: index 6 holds the control characters"));
    flags[i] = v;
    return NULL;
}

void *tcattrs::__setitem__(__ss_int i, cclist *v) {
    i = __wrap(this, i, "list assignment index out of range");
    if(i != 6)
        throw new TypeError(new str("termios attributes: only index 6 holds the control characters"));
    cc = v;
    return NULL;
}

__ss_bool tcattrs::__eq__(pyobj *p) {
    if(!p || p->__class__ != cl_tcattrs)
        return False;
    tcattrs *b = (tcattrs *)p;
    for(int i = 0; i < 6; i++)
        if(flags[i] != b->flags[i])
            return False;
    return cc->__eq__(b->cc);
}

__ss_bool tcattrs::__ne__(pyobj *p) {
    return __mbool(!__eq__(p));
}

str *tcattrs::__repr__() {
    str *r = new str("[");
    for(int i = 0; i < 6; i++)
        r = r->__add__(__str(flags[i]))->__add__(new str(", "));
    return r->__add__(repr(cc))->__add__(new str("]"));
}

tcattrs *tcattrs::__copy__() {
    tcattrs *c = new tcattrs();
    memcpy(c->flags, flags, sizeof(flags));
    c->cc = cc; /* shallow, like copy.copy of a CPython list */
    return c;
}

tcattrs *tcattrs::__deepcopy__(dict<void *, pyobj *> *memo) {
    tcattrs *c = new tcattrs();
    memo->__setitem__(this, c);
    memcpy(c->flags, flags, sizeof(flags));
    c->cc = __deepcopy(cc, memo);
    return c;
}

/* functions */

tcattrs *__tcgetattr(int fd) {
    struct termios mode;
    if(::tcgetattr(fd, &mode) == -1)
        __throw_error();
    tcattrs *a = new tcattrs();
    a->flags[0] = (__ss_int)mode.c_iflag;
    a->flags[1] = (__ss_int)mode.c_oflag;
    a->flags[2] = (__ss_int)mode.c_cflag;
    a->flags[3] = (__ss_int)mode.c_lflag;
    a->flags[4] = (__ss_int)cfgetispeed(&mode);
    a->flags[5] = (__ss_int)cfgetospeed(&mode);
    memcpy(a->cc->cc, mode.c_cc, sizeof(mode.c_cc));
    return a;
}

void *__tcsetattr(int fd, __ss_int when, tcattrs *attributes) {
    struct termios mode;
    if(::tcgetattr(fd, &mode) == -1) /* fill in fields we don't expose */
        __throw_error();
    mode.c_iflag = (tcflag_t)attributes->flags[0];
    mode.c_oflag = (tcflag_t)attributes->flags[1];
    mode.c_cflag = (tcflag_t)attributes->flags[2];
    mode.c_lflag = (tcflag_t)attributes->flags[3];
    memcpy(mode.c_cc, attributes->cc->cc, sizeof(mode.c_cc));
    if(cfsetispeed(&mode, (speed_t)attributes->flags[4]) == -1)
        __throw_error();
    if(cfsetospeed(&mode, (speed_t)attributes->flags[5]) == -1)
        __throw_error();
    if(::tcsetattr(fd, (int)when, &mode) == -1)
        __throw_error();
    return NULL;
}

void __init() {
    __name__ = new str("termios");
    cl_error = new class_("error");
    cl_cclist = new class_("list");
    cl_tcattrs = new class_("list");

    __ss_TCSANOW = TCSANOW;
    __ss_TCSADRAIN = TCSADRAIN;
    __ss_TCSAFLUSH = TCSAFLUSH;
    __ss_NCCS = NCCS;
    __ss_VMIN = VMIN;
    __ss_VTIME = VTIME;
    __ss_ECHO = ECHO;
    __ss_ICANON = ICANON;
}

} // module namespace
