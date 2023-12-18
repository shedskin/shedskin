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

__ss_int unpack_int(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
bytes * unpack_bytes(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
__ss_bool unpack_bool(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
double unpack_float(char o, char c, unsigned int d, bytes *data, __ss_int *pos);
void unpack_pad(char o, char c, unsigned int d, bytes *data, __ss_int *pos);

inline void __pack_one(str *fmt, unsigned int fmtlen, unsigned int &j, str *digits, char &order, bytes *result, pyobj *arg) {
    for(; j<fmtlen; j++) {
        printf("j=%d\n", j);
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
            case 'H':
                printf("H\n");
                break;
            case 's':
                printf("s\n");
                break;
            default:
                ;
        }

    }

}

/*
template<class ... Args> void __pack(bytes *result, size_t &pos, int n, str *fmt, Args ... args) {
    char order = '@';
    str *digits = new str();

    unsigned int fmtlen = fmt->__len__();
    unsigned int j = 0;

    (__pack_one(fmt, fmtlen, j, digits, order, result, args), ...);
}

template<class ... Args> bytes *pack(int n, str *fmt, Args ... args) {
    bytes *result = new bytes();
    __ss_int result_size = calcsize(fmt);
    result->unit.resize(result_size);
    size_t pos = 0;

    __pack(result, pos, n, fmt, args...);

    return result;
}

template<class ... Args> void *pack_into(int n, str *fmt, bytes *buffer, __ss_int offset, Args ... args) {
    size_t pos = (size_t)offset;

    __pack(buffer, pos, n, fmt, args...);

    return NULL;
}
*/

bytes *pack(int n, str *fmt, ...);
void pack_into(int n, str *fmt, bytes *buffer, __ss_int offset, ...);

str *unpack(); /* using __struct__::unpack */
str *unpack_from(); /* using __struct__::unpack */

void __init();

} // module namespace
#endif
