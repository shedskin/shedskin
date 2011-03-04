#ifndef __BINASCII_HPP
#define __BINASCII_HPP

#include "builtin.hpp"
#include "binascii.hpp"

#ifdef USE_ZLIB_CRC32
#include "zlib.h"
#endif

using namespace __shedskin__;
namespace __binascii__ {

class Error;
class Incomplete;


extern str *__name__;

extern class_ *cl_Error;
class Error : public Exception {
public:

    Error() {}
    Error(str *msg) {
        this->__class__ = cl_Error;
        __init__(msg);
    }
};

extern class_ *cl_Incomplete;
class Incomplete : public Exception {
public:

    Incomplete() {}
    Incomplete(str *msg) {
        this->__class__ = cl_Incomplete;
        __init__(msg);
    }
};

extern void * default_4;
extern __ss_bool  default_1;
extern __ss_bool  default_0;
extern __ss_bool  default_3;
extern __ss_bool  default_2;
extern void * default_5;

str *a2b_uu(str *string);
str *b2a_uu(str *data);
str *a2b_base64(str *string);
str *b2a_base64(str *data);
str *a2b_qp(str *string, __ss_bool header);
str *b2a_qp(str *data, __ss_bool quotetabs, __ss_bool istext, __ss_bool header);
str *a2b_hqx(str *string);
str *b2a_hqx(str *data);
str *rledecode_hqx(str *data);
str *rlecode_hqx(str *data);
__ss_int crc_hqx(str *data, __ss_int crc);
__ss_int crc32(str *data, __ss_int crc=0);
str *b2a_hex(str *data);
str *a2b_hex(str *data);
str *hexlify(str *data);
str *unhexlify(str *data);

void __init();

} // module namespace
#endif
