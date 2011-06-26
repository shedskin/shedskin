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

__ss_int unpack_int(char o, char c, unsigned int d, str *data, __ss_int *pos);
str * unpack_str(char o, char c, unsigned int d, str *data, __ss_int *pos);
__ss_bool unpack_bool(char o, char c, unsigned int d, str *data, __ss_int *pos);
double unpack_float(char o, char c, unsigned int d, str *data, __ss_int *pos);
void unpack_pad(char o, char c, unsigned int d, str *data, __ss_int *pos);
str *pack(int n, str *fmt, ...);
str *unpack(); /* using __struct__::unpack */

__ss_int calcsize(str *fmt);

void __init();

} // module namespace
#endif
