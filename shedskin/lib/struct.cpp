/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "struct.hpp"
#include <stdio.h>

namespace __struct__ {

__GC_STRING ordering;

void *buffy;
class_ *cl_error;
bool little_endian;

static inline bool swap_endian(char o) {
    return (little_endian and (o=='>' or o=='!')) or (not little_endian and o=='<');
}

int get_itemsize(char order, char c) {
    switch(c) {
        case 'c': return 1;
        case 's': return 1;
        case 'p': return 1;
        case '?': return 1;
        case 'x': return 1;
    }
    if(order == '@') {
        switch(c) {
            case 'b': return sizeof(signed char);
            case 'B': return sizeof(unsigned char);
            case 'h': return sizeof(short);
            case 'H': return sizeof(unsigned short);
            case 'i': return sizeof(int);
            case 'I': return sizeof(unsigned int);
            case 'l': return sizeof(long);
            case 'L': return sizeof(unsigned long);
            case 'q': return sizeof(long long);
            case 'Q': return sizeof(unsigned long long);
            case 'f': return sizeof(float);
            case 'd': return sizeof(double);
        }
    } else {
        switch(c) {
            case 'b': return 1;
            case 'B': return 1;
            case 'h': return 2;
            case 'H': return 2;
            case 'i': return 4;
            case 'I': return 4;
            case 'l': return 4;
            case 'L': return 4;
            case 'q': return 8;
            case 'Q': return 8;
            case 'f': return 4;
            case 'd': return 8;
        }
    }
    return 0;
}

int padding(char o, int pos, unsigned int itemsize) {
    if(sizeof(void *) == 4) {
#ifndef WIN32
        if(itemsize == 8)
            itemsize = 4;
#endif
    }
    if(o == '@' and pos % itemsize)
        return itemsize - (pos % itemsize);
    return 0;
}

__ss_int unpack_int(char o, char c, unsigned int d, bytes *data, __ss_int *pos) {
    unsigned long long result;
    unsigned int itemsize = get_itemsize(o, c);
    *pos += padding(o, *pos, itemsize);
    if(d==0)
        return 0;
    result = 0;
    for(unsigned int i=0; i<itemsize; i++) {
        unsigned long long c = (unsigned char)(data->unit[*pos+i]);
        if(swap_endian(o))
            result |= (c << 8*(itemsize-i-1));
        else
            result |= (c << 8*i);
    }
    *pos += itemsize;
    if(c == 'h')
        return (short)result;
    return result;
}

bytes *unpack_bytes(char, char c, unsigned int d, bytes *data, __ss_int *pos) {
    bytes *result = 0;
    unsigned int len;
    switch(c) {
        case 'c':
             result = new bytes(__char_cache[(unsigned char)(data->unit[*pos])]->unit);
             break;
        case 's':
             result = new bytes();
             for(unsigned int i=0; i<d; i++)
                 result->unit += data->unit[*pos+i];
             break;
        case 'p':
             result = new bytes();
             len = data->unit[*pos];
             for(unsigned int i=0; i<len; i++)
                 result->unit += data->unit[*pos+i+1];
             break;
    }
    *pos += d;
    result->frozen = 1;
    return result;
}

__ss_bool unpack_bool(char, char, unsigned int d, bytes *data, __ss_int *pos) {
    __ss_bool result;
    if(data->unit[*pos] == '\x00')
        result = False;
    else
        result = True;
    if(d!=0)
        *pos += 1;
    return result;
}

double unpack_float(char o, char c, unsigned int d, bytes *data, __ss_int *pos) {
    double result;
    unsigned int itemsize = get_itemsize(o, c);
    *pos += padding(o, *pos, itemsize);
    if(d==0)
        return 0;
    if(swap_endian(o))
        for(unsigned int i=0; i<itemsize; i++)
            ((char *)buffy)[itemsize-i-1] = data->unit[*pos+i];
    else
        for(unsigned int i=0; i<itemsize; i++)
            ((char *)buffy)[i] = data->unit[*pos+i];
    if(c == 'f')
        result = *((float *)(buffy));
    else
        result = *((double *)(buffy));
    *pos += itemsize;
    return result;
}

void unpack_pad(char, char, unsigned int d, bytes *, __ss_int *pos) {
    *pos += d;
}

__ss_int calcsize(str *fmt) {
    __ss_int result = 0;
    str *digits = new str();
    char order = '@';
    unsigned int itemsize;
    for(unsigned int i=0; i<(unsigned int)len(fmt); i++) {
        char c = fmt->unit[i];
        if(ordering.find(c) != std::string::npos) {
            order = c;
            continue;
        }
        if(::isdigit(c)) {
            digits->unit += c;
            continue;
        }
        unsigned int ndigits = 1;
        if(len(digits)) {
            ndigits = __int(digits);
            digits = new str();
        }
        itemsize = get_itemsize(order, c);
        switch(c) {
            case 'b': 
            case 'B': 
            case 'h': 
            case 'H': 
            case 'i':
            case 'I': 
            case 'l':
            case 'L':
            case 'q': 
            case 'Q':
            case 'd': 
            case 'f':
                result += padding(order, result, itemsize);
            case 'c':
            case 's':
            case 'p':
            case '?':
            case 'x':
                break;
            case 'P':
                throw new error(new str("unsupported 'P' char in struct format"));
            default:
                throw new error(new str("bad char in struct format"));
        }
        result += ndigits * itemsize;
    }
    return result;
}

void fillbuf(char c, __ss_int t, char order, unsigned int itemsize) {
    if(order == '@') {
        switch(c) {
            case 'b': *((signed char *)buffy) = t; break;
            case 'B': *((unsigned char *)buffy) = t; break;
            case 'h': *((short *)buffy) = t; break;
            case 'H': *((unsigned short *)buffy) = t; break;
            case 'i': *((int *)buffy) = t; break;
            case 'I': *((unsigned int *)buffy) = t; break;
            case 'l': *((long *)buffy) = t; break;
            case 'L': *((unsigned long *)buffy) = t; break;
            case 'q': *((long long *)buffy) = t; break;
            case 'Q': *((unsigned long long *)buffy) = t; break;
        }
    } else {
        if(swap_endian(order)) {
            for(int i=itemsize-1; i>=0; i--) {
                ((char *)buffy)[i] = (unsigned char)(t & 0xff);
                t >>= 8;
            }
        } else {
            for(unsigned int i=0; i<itemsize; i++) {
                ((char *)buffy)[i] = (unsigned char)(t & 0xff);
                t >>= 8;
            }
        }
    }
}

void fillbuf2(char c, double t, char, unsigned int) {
    switch(c) {
        case 'f': *((float *)buffy) = t; break;
        case 'd': *((double *)buffy) = t; break;
    }
}

bytes *pack(str *fmt, va_list args) {
    pyobj *arg;
    bytes *result = new bytes();
    char order = '@';
    str *digits = new str();
    int pos=0;
    unsigned int itemsize, pad;
    unsigned int fmtlen = fmt->__len__();
    bytes *strarg;
    int pascal_ff = 0;
    for(unsigned int j=0; j<fmtlen; j++) {
        char c = fmt->unit[j];
        if(ordering.find(c) != std::string::npos) {
            order = c;
            continue;
        }
        if(::isdigit(c)) {
            digits->unit += c;
            continue;
        }
        unsigned int ndigits = 1;
        if(len(digits)) {
            ndigits = __int(digits);
            digits = new str();
        }
        switch(c) {
            case 'b':
            case 'B':
            case 'h':
            case 'H':
            case 'i':
            case 'I':
            case 'l':
            case 'L':
            case 'q':
            case 'Q':
                itemsize = get_itemsize(order, c);
                pad = padding(order, pos, itemsize);
                for(unsigned int j=0; j<pad; j++) {
                    if(pascal_ff) {
                        result->unit += '\xff';
                        pascal_ff = 0;
                    } else
                        result->unit += '\x00';
                }
                pos += pad;
                for(unsigned int j=0; j<ndigits; j++) {
                    arg = va_arg(args, pyobj *);

                    __ss_int value;
                    if(arg->__class__ == cl_int_)
                        value = ((int_ *)arg)->unit;
                    else if(arg->__class__ == cl_bool)
                        value = ((bool_ *)arg)->unit;
                    else
                        throw new error(new str("required argument is not an integer"));

                    fillbuf(c, value, order, itemsize);

                    for(unsigned int k=0; k<itemsize; k++)
                        result->unit += ((char *)buffy)[k];
                    pos += itemsize;
                }
                if(ndigits)
                    pascal_ff = 0;
                break;
            case 'd':
            case 'f':
                itemsize = get_itemsize(order, c);
                pad = padding(order, pos, itemsize);
                for(unsigned int j=0; j<pad; j++) {
                    if(pascal_ff) {
                        result->unit += '\xff';
                        pascal_ff = 0;
                    } else
                        result->unit += '\x00';
                }
                pos += pad;
                for(unsigned int j=0; j<ndigits; j++) {
                    arg = va_arg(args, pyobj *);
                    double value;
                    if(arg->__class__ == cl_float_)
                        value = ((float_ *)arg)->unit;
                    else if(arg->__class__ == cl_int_)
                        value = ((int_ *)arg)->unit;
                    else
                        throw new error(new str("required argument is not a float"));
                    fillbuf2(c, value, order, itemsize);
                    if(swap_endian(order))
                        for(int i=itemsize-1; i>=0; i--) 
                            result->unit += ((char *)buffy)[i];
                    else 
                        for(unsigned int i=0; i<itemsize; i++) 
                            result->unit += ((char *)buffy)[i];
                    pos += itemsize;
                }
                if(ndigits)
                    pascal_ff = 0;
                break;
            case 'c': 
                for(unsigned int j=0; j<ndigits; j++) {
                    arg = va_arg(args, pyobj *);
                    if(arg->__class__ != cl_bytes)
                        throw new error(new str("char format require bytes object of length 1"));
                    strarg = ((bytes *)(arg));
                    unsigned int len = strarg->__len__();
                    if(len != 1)
                        throw new error(new str("char format require bytes object of length 1"));
                    result->unit += strarg->unit[0];
                    pos += 1;
                }
                if(ndigits)
                    pascal_ff = 0;
                break;
            case 'p': 
                arg = va_arg(args, pyobj *);
                if(arg->__class__ != cl_bytes)
                    throw new error(new str("argument for 'p' must be a bytes object"));
                if(ndigits) {
                    strarg = ((bytes *)(arg));
                    unsigned int len = strarg->__len__();
                    if(len+1 > ndigits)
                        len = ndigits-1;
                    result->unit += (unsigned char)(len);
                    for(unsigned int j=0; j<len; j++)
                        result->unit += strarg->unit[j];
                    for(unsigned int j=0; j<ndigits-len-1; j++)
                        result->unit += '\x00';
                    pos += ndigits;
                    pascal_ff = 0;
                }
                else
                    pascal_ff = 1;
                break;
            case 's':
                arg = va_arg(args, pyobj *);
                if(arg->__class__ != cl_bytes)
                    throw new error(new str("argument for 's' must be a bytes object"));
                if(ndigits) {
                    strarg = ((bytes *)(arg));
                    unsigned int len = strarg->__len__();
                    if(len > ndigits)
                        len = ndigits;
                    for(unsigned int j=0; j<len; j++)
                        result->unit += strarg->unit[j];
                    for(unsigned int j=0; j<ndigits-len; j++) {
                        if(!len and pascal_ff) {
                            result->unit += '\xff';
                            pascal_ff = 0;
                        } else 
                            result->unit += '\x00';
                    }
                    pos += ndigits;
                    pascal_ff = 0;
                }
                break;
            case '?':
                for(unsigned int j=0; j<ndigits; j++) {
                    arg = va_arg(args, pyobj *);
                    if(arg->__nonzero__())
                        result->unit += '\x01';
                    else
                        result->unit += '\x00';
                    pos += 1;
                }
                if(ndigits)
                    pascal_ff = 0;
                break;
            case 'x':
                for(unsigned int j=0; j<ndigits; j++) {
                    if(pascal_ff) {
                        result->unit += '\xff';
                        pascal_ff = 0;
                    }
                    else
                        result->unit += '\x00';
                }
                pos += ndigits;
                break;
            case 'P':
                 throw new error(new str("unsupported 'P' char in struct format"));
            default:
                 throw new error(new str("bad char in struct format"));
        }
    }
    return result;
}

bytes *pack(int, str *fmt, ...) {
    va_list args;
    va_start(args, fmt);
    bytes *result = pack(fmt, args);
    va_end(args);
    return result;
}

void pack_into(int n, str *fmt, bytes *buffer, __ss_int offset, ...) {
    va_list args;
    va_start(args, offset);
    bytes *result = pack(fmt, args); // TODO avoid intermediate object
    va_end(args);

    buffer->unit.replace(offset, result->unit.size(), result->unit);
}

void __init() {
    ordering = "@<>!=";
    cl_error = new class_("error");
    int num = 1;
    little_endian = (*(char *)&num == 1);
    buffy = malloc(8);
}

} // module namespace

