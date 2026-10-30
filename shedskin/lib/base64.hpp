/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __BASE64_HPP
#define __BASE64_HPP

#include "builtin.hpp"
#include "binascii.hpp"

using namespace __shedskin__;
namespace __base64__ {

extern str *__name__;

bytes *b64encode(bytes *s, bytes *altchars, __ss_bool padded=True, __ss_int wrapcol=0);
bytes *standard_b64encode(bytes *s);
bytes *urlsafe_b64encode(bytes *s, __ss_bool padded=True);

/* validate is tri-state: -1 = not given (True iff ignorechars is given) */
bytes *__b64decode(bytes *s, bytes *altchars, int validate, __ss_bool padded, bytes *ignorechars, __ss_bool canonical);

/* validate is __ss_void_struct when omitted by the caller (model default
 * __void), otherwise an __ss_bool (or int). */
template<class V>
bytes *b64decode(bytes *s, bytes *altchars, V validate, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False) {
    int v;
    if constexpr (std::is_same_v<V, __ss_void_struct>)
        v = -1;
    else
        v = (bool)validate ? 1 : 0;
    return __b64decode(s, altchars, v, padded, ignorechars, canonical);
}
bytes *standard_b64decode(bytes *s);
bytes *urlsafe_b64decode(bytes *s, __ss_bool padded=False);

/* the decoders also accept an ASCII str (see binascii.hpp) */
template<class T, class V>
bytes *b64decode(T *s, bytes *altchars, V validate, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False) {
    return b64decode(__binascii__::__ascii_data(s), altchars, validate, padded, ignorechars, canonical);
}
/* ..as does altchars (a deduced A, so that a NULL altchars can't pick this) */
template<class T, class A, class V>
bytes *b64decode(T *s, A *altchars, V validate, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False) {
    return b64decode(__binascii__::__ascii_data(s), __binascii__::__ascii_data(altchars), validate, padded, ignorechars, canonical);
}
template<class T> bytes *standard_b64decode(T *s) { return standard_b64decode(__binascii__::__ascii_data(s)); }
template<class T> bytes *urlsafe_b64decode(T *s, __ss_bool padded=False) { return urlsafe_b64decode(__binascii__::__ascii_data(s), padded); }

bytes *b16encode(bytes *s, __ss_int wrapcol=0);
bytes *b16decode(bytes *s, __ss_bool casefold, bytes *ignorechars=0);
template<class T> bytes *b16decode(T *s, __ss_bool casefold, bytes *ignorechars=0) { return b16decode(__binascii__::__ascii_data(s), casefold, ignorechars); }

bytes *b32encode(bytes *s, __ss_bool padded=True, __ss_int wrapcol=0);
bytes *b32decode(bytes *s, __ss_bool casefold=False, bytes *map01=0, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False);
template<class T> bytes *b32decode(T *s, __ss_bool casefold=False, bytes *map01=0, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False) { return b32decode(__binascii__::__ascii_data(s), casefold, map01, padded, ignorechars, canonical); }
template<class T, class M> bytes *b32decode(T *s, __ss_bool casefold, M *map01, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False) { return b32decode(__binascii__::__ascii_data(s), casefold, __binascii__::__ascii_data(map01), padded, ignorechars, canonical); }
bytes *b32hexencode(bytes *s, __ss_bool padded=True, __ss_int wrapcol=0);
bytes *b32hexdecode(bytes *s, __ss_bool casefold=False, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False);
template<class T> bytes *b32hexdecode(T *s, __ss_bool casefold=False, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False) { return b32hexdecode(__binascii__::__ascii_data(s), casefold, padded, ignorechars, canonical); }

bytes *a85encode(bytes *b, __ss_bool foldspaces=False, __ss_int wrapcol=0, __ss_bool pad=False, __ss_bool adobe=False);
bytes *a85decode(bytes *b, __ss_bool foldspaces=False, __ss_bool adobe=False, bytes *ignorechars=0, __ss_bool canonical=False);
template<class T> bytes *a85decode(T *b, __ss_bool foldspaces=False, __ss_bool adobe=False, bytes *ignorechars=0, __ss_bool canonical=False) { return a85decode(__binascii__::__ascii_data(b), foldspaces, adobe, ignorechars, canonical); }
bytes *b85encode(bytes *b, __ss_bool pad=False, __ss_int wrapcol=0);
bytes *b85decode(bytes *b, bytes *ignorechars=0, __ss_bool canonical=False);
template<class T> bytes *b85decode(T *b, bytes *ignorechars=0, __ss_bool canonical=False) { return b85decode(__binascii__::__ascii_data(b), ignorechars, canonical); }
bytes *z85encode(bytes *s, __ss_bool pad=False, __ss_int wrapcol=0);
bytes *z85decode(bytes *s, bytes *ignorechars=0, __ss_bool canonical=False);
template<class T> bytes *z85decode(T *s, bytes *ignorechars=0, __ss_bool canonical=False) { return z85decode(__binascii__::__ascii_data(s), ignorechars, canonical); }

bytes *encodebytes(bytes *s);
bytes *decodebytes(bytes *s);
void *encode(file_binary *input, file_binary *output);
void *decode(file_binary *input, file_binary *output);

void __init();

} // module namespace
#endif
