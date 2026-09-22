/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __IO_HPP
#define __IO_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __io__ {

extern class_ *cl_UnsupportedOperation;
class UnsupportedOperation : public OSError {
public:
    UnsupportedOperation(str *msg=0) : OSError(msg) {
        __class__ = cl_UnsupportedOperation;
        /* plain message, like CPython's UnsupportedOperation('fileno') */
        this->__init__(msg);
        __ss_errno = 0;
        strerror = 0;
        filename = 0;
    }
    str *__str__() { return BaseException::__str__(); }
    str *__repr__() { return BaseException::__repr__(); }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OSError; }
#endif
};

class BytesIO : public file_binary {
public:
    __ss_int pos; // TODO size_t
    bytes *s;

    BytesIO(bytes *initial_bytes=NULL) : file_binary(), pos(0), s(initial_bytes ? new bytes(initial_bytes) : new bytes()) {}

    bytes *read(__ss_int n=-1);
    bytes *readline(__ss_int n=-1);
    list<bytes *> *readlines(__ss_int hint=-1);
    __ss_int seek(__ss_int i, __ss_int w=0);
    __ss_int tell() { return pos; }
    __ss_int truncate(__ss_int size=-1);
    void *close() { closed = True; return NULL; }
    __ss_int write(bytes *data);

    bool __error() { return false; }
    bool __eof() { return (pos >= len(s)); }

    bytes *getvalue();
    bytes *read1(__ss_int n=-1) { return read(n); }
    __ss_int readinto(bytes *b);
    __ss_int readinto1(bytes *b) { return readinto(b); }

    __ss_bool readable() { __check_closed(); return True; }
    __ss_bool writable() { __check_closed(); return True; }
    __ss_bool seekable() { __check_closed(); return True; }
    __ss_bool isatty() { __check_closed(); return False; }
    __ss_int __ss_fileno() { throw new UnsupportedOperation(new str("fileno")); }
    void *detach() { throw new UnsupportedOperation(new str("detach")); }
};

class StringIO : public file {
public:
    __ss_int pos; // TODO size_t
    str *s;

    /* newline handling: NULL (None) -> universal: '\r\n' and '\r' written as '\n';
       '' -> no translation, lines end at '\n', '\r' or '\r\n';
       '\n' (default), '\r', '\r\n' -> '\n' written as nl, lines end at nl */
    bool universal, any_ending;
    __GC_STR nl;
    __ss_bool line_buffering; /* always False (only meaningful for TextIOWrapper) */

    StringIO(str *initial_value=NULL) : StringIO(initial_value, new str("\n")) {}
    StringIO(str *initial_value, __ss_void_struct) : StringIO(initial_value) {} /* newline not given */
    StringIO(str *initial_value, str *newline);

    __GC_STR __translate(str *data);
    size_t __line_end(size_t start);

    str *read(__ss_int n=-1);
    str *readline(__ss_int n=-1);
    list<str *> *readlines(__ss_int hint=-1);
    __ss_int seek(__ss_int i, __ss_int w=0);
    __ss_int tell() { return pos; }
    __ss_int truncate(__ss_int size=-1);
    void *close() { closed = True; return NULL; }
    __ss_int write(str *data);

    bool __error() { return false; }
    bool __eof() { return (pos >= len(s)); }

    str *getvalue();

    void *flush() { return NULL; } /* CPython: no closed check here */

    __ss_bool readable() { __check_closed(); return True; }
    __ss_bool writable() { __check_closed(); return True; }
    __ss_bool seekable() { __check_closed(); return True; }
    __ss_bool isatty() { __check_closed(); return False; }
    __ss_int __ss_fileno() { throw new UnsupportedOperation(new str("fileno")); }
    void *detach() { throw new UnsupportedOperation(new str("detach")); }
};

extern const __ss_int DEFAULT_BUFFER_SIZE;

/* SEEK_SET/SEEK_CUR/SEEK_END are in shedskin's reserved-identifier list
   (they collide with stdio.h macros), so the compiler emits __ss_-prefixed
   references for them; declare them under those names accordingly. */
extern const __ss_int __ss_SEEK_SET, __ss_SEEK_CUR, __ss_SEEK_END;

/* shedskin always runs in UTF-8 mode (sys.flags.utf8_mode == 1), so the
   default is 'utf-8' rather than 'locale'; stacklevel only affects the
   EncodingWarning that CPython emits under -X warn_default_encoding. */
str *text_encoding(str *encoding, __ss_int stacklevel=2);

void __init();

} // module namespace
#endif
