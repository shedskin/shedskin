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
extern bytes *BASE64_ALPHABET, *URLSAFE_BASE64_ALPHABET, *UU_ALPHABET, *CRYPT_ALPHABET, *BINHEX_ALPHABET, *BASE85_ALPHABET, *ASCII85_ALPHABET, *Z85_ALPHABET, *BASE32_ALPHABET, *BASE32HEX_ALPHABET;

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
/* a2b_base64 workhorse. strict_mode is tri-state: -1 means "not given",
 * which (as in CPython 3.15) resolves to True iff ignorechars is given.
 * ignorechars == NULL means "not given"; alphabet == NULL means the
 * standard alphabet. The table_a2b overload takes a prebuilt 256-entry
 * reverse table (entries >= 64 invalid), which base64.b64decode uses to
 * emulate the legacy altchars-translation behaviour. */
const unsigned char *__a2b_base64_table(); /* the standard 256-entry reverse table */
bytes *__a2b_base64(bytes *string, int strict_mode, __ss_bool padded, const unsigned char *table_a2b, bytes *ignorechars, __ss_bool canonical);
bytes *__a2b_base64(bytes *string, int strict_mode, __ss_bool padded, bytes *alphabet, bytes *ignorechars, __ss_bool canonical);

/* strict_mode is __ss_void_struct when omitted by the caller (model default
 * __void), otherwise an __ss_bool (or int). */
template<class S>
bytes *a2b_base64(bytes *string, S strict_mode, __ss_bool padded=True, bytes *alphabet=0, bytes *ignorechars=0, __ss_bool canonical=False) {
    int sm;
    if constexpr (std::is_same_v<S, __ss_void_struct>)
        sm = -1;
    else
        sm = (bool)strict_mode ? 1 : 0;
    return __a2b_base64(string, sm, padded, alphabet, ignorechars, canonical);
}
bytes *b2a_base64(bytes *data, __ss_bool newline, __ss_int wrapcol=0, __ss_bool padded=True, bytes *alphabet=0);
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
/* a bytes separator (templates, so that a NULL sep still picks the above) */
template<class S> bytes *b2a_hex(bytes *data, S *sep, __ss_int bytes_per_sep=1) { return b2a_hex(data, __hex_sep(sep), bytes_per_sep); }
template<class S> bytes *hexlify(bytes *data, S *sep, __ss_int bytes_per_sep=1) { return hexlify(data, __hex_sep(sep), bytes_per_sep); }
bytes *a2b_hex(bytes *data, bytes *ignorechars=0);
bytes *unhexlify(bytes *data, bytes *ignorechars=0);

void __init();

} // module namespace
#endif
