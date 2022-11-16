/* Copyright 2005-2022 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __STRING_HPP
#define __STRING_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __string__ {

extern str *ascii_letters, *ascii_uppercase, *ascii_lowercase, *whitespace, *punctuation, *printable, *hexdigits, *octdigits, *digits;

str *capwords(str *s, str *sep=0);

void __init();

} // module namespace
#endif
