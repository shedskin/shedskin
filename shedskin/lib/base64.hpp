/* Copyright 2005-2025 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __BASE64_HPP
#define __BASE64_HPP

#include "builtin.hpp"
#include "binascii.hpp"

using namespace __shedskin__;
namespace __base64__ {

bytes *b64encode(bytes *s, bytes *altchars);
bytes *standard_b64encode(bytes *s);
bytes *urlsafe_b64encode(bytes *s);

bytes *b64decode(bytes *s, bytes *altchars, __ss_bool validate);
bytes *standard_b64decode(bytes *s);
bytes *urlsafe_b64decode(bytes *s);

void __init();

} // module namespace
#endif
