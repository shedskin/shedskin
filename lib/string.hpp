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

int count(str *a, str *b, int start=0);
int count(str *a, str *b, int start, int end);

int find(str *s, str *t, int a=0);
int find(str *s, str *t, int a, int b);
int rfind(str *s, str *t, int a=0);
int rfind(str *s, str *t, int a, int b);
int index(str *s, str *t, int a=0);
int index(str *s, str *t, int a, int b);
int rindex(str *s, str *t, int a=0);
int rindex(str *s, str *t, int a, int b);

str *expandtabs(str *s, int width=8);

list<str *> *split(str *s, str *sep=0, int c=-1);
list<str *> *splitfields(str *s, str *sep=0, int c=-1);

str *replace(str *s, str *a, str *b, int c=-1); 
str *translate(str *s, str *table, str *delchars=0);

str *zfill(str *s, int width);
str *upper(str *s);
str *lower(str *s);

str *strip(str *s, str *chars=0);
str *lstrip(str *s, str *chars=0);
str *rstrip(str *s, str *chars=0);

str *ljust(str *s, int width, str *fchar=0);
str *rjust(str *s, int width, str *fchar=0);

str *maketrans(str *frm, str *to);

str *capitalize(str *s);
str *capwords(str *s, str *sep=0);
str *swapcase(str *s);

str *center(str *s, int w, str *fill=0);

int atoi(str *s, int base=10);
int atol(str *s, int base=10);
double atof(str *s);

void __init();

} // module namespace
#endif
