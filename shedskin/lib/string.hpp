#ifndef __STRING_HPP
#define __STRING_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __string__ {

extern str *ascii_letters, *ascii_uppercase, *ascii_lowercase, *lowercase, *uppercase, *whitespace, *punctuation, *printable, *hexdigits, *octdigits, *digits, *letters;

str *join(pyiter<str *> *a, str *b=0);
str *join(pyseq<str *> *a, str *b=0);
str *joinfields(pyiter<str *> *a, str *b=0);
str *joinfields(pyseq<str *> *a, str *b=0);

__ss_int count(str *a, str *b, __ss_int start=0);
__ss_int count(str *a, str *b, __ss_int start, __ss_int end);

__ss_int find(str *s, str *t, __ss_int a=0);
__ss_int find(str *s, str *t, __ss_int a, __ss_int b);
__ss_int rfind(str *s, str *t, __ss_int a=0);
__ss_int rfind(str *s, str *t, __ss_int a, __ss_int b);
__ss_int index(str *s, str *t, __ss_int a=0);
__ss_int index(str *s, str *t, __ss_int a, __ss_int b);
__ss_int rindex(str *s, str *t, __ss_int a=0);
__ss_int rindex(str *s, str *t, __ss_int a, __ss_int b);

str *expandtabs(str *s, __ss_int width=8);

list<str *> *split(str *s, str *sep=0, __ss_int c=-1);
list<str *> *splitfields(str *s, str *sep=0, __ss_int c=-1);

str *replace(str *s, str *a, str *b, __ss_int c=-1);
str *translate(str *s, str *table, str *delchars=0);

str *zfill(str *s, __ss_int width);
str *upper(str *s);
str *lower(str *s);

list<str *> *rsplit(str *s, str *sep = 0, __ss_int maxsep = -1);

str *strip(str *s, str *chars=0);
str *lstrip(str *s, str *chars=0);
str *rstrip(str *s, str *chars=0);

str *ljust(str *s, __ss_int width, str *fchar=0);
str *rjust(str *s, __ss_int width, str *fchar=0);

str *maketrans(str *frm, str *to);

str *capitalize(str *s);
str *capwords(str *s, str *sep=0);
str *swapcase(str *s);

str *center(str *s, __ss_int w, str *fill=0);

__ss_int atoi(str *s, __ss_int base=10);
__ss_int atol(str *s, __ss_int base=10);
double atof(str *s);

void __init();

} // module namespace
#endif
