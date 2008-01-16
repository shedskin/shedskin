#include <stdio.h>
#include "cStringIO.hpp"

namespace __cStringIO__ {

StringI::StringI(str *s) : file() {
    pos = 0;
    if(s) this->s = s;
    else this->s = new str();

}

int StringI::seek(int i, int w) {
    if(w==0) pos = i;
    else if(w==1) pos += i;
    else pos = len(s)+i;
    endoffile = 0;
    return 0;
}

int StringI::getchar() {
    if(pos == len(s))
        return EOF;
    return s->unit[pos++];
}

int StringI::putchar(int c) {
    if(pos < len(s))
        s->unit[pos] = c;
    else 
        s->unit += c;

    pos++;
    return 0;
}

StringI *StringIO(str *s) {
    return (new StringI(s));

}

void __init() {

}

} // module namespace

