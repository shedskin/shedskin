/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __STRUCT_HPP
#define __STRUCT_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __struct__ {

extern void *buffy;
extern __GC_STRING ordering;

extern class_ *cl_error;
class error : public Exception {
public:
    error(str *msg=0) : Exception(msg) {
        __class__ = cl_error;
    }
};

__ss_int calcsize(str *fmt);
__ss_int calcitems(str *fmt);

__ss_int unpack_int(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
bytes * unpack_bytes(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
__ss_bool unpack_bool(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
double unpack_float(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
void unpack_pad(char o, char c, unsigned int d, bytes *data, __ss_int *pos);

int get_itemsize(char order, char c);

void fillbuf_int(char c, __ss_int t, char order, unsigned int itemsize);
void fillbuf_float(char c, __ss_float t, char order, unsigned int itemsize);

template<class T> void __pack_int(char c, T t, char order, unsigned int itemsize) {
    throw new error(new str("required argument is not an integer"));
}
template<> inline void __pack_int(char c, __ss_int t, char order, unsigned int itemsize) {
    fillbuf_int(c, t, order, itemsize);
}

template<class T> void __pack_float(char c, T t, char order, unsigned int itemsize) {} // TODO raise error
template<> inline void __pack_float(char c, __ss_float t, char order, unsigned int itemsize) {
    fillbuf_float(c, t, order, itemsize);
}

template<class T> void __pack_char(char c, T t, bytes *result, size_t &pos) {} // TODO raise error
template<> inline void __pack_char(char c, bytes *b, bytes *result, size_t &pos) {
    result->unit[pos++] = b->unit[0];
}

template<class T> void __pack_str(char c, T t, bytes *result, size_t &pos ) {} // TODO raise error
template<> inline void __pack_str(char c, bytes *b, bytes *result, size_t &pos) {
    __ss_int len = b->__len__();
    for(__ss_int j=0; j<len; j++)
        result->unit[pos++] = b->unit[j];
}


template<class T> void __pack_one(str *fmt, unsigned int fmtlen, unsigned int &j, char &order, bytes *result, size_t &pos, __ss_int &ndigits, T arg) {
    unsigned int itemsize;

    for(; j<fmtlen; j++) {
        char c = fmt->unit[j];
        if(ordering.find(c) != std::string::npos) {
            order = c;
            continue;
        }
        if(::isdigit(c)) {
            ndigits = c - '0';
            continue;
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
                __pack_float(c, arg, order, itemsize);
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

            case 's':
                __pack_str(c, arg, result, pos);
                j++;
                return;

            default:
                ;
        }

    }

}

template<class ... Args> void __pack(bytes *result, size_t &pos, __ss_int &ndigits, int n, str *fmt, Args ... args) {
    char order = '@';

    unsigned int fmtlen = fmt->__len__();
    unsigned int j = 0;

    (__pack_one(fmt, fmtlen, j, order, result, pos, ndigits, args), ...);
}

template<class ... Args> bytes *pack(int n, str *fmt, Args ... args) {
    bytes *result = new bytes();
    __ss_int result_size = calcsize(fmt);
    result->unit.resize(result_size);
    size_t pos = 0;
    __ss_int ndigits = -1;

    __ss_int expected_args = calcitems(fmt);
    __ss_int received_args = (__ss_int) sizeof...(args);
    if(expected_args != received_args)
        throw new error(__modct(new str("pack expected %d items for packing (got %d)"), 2, ___box(expected_args), ___box(received_args)));

    __pack(result, pos, ndigits, n, fmt, args...);

    return result;
}

template<class ... Args> void *pack_into(int n, str *fmt, bytes *buffer, __ss_int offset, Args ... args) {
    size_t pos = (size_t)offset;
    __ss_int ndigits = -1;

    __pack(buffer, pos, ndigits, n, fmt, args...);

    return NULL;
}

str *unpack(); /* using __struct__::unpack */
str *unpack_from(); /* using __struct__::unpack */

void __init();

} // module namespace
#endif
