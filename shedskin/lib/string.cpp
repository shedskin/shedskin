#include "string.hpp"
#include <stdio.h>
#include <ctype.h>

namespace __string__ {

str *const_0;

str *ascii_letters, *ascii_uppercase, *ascii_lowercase, *uppercase, *lowercase, *digits, *hexdigits, *octdigits, *printable, *punctuation, *whitespace, *letters;

char trans_table[256];

str *join(pyiter<str *> *a, str *b) {
    if(!b) b = const_0;
    return b->join(a);
}
str *join(pyseq<str *> *a, str *b) {
    if(!b) b = const_0;
    return b->join(a);
}
str *joinfields(pyiter<str *> *a, str *b) { return join(a, b); }
str *joinfields(pyseq<str *> *a, str *b) { return join(a, b); }

__ss_int count(str *a, str *b, __ss_int start) { return count(a, b, start, a->__len__()); }
__ss_int count(str *a, str *b, __ss_int start, __ss_int end) { return a->count(b, start, end); }

__ss_int find(str *s, str *t, __ss_int a) { return find(s, t, a, s->__len__()); }
__ss_int find(str *s, str *t, __ss_int a, __ss_int b) { return s->find(t, a, b); }
__ss_int rfind(str *s, str *t, __ss_int a) { return rfind(s, t, a, s->__len__()); }
__ss_int rfind(str *s, str *t, __ss_int a, __ss_int b) { return s->rfind(t, a, b); }
__ss_int index(str *s, str *t, __ss_int a) { return index(s, t, a, s->__len__()); }
__ss_int index(str *s, str *t, __ss_int a, __ss_int b) { return s->index(t, a, b); }
__ss_int rindex(str *s, str *t, __ss_int a) { return rindex(s, t, a, s->__len__()); }
__ss_int rindex(str *s, str *t, __ss_int a, __ss_int b) { return s->rindex(t, a, b); }

list<str *> *rsplit(str *s, str *sep, __ss_int maxsep) { return s->rsplit(sep, maxsep); }

list<str *> *split(str *s, str *sep, __ss_int c) { return s->split(sep, c); }
list<str *> *splitfields(str *s, str *sep, __ss_int c) { return s->split(sep, c); }

str *replace(str *s, str *a, str *b, __ss_int c) { return s->replace(a, b, c); }
str *translate(str *s, str *table, str *delchars) { return s->translate(table, delchars); }

str *zfill(str *s, __ss_int width) { return s->zfill(width); }
str *upper(str *s) { return s->upper(); }
str *lower(str *s) { return s->lower(); }

str *strip(str *s, str *chars) { return s->strip(chars); }
str *lstrip(str *s, str *chars) { return s->lstrip(chars); }
str *rstrip(str *s, str *chars) { return s->rstrip(chars); }

str *ljust(str *s, __ss_int width, str *fchar) { return s->ljust(width, fchar); }
str *rjust(str *s, __ss_int width, str *fchar) { return s->rjust(width, fchar); }

str *expandtabs(str *s, __ss_int width) {
    return s->expandtabs(width);
}

str *maketrans(str *frm, str *to) {
    str *r = new str(trans_table, 256);
    __ss_int l = len(frm);
    if(l != len(to))
        throw new ValueError(new str("maketrans arguments must have same length"));
    for(__ss_int i=0; i<l; i++)
        r->unit[(unsigned char)frm->unit[i]] = to->unit[i];
    return r;
}

str *capitalize(str *s) {
    return s->capitalize();
}

str *capwords(str *s, str *sep) {
    list<str *> *__3 = s->split(sep);
    list<str *> *result = new list<str *>();
    __ss_int __2;

    result->resize(len(__3));
    str *e;
    FOR_IN_SEQ(e,__3,3,2)
        result->units[__2] = e->capitalize();
    END_FOR

    if(!sep) sep = const_0;
    return sep->join(result);
}

str *swapcase(str *s) {
    return s->swapcase();
}

str *center(str *s, __ss_int w, str *sep) {
    return s->center(w, sep);
}

__ss_int atoi(str *s, __ss_int base) {
    return __int(s, base);
}

__ss_int atol(str *s, __ss_int base) {
    char c = s->unit[len(s)-1];
    if(c=='l' || c=='L')
        s = s->__slice__(7, 0, -1, 1);

    return __int(s, base);
}

double atof(str *s) {
    return __float(s);
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

    lowercase = ascii_lowercase = __ctype_str(islower);
    uppercase = ascii_uppercase = __ctype_str(isupper);
    letters = ascii_letters = lowercase->__add__(uppercase);

    digits = new str("0123456789");
    hexdigits = new str("0123456789abcdefABCDEF");
    octdigits = new str("01234567");

    punctuation = __ctype_str(ispunct);
    whitespace = __ctype_str(isspace);

    printable = __add_strs(5, digits, lowercase, uppercase, punctuation, new str(" \t\n\r\x0b\x0c"));

    for(__ss_int i=0; i<256; i++)
        trans_table[i] = i;

}

} // module namespace

