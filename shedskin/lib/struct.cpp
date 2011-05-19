#include "struct.hpp"
#include <stdio.h>

namespace __struct__ {

__GC_STRING ordering;

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
            result = unpack_one(data, *pos, 2, o=='>');
             *pos += 2;
            break;
        case 'I':
            result = unpack_one(data, *pos, 4, o=='>');
             *pos += 4;
            break;
        case 'B':
            result = unpack_one(data, *pos, 1, o=='>');
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
__ss_bool unpack_bool(char o, char c, int d, str *data, __ss_int *pos) {
    return True;
}

double unpack_float(char o, char c, int d, str *data, __ss_int *pos) {
    return 3.141;
}

__ss_int calcsize(str *fmt) {
    __ss_int result = 0;
    str *digits = new str();
    for(unsigned int i=0; i<len(fmt); i++) {
        char c = fmt->unit[i];
        if(ordering.find(c) != -1)
            continue;
        if(::isdigit(c)) {
            digits->unit += c;
        } else {
            int ndigits = 1;
            if(len(digits)) {
                ndigits = __int(digits);
                digits = new str();
            }
            switch(c) {
                case 'H': result += 2*ndigits; break;
                case 'I': result += 4*ndigits; break;
                case 'B': result += ndigits; break;
                case 's': result += ndigits; break;
            }
        }
    }
    return result;
}

str *pack(int n, str *fmt, ...) {
    pyobj *arg;
    va_list args;
    va_start(args, fmt);
    str *result = new str();
    str *digits = new str();
    for(unsigned int i=0, j=0; i<n; j++) {
        char c = fmt->unit[j];
        if(ordering.find(c) != -1)
            continue;
        if(::isdigit(c)) {
            digits->unit += c;
            continue;
        }
        int ndigits = 1;
        if(len(digits)) {
            ndigits = __int(digits);
            digits = new str();
        }
        switch(c) {
            case 'H': 
                arg = va_arg(args, pyobj *);
                if(arg->__class__ == cl_int_) {
                    result->unit += (char)((((int_ *)(arg))->unit) & 0xff);
                    result->unit += (char)(((((int_ *)(arg))->unit) >> 8) & 0xff);
                }
                break;
            case 'I': 
                arg = va_arg(args, pyobj *);
                if(arg->__class__ == cl_int_) {
                    result->unit += (char)(((((int_ *)(arg))->unit) >> 24) & 0xff);
                    result->unit += (char)(((((int_ *)(arg))->unit) >> 16) & 0xff);
                    result->unit += (char)(((((int_ *)(arg))->unit) >> 8) & 0xff);
                    result->unit += (char)((((int_ *)(arg))->unit) & 0xff);
                }
                break;
            case 'c': 
                arg = va_arg(args, pyobj *);
                if(arg->__class__ == cl_str_)
                    result->unit += ((str *)(arg))->unit[0];
                break;
            case 'p': 
                arg = va_arg(args, pyobj *);
                if(arg->__class__ == cl_str_) {
                    int len = ((str *)(arg))->__len__()-1;
                    result->unit += (unsigned char)(len);
                    for(unsigned int j=0; j<len; j++)
                        result->unit += ((str *)(arg))->unit[j];
                }
                break;
            case 'L': 
                for(unsigned int j=0; j<ndigits; j++) {
                    arg = va_arg(args, pyobj *);
                    if(arg->__class__ == cl_int_) {
                        result->unit += (char)(((((int_ *)(arg))->unit) >> 24) & 0xff);
                        result->unit += (char)(((((int_ *)(arg))->unit) >> 16) & 0xff);
                        result->unit += (char)(((((int_ *)(arg))->unit) >> 8) & 0xff);
                        result->unit += (char)((((int_ *)(arg))->unit) & 0xff);
                    }
                }
                break;
            case 'b': 
                for(unsigned int j=0; j<ndigits; j++) {
                    arg = va_arg(args, pyobj *);
                    if(arg->__class__ == cl_int_)
                        result->unit += (char)((((int_ *)(arg))->unit) & 0xff);
                }
                break;
        }
        i++;
    }
    va_end(args);
    return result;
}

void __init() {
    ordering = "@<>!=";
}

} // module namespace

