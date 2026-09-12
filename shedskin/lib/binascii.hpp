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
extern bytes *default_0, *default_2, *default_5;
extern bytes *BASE64_ALPHABET, *URLSAFE_BASE64_ALPHABET, *BASE85_ALPHABET, *ASCII85_ALPHABET, *Z85_ALPHABET, *BASE32_ALPHABET, *BASE32HEX_ALPHABET;

extern class_ *cl_Error;
class Error : public Exception {
public:

    Error() {}
    Error(str *msg): Exception(msg) {
        this->__class__ = cl_Error;
    }
};

extern class_ *cl_Incomplete;
class Incomplete : public Exception {
public:

    Incomplete() {}
    Incomplete(str *msg): Exception(msg) {
        this->__class__ = cl_Incomplete;
    }
};

bytes *a2b_uu(bytes *string);
bytes *b2a_uu(bytes *data, __ss_bool backtick);
bytes *a2b_base64(bytes *string, __ss_bool strict_mode, bytes *altchars=0);
bytes *b2a_base64(bytes *data, __ss_bool newline, __ss_int wrapcol=0, bytes *altchars=0);
bytes *a2b_ascii85(bytes *data, __ss_bool foldspaces=False, __ss_bool adobe=False, bytes *ignorechars=0, __ss_bool canonical=False);
bytes *b2a_ascii85(bytes *data, __ss_bool foldspaces=False, __ss_int wrapcol=0, __ss_bool pad=False, __ss_bool adobe=False);
bytes *a2b_base85(bytes *data, bytes *alphabet=0, bytes *ignorechars=0, __ss_bool canonical=False);
bytes *b2a_base85(bytes *data, bytes *alphabet=0, __ss_int wrapcol=0, __ss_bool pad=False);
bytes *a2b_base32(bytes *data, __ss_bool padded=True, bytes *alphabet=0, bytes *ignorechars=0, __ss_bool canonical=False);
bytes *b2a_base32(bytes *data, __ss_bool padded=True, bytes *alphabet=0, __ss_int wrapcol=0);
void wraplines(bytes *data, size_t width);
bytes *a2b_qp(bytes *string, __ss_bool header);
bytes *b2a_qp(bytes *data, __ss_bool quotetabs, __ss_bool istext, __ss_bool header);
__ss_int crc_hqx(bytes *data, __ss_int crc);
__ss_int crc32(bytes *data, __ss_int crc=0);
bytes *b2a_hex(bytes *data, str *sep=0, __ss_int bytes_per_sep=1);
bytes *hexlify(bytes *data, str *sep=0, __ss_int bytes_per_sep=1);
bytes *a2b_hex(bytes *data);
bytes *unhexlify(bytes *data);

void __init();

} // module namespace
#endif
