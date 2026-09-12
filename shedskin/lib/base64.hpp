/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __BASE64_HPP
#define __BASE64_HPP

#include "builtin.hpp"
#include "binascii.hpp"

using namespace __shedskin__;
namespace __base64__ {

extern str *__name__;
extern bytes *default_3, *default_4, *default_5, *default_6, *default_7;

bytes *b64encode(bytes *s, bytes *altchars, __ss_bool padded=True, __ss_int wrapcol=0);
bytes *standard_b64encode(bytes *s);
bytes *urlsafe_b64encode(bytes *s);

bytes *b64decode(bytes *s, bytes *altchars, __ss_bool validate);
bytes *standard_b64decode(bytes *s);
bytes *urlsafe_b64decode(bytes *s);

bytes *b16encode(bytes *s);
bytes *b16decode(bytes *s, __ss_bool casefold);

bytes *b32encode(bytes *s, __ss_bool padded=True, __ss_int wrapcol=0);
bytes *b32decode(bytes *s, __ss_bool casefold=False, bytes *map01=0, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False);
bytes *b32hexencode(bytes *s, __ss_bool padded=True, __ss_int wrapcol=0);
bytes *b32hexdecode(bytes *s, __ss_bool casefold=False, __ss_bool padded=True, bytes *ignorechars=0, __ss_bool canonical=False);

bytes *a85encode(bytes *b, __ss_bool foldspaces=False, __ss_int wrapcol=0, __ss_bool pad=False, __ss_bool adobe=False);
bytes *a85decode(bytes *b, __ss_bool foldspaces=False, __ss_bool adobe=False, bytes *ignorechars=0, __ss_bool canonical=False);
bytes *b85encode(bytes *b, __ss_bool pad=False, __ss_int wrapcol=0);
bytes *b85decode(bytes *b, bytes *ignorechars=0, __ss_bool canonical=False);
bytes *z85encode(bytes *s, __ss_bool pad=False, __ss_int wrapcol=0);
bytes *z85decode(bytes *s, bytes *ignorechars=0, __ss_bool canonical=False);

bytes *encodebytes(bytes *s);
bytes *decodebytes(bytes *s);
void *encode(file_binary *input, file_binary *output);
void *decode(file_binary *input, file_binary *output);

void __init();

} // module namespace
#endif
