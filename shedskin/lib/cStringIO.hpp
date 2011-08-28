/* Copyright 2005-2011 Mark Dufour and contributors; License MIT (See LICENSE) */

#ifndef __CSTRINGIO_HPP
#define __CSTRINGIO_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __cStringIO__ {

class StringI : public file {
public:
    __ss_int pos;
    str *s;

    StringI(str *s=NULL) : file(), pos(0), s(s ? s : new str()) {}

    str * read(int n=-1);
    str * readline(int n=-1);
    void *seek(__ss_int i, __ss_int w=0);
    __ss_int tell() { return pos; }
    void *truncate(int size=-1) { 
        s->unit.resize(size == -1 ? pos : size); 
        return NULL;
    }
    void *write(str* data);

    bool __error() { return false; }
    bool __eof() { return (pos >= len(s)); }
};

StringI *StringIO(str *s=0);

void __init();

} // module namespace
#endif
