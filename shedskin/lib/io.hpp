/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __IO_HPP
#define __IO_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __io__ {

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
    __ss_int truncate(int size=-1) {
        __ss_int newsize = (size == -1 ? pos : size);
        s->unit.resize((size_t)newsize);
        return newsize;
    }
    __ss_int write(bytes *data);

    bool __error() { return false; }
    bool __eof() { return (pos >= len(s)); }

    bytes *getvalue();
};

class StringIO : public file {
public:
    __ss_int pos; // TODO size_t
    str *s;

    StringIO(str *initial_value=NULL) : file(), pos(0), s(initial_value ? new str(initial_value->unit) : new str()) {}

    str *read(__ss_int n=-1);
    str *readline(__ss_int n=-1);
    list<str *> *readlines(__ss_int hint=-1);
    __ss_int seek(__ss_int i, __ss_int w=0);
    __ss_int tell() { return pos; }
    __ss_int truncate(int size=-1) {
        __ss_int newsize = (size == -1 ? pos : size);
        s->unit.resize((size_t)newsize);
        return newsize;
    }
    __ss_int write(str *data);

    bool __error() { return false; }
    bool __eof() { return (pos >= len(s)); }

    str *getvalue();
};

extern bytes *default_0;
extern str *default_1;

extern const __ss_int DEFAULT_BUFFER_SIZE;

/* SEEK_SET/SEEK_CUR/SEEK_END are in shedskin's reserved-identifier list
   (they collide with stdio.h macros), so the compiler emits __ss_-prefixed
   references for them; declare them under those names accordingly. */
extern const __ss_int __ss_SEEK_SET, __ss_SEEK_CUR, __ss_SEEK_END;

void __init();

} // module namespace
#endif
