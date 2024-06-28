/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "struct.hpp"
#include <stdio.h>

namespace __struct__ {

void *buffy;
class_ *cl_error;
bool little_endian;


unsigned int get_itemsize(char order, char c) {
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
//            case 'n': return sizeof(ssize_t); MSVC?
            case 'N': return sizeof(size_t);
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

__ss_int padding(char o, __ss_int pos, unsigned int itemsize) {
    unsigned int upos = (unsigned int)pos;

    if(sizeof(void *) == 4) {
#ifndef WIN32
        if(itemsize == 8)
            itemsize = 4;
#endif
    }
    if(o == '@' and upos % itemsize)
        return (__ss_int)(itemsize - (upos % itemsize));
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
        unsigned long long c2 = (unsigned char)(data->unit[(size_t)(*pos+(__ss_int)i)]);
        if(swap_endian(o))
            result |= (c2 << 8*(itemsize-i-1));
        else
            result |= (c2 << 8*i);
    }
    *pos += (__ss_int)itemsize;
    if(c == 'h')
        return (short)result;
    return (__ss_int)result;
}

bytes *unpack_bytes(char, char c, unsigned int d, bytes *data, __ss_int *pos) {
    bytes *result = 0;
    unsigned int len;
    switch(c) {
        case 'c':
             result = new bytes(__char_cache[(unsigned char)(data->unit[(size_t)(*pos)])]->unit);
             break;
        case 's':
             result = new bytes();
             for(unsigned int i=0; i<d; i++)
                 result->unit += data->unit[(size_t)(*pos+(__ss_int)i)];
             break;
        case 'p':
             result = new bytes();
             len = (unsigned char)data->unit[(size_t)(*pos)];
             for(unsigned i=0; i<len; i++)
                 result->unit += data->unit[(size_t)(*pos+(__ss_int)i+1)];
             break;
    }
    *pos += (__ss_int)d;
    result->frozen = 1;
    return result;
}

__ss_bool unpack_bool(char, char, unsigned int d, bytes *data, __ss_int *pos) {
    __ss_bool result;
    if(data->unit[(size_t)(*pos)] == '\x00')
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
            ((char *)buffy)[itemsize-i-1] = data->unit[(size_t)(*pos+(__ss_int)i)];
    else
        for(unsigned int i=0; i<itemsize; i++)
            ((char *)buffy)[i] = data->unit[(size_t)(*pos+(__ss_int)i)];
    if(c == 'f')
        result = *((float *)(buffy));
    else
        result = *((double *)(buffy));
    *pos += (__ss_int)itemsize;
    return result;
}

void unpack_pad(char, char, unsigned int d, bytes *, __ss_int *pos) {
    *pos += (__ss_int)d;
}

__ss_int calcsize(str *fmt) {
    __ss_int result = 0;
    char order = '@';
    unsigned int itemsize;
    __ss_int n = 0;
    __ss_int ndigits = -1;

    for(unsigned int i=0; i<(unsigned int)len(fmt); i++) {
        char c = fmt->unit[i];
        switch(c) {
            case '@':
            case '=':
            case '<':
            case '>':
            case '!':
                order = c;
                break;
            case '0':
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                n = c - '0';
                if(ndigits == -1)
                    ndigits = n;
                else
                    ndigits = 10*ndigits+n;
                break;
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
//            case 'n':
            case 'N':
                itemsize = get_itemsize(order, c);
                if(ndigits == -1)
                    ndigits = 1;
                result += ndigits * (__ss_int)itemsize;
                ndigits = -1;
                result += padding(order, result, itemsize);
                break;
            case 'c':
            case 's':
            case 'p':
            case '?':
            case 'x':
                if(ndigits == -1)
                    ndigits = 1;
                result += ndigits;
                ndigits = -1;
                break;
            case ' ':
            case '\t':
            case '\n':
            case '\r':
            case '\x0b':
            case '\x0c':
                break;
            case 'P':
                throw new error(new str("unsupported 'P' char in struct format"));
            default:
                throw new error(new str("bad char in struct format"));
        }
    }
    return result;
}

__ss_int calcitems(str *fmt) {
    __ss_int result = 0;
    __ss_int n = 0;
    __ss_int ndigits = -1;

    for(unsigned int i=0; i<(unsigned int)len(fmt); i++) {
        char c = fmt->unit[i];
        switch(c) {
            case '@':
            case '=':
            case '<':
            case '>':
            case '!':
                break;
            case '0':
            case '1':
            case '2':
            case '3':
            case '4':
            case '5':
            case '6':
            case '7':
            case '8':
            case '9':
                n = c - '0';
                if(ndigits == -1)
                    ndigits = n;
                else
                    ndigits = 10*ndigits+n;
                break;
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
//            case 'n':
            case 'N':
            case 'c':
            case '?':
                if(ndigits == -1)
                    ndigits = 1;
                result += ndigits;
                ndigits = -1;
                break;
            case 's':
            case 'p':
                result += 1;
                ndigits = -1;
                break;
            case ' ':
            case '\t':
            case '\n':
            case '\r':
            case '\x0b':
            case '\x0c':
                break;
            case 'x':
                ndigits = -1;
                break;
            case 'P':
                throw new error(new str("unsupported 'P' char in struct format"));
            default:
                throw new error(new str("bad char in struct format"));
        }
    }
    return result;
}

void fillbuf_int(char c, __ss_int t, char order, unsigned int itemsize) {
    if(order == '@') {
        switch(c) {
            case 'b': *((signed char *)buffy) = (signed char)t; break;
            case 'B': *((unsigned char *)buffy) = (unsigned char)t; break;
            case 'h': *((short *)buffy) = (short)t; break;
            case 'H': *((unsigned short *)buffy) = (unsigned short)t; break;
            case 'i': *((int *)buffy) = (int)t; break;
            case 'I': *((unsigned int *)buffy) = (unsigned int)t; break;
            case 'l': *((long *)buffy) = (long)t; break;
            case 'L': *((unsigned long *)buffy) = (unsigned long)t; break;
            case 'q': *((long long *)buffy) = (long long)t; break;
            case 'Q': *((unsigned long long *)buffy) = (unsigned long long)t; break;
//            case 'n': *((ssize_t *)buffy) = t; break;
            case 'N': *((size_t *)buffy) = (size_t)t; break;
        }
    } else {
        if(swap_endian(order)) {
            for(int i=(int)itemsize-1; i>=0; i--) {
                ((char *)buffy)[(size_t)i] = (char)(t & 0xff);
                t >>= 8;
            }
        } else {
            for(unsigned int i=0; i<itemsize; i++) {
                ((char *)buffy)[i] = (char)(t & 0xff);
                t >>= 8;
            }
        }
    }
}

void fillbuf_float(char c, double t, char, unsigned int) {
    switch(c) {
        case 'f': *((float *)buffy) = (float)t; break;
        case 'd': *((double *)buffy) = t; break;
    }
}

void __init() {
    cl_error = new class_("error");
    int num = 1;
    little_endian = (*(char *)&num == 1);
    buffy = malloc(8);
}

} // module namespace

