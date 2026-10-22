/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __TERMIOS_HPP
#define __TERMIOS_HPP

#include "builtin.hpp"

#include <termios.h>

using namespace __shedskin__;
namespace __termios__ {

extern str *__name__;
extern class_ *cl_error, *cl_cclist, *cl_tcattrs;

extern __ss_int __ss_TCSANOW, __ss_TCSADRAIN, __ss_TCSAFLUSH, __ss_NCCS, __ss_VMIN, __ss_VTIME, __ss_ECHO, __ss_ICANON;

class error : public Exception {
public:
    error(str *msg=0) : Exception(msg) {
        __class__ = cl_error;
    }
};

/* the control characters of a termios attribute list: 1-byte bytes objects
   when read, ints or 1-byte bytes objects when written (like CPython) */
class cclist : public pyseq<bytes *> {
public:
    cc_t cc[NCCS];

    cclist() {
        __class__ = cl_cclist;
        memset(cc, 0, sizeof(cc));
    }

    __ss_int __len__();
    bytes *__getitem__(__ss_int i);
    void *__setitem__(__ss_int i, __ss_int v);
    void *__setitem__(__ss_int i, bytes *v);
    __ss_bool __eq__(pyobj *p);
    __ss_bool __ne__(pyobj *p);
    str *__repr__();
    cclist *__copy__();
    cclist *__deepcopy__(dict<void *, pyobj *> *memo);
};

/* a termios attribute list: [iflag, oflag, cflag, lflag, ispeed, ospeed, cc].
   attrs[6], attrs[CC] and attrs[tty.CC] translate to __getcc__ */
class tcattrs : public pyobj {
public:
    __ss_int flags[6]; /* iflag, oflag, cflag, lflag, ispeed, ospeed */
    cclist *cc;

    tcattrs() {
        __class__ = cl_tcattrs;
        memset(flags, 0, sizeof(flags));
        cc = new cclist();
    }

    __ss_int __len__();
    __ss_int __getitem__(__ss_int i);
    cclist *__getcc__();
    void *__setitem__(__ss_int i, __ss_int v);
    void *__setitem__(__ss_int i, cclist *v);
    __ss_bool __eq__(pyobj *p);
    __ss_bool __ne__(pyobj *p);
    str *__repr__();
    tcattrs *__copy__();
    tcattrs *__deepcopy__(dict<void *, pyobj *> *memo);
};

/* like CPython, fd is a file descriptor or an object with a fileno() method */
template<class T> inline int __tc_fd(T fd) {
    if constexpr (std::is_pointer_v<T>)
        return (int)fd->__ss_fileno();
    else
        return (int)fd;
}

tcattrs *__tcgetattr(int fd);
void *__tcsetattr(int fd, __ss_int when, tcattrs *attributes);

template<class T> tcattrs *tcgetattr(T fd) {
    return __tcgetattr(__tc_fd(fd));
}

template<class T> void *tcsetattr(T fd, __ss_int when, tcattrs *attributes) {
    return __tcsetattr(__tc_fd(fd), when, attributes);
}

void __init();

} // module namespace
#endif
