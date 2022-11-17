/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __IO_HPP
#define __IO_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __io__ {

class BytesI : public file_binary {
public:
    __ss_int pos;
    bytes *s;

    BytesI(bytes *s=NULL) : file_binary(), pos(0), s(s ? s : new bytes()) {}

    bytes * read(int n=-1);
    bytes * readline(int n=-1);
    void *seek(__ss_int i, __ss_int w=0);
    __ss_int tell() { return pos; }
    void *truncate(int size=-1) { 
        s->unit.resize(size == -1 ? pos : size); 
        return NULL;
    }
    void *write(bytes* data);

    bool __error() { return false; }
    bool __eof() { return (pos >= len(s)); }
};

BytesI *BytesIO(bytes *s=0);

extern bytes *default_0;

void __init();

} // module namespace
#endif
