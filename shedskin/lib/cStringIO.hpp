#ifndef __CSTRINGIO_HPP
#define __CSTRINGIO_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __cStringIO__ {

class StringI : public file {
public:
    __ss_int pos;
    str *s;

    StringI(str *s);

    int getchar();
    void *putchar(int c);
    void *seek(__ss_int i, __ss_int w=0);
};


StringI *StringIO(str *s=0);

void __init();

} // module namespace
#endif
