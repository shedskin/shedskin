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

    BytesIO(bytes *initial_bytes=NULL) : file_binary(), pos(0), s(initial_bytes ? initial_bytes : new bytes()) {}

    bytes *read(int n=-1);
    bytes *readline(int n=-1);
    list<bytes *> *readlines(__ss_int hint=-1);
    __ss_int seek(__ss_int i, __ss_int w=0);
    __ss_int tell() { return pos; }
    void *truncate(int size=-1) {
        s->unit.resize((size_t)(size == -1 ? pos : size));
        return NULL;
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

    StringIO(str *initial_value=NULL) : file(), pos(0), s(initial_value ? initial_value : new str()) {}

    str *read(int n=-1);
    str *readline(int n=-1);
    list<str *> *readlines(__ss_int hint=-1);
    __ss_int seek(__ss_int i, __ss_int w=0);
    __ss_int tell() { return pos; }
    void *truncate(int size=-1) {
        s->unit.resize((size_t)(size == -1 ? pos : size));
        return NULL;
    }
    __ss_int write(str *data);

    bool __error() { return false; }
    bool __eof() { return (pos >= len(s)); }

    str *getvalue();
};

extern bytes *default_0;
extern str *default_1;

void __init();

} // module namespace
#endif
