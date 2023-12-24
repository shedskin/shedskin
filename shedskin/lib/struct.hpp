/* Copyright 2005-2023 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __STRUCT_HPP
#define __STRUCT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __struct__ {

extern void *buffy;

extern class_ *cl_error;
class error : public Exception {
public:
    error(str *msg=0) : Exception(msg) {
        __class__ = cl_error;
    }
};


extern bool little_endian;

static inline bool swap_endian(char o) {
    return (little_endian and (o=='>' or o=='!')) or (not little_endian and o=='<');
}

__ss_int calcsize(str *fmt);
__ss_int calcitems(str *fmt);
int padding(char o, unsigned int pos, unsigned int itemsize);

__ss_int unpack_int(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
bytes * unpack_bytes(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
__ss_bool unpack_bool(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
double unpack_float(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
void unpack_pad(char o, char c, unsigned int d, bytes *data, __ss_int *pos);

int get_itemsize(char order, char c);

void fillbuf_int(char c, __ss_int t, char order, unsigned int itemsize);
void fillbuf_float(char c, __ss_float t, char order, unsigned int itemsize);

/* pack int */

template<class T> void __pack_int(char c, T t, char order, unsigned int itemsize) {
    throw new error(new str("required argument is not an integer"));
}
template<> inline void __pack_int(char c, __ss_int t, char order, unsigned int itemsize) {
    fillbuf_int(c, t, order, itemsize);
}
template<> inline void __pack_int(char c, __ss_bool t, char order, unsigned int itemsize) {
    fillbuf_int(c, t, order, itemsize);
}

/* pack float */

template<class T> void __pack_float(char c, T t, char order, unsigned int itemsize) {
    throw new error(new str("required argument is not a float"));
}
template<> inline void __pack_float(char c, __ss_float t, char order, unsigned int itemsize) {
    fillbuf_float(c, t, order, itemsize);
}
template<> inline void __pack_float(char c, __ss_int t, char order, unsigned int itemsize) {
    fillbuf_float(c, (__ss_float)t, order, itemsize);
}

/* pack char */

template<class T> void __pack_char(char c, T t, bytes *result, size_t &pos) {
    throw new error(new str("char format requires a bytes object of length 1"));
}
template<> inline void __pack_char(char c, bytes *b, bytes *result, size_t &pos) {
    if(b->__len__() != 1)
        throw new error(new str("char format requires a bytes object of length 1"));
    result->unit[pos++] = b->unit[0];
}

/* pack str */

template<class T> void __pack_str(char c, T t, bytes *result, size_t &pos, __ss_int ndigits) {
    throw new error(new str("argument for 's' must be a bytes object"));
}
template<> inline void __pack_str(char c, bytes *b, bytes *result, size_t &pos, __ss_int ndigits) {
    __ss_int len = b->__len__();
    if(ndigits == -1)
        ndigits = 1;
    if(len > ndigits)
        len = ndigits;
    for(__ss_int j=0; j<len; j++)
        result->unit[pos++] = b->unit[j];
    for(__ss_int j=0; j<ndigits-len; j++)
        result->unit[pos++] = '\x00';
}

/* pack pascal */

template<class T> void __pack_pascal(char c, T t, bytes *result, size_t &pos, __ss_int ndigits) {
    throw new error(new str("argument for 'p' must be a bytes object"));
}
template<> inline void __pack_pascal(char c, bytes *t, bytes *result, size_t &pos, __ss_int ndigits) {
    if(ndigits == -1)
        ndigits = 1;
    __ss_int len = t->__len__();
    if(len+1 > ndigits)
        len = ndigits-1;
    if(len > 255)
        result->unit[pos++] = (unsigned char)(255);
    else
        result->unit[pos++] = (unsigned char)(len);
    for(__ss_int j=0; j<len; j++)
        result->unit[pos++] = t->unit[j];
    for(__ss_int j=0; j<ndigits-len-1; j++)
        result->unit[pos++] = '\x00';
}

/* pack single arg */

template<class T> void __pack_one(str *fmt, unsigned int fmtlen, unsigned int &j, char &order, bytes *result, size_t &pos, __ss_int &ndigits, T arg) {
    unsigned int itemsize;
    int pad;
    __ss_int n;

    for(; j<fmtlen; j++) {
        char c = fmt->unit[j];
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
                itemsize = get_itemsize(order, c);
                pad = padding(order, (unsigned int)pos, itemsize);
                for(int k=0; k<pad; k++)
                    result->unit[pos++] = '\x00';
                __pack_int(c, arg, order, itemsize);
                for(unsigned int k=0; k<itemsize; k++)
                    result->unit[pos++] = ((char *)buffy)[k];
                if(ndigits == -1 or --ndigits == 0) {
                    j++;
                    ndigits = -1;
                }
                return;

            case 'd':
            case 'f':
                itemsize = get_itemsize(order, c);
                pad = padding(order, (unsigned int)pos, itemsize);
                for(int k=0; k<pad; k++)
                    result->unit[pos++] = '\x00';
                __pack_float(c, arg, order, itemsize);
                if(swap_endian(order))
                    for(int k=(int)itemsize-1; k>=0; k--)
                        result->unit[pos++] = ((char *)buffy)[k];
                else
                    for(unsigned int k=0; k<itemsize; k++)
                        result->unit[pos++] = ((char *)buffy)[k];
                if(ndigits == -1 or --ndigits == 0) {
                    j++;
                    ndigits = -1;
                }
                return;

            case 'c':
                __pack_char(c, arg, result, pos);
                if(ndigits == -1 or --ndigits == 0) {
                    j++;
                    ndigits = -1;
                }
                return;

            case '?':
                if(___bool(arg))
                    result->unit[pos++] = '\x01';
                else
                    result->unit[pos++] = '\x00';
                if(ndigits == -1 or --ndigits == 0) {
                    j++;
                    ndigits = -1;
                }
                return;

            case 's':
                __pack_str(c, arg, result, pos, ndigits);
                j++;
                return;

            case 'p':
                __pack_pascal(c, arg, result, pos, ndigits);
                j++;
                return;

            case 'x':
                if(ndigits == -1)
                    ndigits = 1;
                for(__ss_int k=0; k<ndigits; k++)
                    result->unit[pos++] = '\x00';
                break;

            default:
                ;
        }

    }

}

/* pack multiple args */

template<class ... Args> void __pack(bytes *result, size_t &pos, __ss_int &ndigits, int n, str *fmt, Args ... args) {
    char order = '@';

    unsigned int fmtlen = fmt->__len__();
    unsigned int j = 0;

    (__pack_one(fmt, fmtlen, j, order, result, pos, ndigits, args), ...);
}

/* python API */

template<class ... Args> bytes *pack(int n, str *fmt, Args ... args) {
    bytes *result = new bytes();
    __ss_int result_size = calcsize(fmt);
    result->unit.resize(result_size);
    size_t pos = 0;
    __ss_int ndigits = -1;

    __ss_int expected_args = calcitems(fmt);
    __ss_int received_args = (__ss_int) sizeof...(args);
    if(expected_args != received_args)
        throw new error(__mod6(new str("pack expected %d items for packing (got %d)"), 2, expected_args, received_args));

    __pack(result, pos, ndigits, n, fmt, args...);

    return result;
}

template<class ... Args> void *pack_into(int n, str *fmt, bytes *buffer, __ss_int offset, Args ... args) {
    size_t pos = (size_t)offset;
    __ss_int ndigits = -1;

    __ss_int expected_args = calcitems(fmt);
    __ss_int received_args = (__ss_int) sizeof...(args);
    if(expected_args != received_args)
        throw new error(__mod6(new str("pack_into expected %d items for packing (got %d)"), 2, expected_args, received_args));

    __ss_int result_size = calcsize(fmt);
    if(offset + result_size > len(buffer))
        throw new error(new str("pack_into requires larger buffer"));

    __pack(buffer, pos, ndigits, n, fmt, args...);

    return NULL;
}

str *unpack();
str *unpack_from();

/* internal */

void __init();

} // module namespace
#endif
