/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "string.hpp"
#include <stdio.h>
#include <ctype.h>

namespace __string__ {

str *const_0;

str *ascii_letters, *ascii_uppercase, *ascii_lowercase, *hexdigits, *octdigits, *printable, *punctuation, *whitespace, *digits;

str *capwords(str *s, str *sep) {
    list<str *> *__3 = s->split(sep);
    list<str *> *result = new list<str *>();
    result->resize(len(__3));
    str *e;
    list<str *>::for_in_loop __4;
    int __2;
    list<str *> *__1;
    FOR_IN(e,__3,1,2,4)
        result->units[__2] = e->capitalize();
    END_FOR

    if(!sep) sep = const_0;
    return sep->join(result);
}


str *__ctype_str(int (*cfunc)(int)) {
    str *s = new str();
    for(__ss_int i=0; i<256; i++)
        if(cfunc(i))
            s->unit += (char)i;
    return s;
}


void __init() {
    const_0 = new str(" ");

    ascii_lowercase = __ctype_str(islower);
    ascii_uppercase = __ctype_str(isupper);
    ascii_letters = ascii_lowercase->__add__(ascii_uppercase);

    digits = new str("0123456789");
    octdigits = new str("01234567");
    hexdigits = new str("0123456789abcdefABCDEF");

    punctuation = __ctype_str(ispunct);
    whitespace = new str(" \t\n\r\x0b\x0c");

    printable = __add_strs(5, digits, ascii_lowercase, ascii_uppercase, punctuation, whitespace);

}

} // module namespace

