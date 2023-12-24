/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "struct.hpp"
#include <stdio.h>

namespace __struct__ {

void *buffy;
class_ *cl_error;
bool little_endian;


int get_itemsize(char order, char c) {
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

int padding(char o, unsigned int pos, unsigned int itemsize) {
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
    unsigned int itemsize = (__ss_int)get_itemsize(o, c);
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
    return (__ss_int)result;
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
             len = (unsigned char)data->unit[*pos];
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
                itemsize = get_itemsize(order, c);
                if(ndigits == -1)
                    ndigits = 1;
                result += ndigits * itemsize;
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

void fillbuf_float(char c, double t, char order, unsigned int itemsize) {
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

