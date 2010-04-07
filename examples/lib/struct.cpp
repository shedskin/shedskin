#include "struct.hpp"
#include <stdio.h>

namespace __struct__ {

str *r;
tuple2<__ss_int, __ss_int> *t;

str *pack(__ss_int x, __ss_int count, __ss_int endian) {
    str *r = new str("");
    for(int i=0; i<count; i++) {
        if(endian)
            r->unit += (unsigned char)((x >> 8*(count-i-1)) & 255);
        else
            r->unit += (unsigned char)((x >> 8*i) & 255);

    }

    return r;
}

__ss_int unpack(str *s, __ss_int idx, __ss_int count, __ss_int endian) {
    unsigned int r = 0;

    for(int i=0; i<count; i++) {
        unsigned char c = s->__getitem__(i+idx)->unit[0];
        if (endian)
            r += (c << 8*(count-i-1));
        else
            r += (c << 8*i);

    }

    return r;
}

void plemp(str *fmt, pyseq<__ss_int> *seq, str *s) {
    if(seq) 
        r = new str("");
    else
        t = new tuple2<__ss_int, __ss_int>();

    int endian = 1; // 0: little, 1: big

    int j = 0;
    for(int i=0; i<len(fmt); i++) {
        char c = fmt->__getitem__(i)->unit[0];

        if(c == '<') 
             endian = 0;
        else if(c == '>') 
             endian = 1;
        else if(c == 'H') {
            if(seq) {
                r = r->__add__(pack(seq->__getitem__(j), 2, endian));
                //printf("pack H %d\n", seq->__getitem__(j));
                j++;
            }
            else {
                //printf("unpack H %s\n", CS(repr(s)));
                t->append(unpack(s, j, 2, endian));
                j += 2;
            }
        }
        else if(c == 'L') {
            if(seq) {
                r = r->__add__(pack(seq->__getitem__(j), 4, endian));
                //printf("pack H %d\n", seq->__getitem__(j));
                j++;
            }
            else {
                //printf("unpack H %s\n", CS(repr(s)));
                t->append(unpack(s, j, 4, endian));
                j += 4;
            }
        }
        else if(c == 'B') {
            if(seq) {
                r = r->__add__(pack(seq->__getitem__(j), 1, endian));
                //printf("pack B %d\n", seq->__getitem__(j));
                j++;
            }
            else {
                //printf("unpack B %s\n", CS(repr(s)));
                t->append(unpack(s, j, 1, endian));
                j += 1;
            }
        }
        else { // pad bytes
            if(seq) {
                r = r->__add__((new str("\0", 1))->__mul__(c-'0'));
                //printf("pad %d\n", c-'0');
            }
            else {
                //printf("skip %c\n", c);
                j += (c-'0');
            }

            i++;
        }

    }
}

str *pack_ints(str *fmt, pyseq<__ss_int> *s) {
    plemp(fmt, s, 0);
    return r;
}

tuple2<__ss_int, __ss_int> *unpack_ints(str *fmt, str *s) {
    plemp(fmt, 0, s);
    return t;
}

void __init() {

}

} // module namespace

