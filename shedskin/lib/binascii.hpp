/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

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

bytes *a2b_uu(bytes *string);
bytes *b2a_uu(bytes *data);
bytes *a2b_base64(bytes *string);
bytes *b2a_base64(bytes *data);
bytes *a2b_qp(bytes *string, __ss_bool header);
bytes *b2a_qp(bytes *data, __ss_bool quotetabs, __ss_bool istext, __ss_bool header);
tuple2<bytes *, __ss_int> *a2b_hqx(bytes *string);
bytes *b2a_hqx(bytes *data);
bytes *rledecode_hqx(bytes *data);
bytes *rlecode_hqx(bytes *data);
__ss_int crc_hqx(bytes *data, __ss_int crc);
__ss_int crc32(bytes *data, __ss_int crc=0);
bytes *b2a_hex(bytes *data);
bytes *a2b_hex(bytes *data);
bytes *hexlify(bytes *data);
bytes *unhexlify(bytes *data);

void __init();

} // module namespace
#endif
