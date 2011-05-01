#include "struct.hpp"
#include <stdio.h>

namespace __struct__ {

__ss_int unpack_one(str *s, __ss_int idx, __ss_int count, __ss_int endian) {
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


__ss_int unpack_int(char o, char c, int d, str *data, __ss_int *pos) {
    __ss_int result;
    switch(c) {
        case 'H':
            result = unpack_one(data, *pos, 2, 1);
             *pos += 2;
            break;
        case 'I':
            result = unpack_one(data, *pos, 4, 1);
             *pos += 4;
            break;
        case 'B':
            result = unpack_one(data, *pos, 1, 1);
             *pos += 1;
            break;
    }
    return result;
}

str * unpack_str(char o, char c, int d, str *data, __ss_int *pos) {
    str *result = new str(data->unit.substr(*pos, d));
    *pos += d;
    return result;
}

__ss_int calcsize(str *fmt) {
    return 42;

}

void __init() {

}

} // module namespace

