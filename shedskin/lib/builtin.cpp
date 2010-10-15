#include "builtin.hpp"
#include "re.hpp"
#include <climits>
#include <cmath>
#include <numeric>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <limits.h>

namespace __shedskin__ {

class_ *cl_class_, *cl_none, *cl_str_, *cl_int_, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict, *cl_set, *cl_object, *cl_rangeiter, *cl_xrange;

str *sp, *nl, *__fmt_s, *__fmt_H, *__fmt_d;
__GC_STRING ws, __fmtchars;
__GC_VECTOR(str *) __char_cache;

__ss_bool True;
__ss_bool False;

list<str *> *__join_cache, *__mod5_cache;
list<pyobj *> *__print_cache;

char __str_cache[4000];

file *__ss_stdin, *__ss_stdout, *__ss_stderr;

#ifdef __SS_BIND
dict<void *, void *> *__ss_proxy;
#endif

void __init() {
    GC_INIT();
#ifdef __SS_BIND
    Py_Initialize();
    __ss_proxy = new dict<void *, void *>();
#endif

    cl_class_ = new class_ ("class_", 0, 0);
    cl_none = new class_("none", 1, 1);
    cl_str_ = new class_("str_", 2, 2);
    cl_int_ = new class_("int_", 3, 3);
    cl_float_ = new class_("float_", 4, 4);
    cl_list = new class_("list", 5, 5);
    cl_tuple = new class_("tuple", 6, 6);
    cl_dict = new class_("dict", 7, 7);
    cl_set = new class_("set", 8, 8);
    cl_object = new class_("object", 9, 9);
    cl_rangeiter = new class_("rangeiter", 10, 10);
    cl_complex = new class_("complex", 11, 11);
    cl_xrange = new class_("xrange", 12, 12);

    True.value = 1;
    False.value = 0;

    ws = " \n\r\t\f\v";
    __fmtchars = "#*-+ .0123456789hlL";
    sp = new str(" ");
    nl = new str("\n");
    __fmt_s = new str("%s");
    __fmt_H = new str("%H");
    __fmt_d = new str("%d");

    for(int i=0;i<256;i++) {
        char c = i;
        __char_cache.push_back(new str(&c, 1));
    }

    __join_cache = new list<str *>();
    __print_cache = new list<pyobj *>();
    __mod5_cache = new list<str *>();

    for(int i=0; i<1000; i++) {
        __str_cache[4*i] = '0' + (i % 10);
        __str_cache[4*i+1] = '0' + ((i/10) % 10);
        __str_cache[4*i+2] = '0' + ((i/100) % 10);
    }

    __ss_stdin = new file(stdin);
    __ss_stdin->name = new str("<stdin>");
    __ss_stdout = new file(stdout);
    __ss_stdout->name = new str("<stdout>");
    __ss_stderr = new file(stderr);
    __ss_stderr->name = new str("<stderr>");
}

/* int_ methods */

int_::int_(__ss_int i) {
    unit = i;
    __class__ = cl_int_;
}

str *int_::__repr__() {
    return __str(unit);
}

/* float methods */

float_::float_(double f) {
    unit = f;
    __class__ = cl_float_;
}

str *float_::__repr__() {
    return __str(unit);
}

bool_::bool_(__ss_bool i) {
    unit = i;
    //__class__ = cl_int_;
}

str *bool_::__repr__() {
    if(unit.value)
        return new str("True");
    return new str("False");
}

/* float methods */
/* complex methods */

complex::complex(double real, double imag) {
    this->__class__ = cl_complex;
    this->real = real;
    this->imag = imag;
}

complex::complex(str *s) {
    this->__class__ = cl_complex;
    __re__::match_object *m;
    __re__::re_object *p;

    p = __re__::compile(new str("(?P<one>[+-]?([\\d\\.]+e[+-]?\\d+|[\\d\\.]*)j?)(?P<two>[+-]?([\\d\\.]+e[+-]?\\d+|[\\d\\.]*)j?)?$"));
    m = p->match(s->strip());
    if (___bool(m)) {
        complex *c = (parsevalue(m->group(1, new str("one"))))->__add__(parsevalue(m->group(1, new str("two"))));
        real = c->real;
        imag = c->imag;
    }
    else {
        throw ((new ValueError(new str("complex() arg is a malformed string"))));
    }
}

#ifdef __SS_BIND
complex::complex(PyObject *p) {
    this->__class__ = cl_complex;
    real = PyComplex_RealAsDouble(p);
    imag = PyComplex_ImagAsDouble(p);
}
PyObject *complex::__to_py__() {
    return PyComplex_FromDoubles(real, imag);
}
#endif

complex *complex::parsevalue(str *s) {
    complex *mult;

    if ((!___bool(s))) {
        return __add2(0, new complex(0.0, 0.0));
    }
    mult = __add2(1, new complex(0.0, 0.0));
    if (__eq(s->__getitem__((-1)), new str("j"))) {
        s = s->__slice__(2, 0, (-1), 0);
        mult = __add2(0, new complex(0.0, 1.0));
    }
    if (((new list<str *>(2, new str("+"), new str("-"))))->__contains__(s)) {
        s = s->__iadd__(new str("1"));
    }
    return __mul2(__float(s), mult);
}

complex *complex::__add__(complex *b) { return new complex(real+b->real, imag+b->imag); }
complex *complex::__add__(double b) { return new complex(b+real, imag); }
complex *complex::__iadd__(complex *b) { return __add__(b); }
complex *complex::__iadd__(double b) { return __add__(b); }

complex *complex::__sub__(complex *b) { return new complex(real-b->real, imag-b->imag); }
complex *complex::__sub__(double b) { return new complex(real-b, imag); }
complex *complex::__rsub__(double b) { return new complex(b-real, -imag); }
complex *complex::__isub__(complex *b) { return __sub__(b); }
complex *complex::__isub__(double b) { return __sub__(b); }

complex *complex::__mul__(complex *b) { return new complex(real*b->real-imag*b->imag, real*b->imag+imag*b->real); }
complex *complex::__mul__(double b) { return new complex(b*real, b*imag); }
complex *complex::__imul__(complex *b) { return __mul__(b); }
complex *complex::__imul__(double b) { return __mul__(b); }

void __complexdiv(complex *c, complex *a, complex *b) {
    double norm = b->real*b->real+b->imag*b->imag;
    c->real = (a->real*b->real+a->imag*b->imag)/norm;
    c->imag = (a->imag*b->real-b->imag*a->real)/norm;
}

complex *complex::__div__(complex *b) { complex *c=new complex(); __complexdiv(c, this, b); return c; }
complex *complex::__div__(double b) { return new complex(real/b, imag/b); }
complex *complex::__idiv__(complex *b) { return __div__(b); }
complex *complex::__idiv__(double b) { return __div__(b); }
complex *complex::__rdiv__(double b) { complex *c=new complex(); __complexdiv(c, new complex(b), this); return c; }

complex *complex::conjugate() { return new complex(real, -imag); }
complex *complex::__pos__() { return this; }
complex *complex::__neg__() { return new complex(-real, -imag); }
double complex::__abs__() { return std::sqrt(real*real+imag*imag); }
double __abs(complex *c) { return c->__abs__(); }

complex *complex::__floordiv__(complex *b) {
    complex *c = __div__(b);
    c->real = ((__ss_int)c->real);
    c->imag = 0;
    return c;
}
complex *complex::__floordiv__(double b) {
    complex *c = __div__(b);
    c->real = ((__ss_int)c->real);
    c->imag = 0;
    return c;
}

complex *complex::__mod__(complex *b) {
    complex *c = __div__(b);
    return __sub__(b->__mul__(((__ss_int)c->real)));
}
complex *complex::__mod__(double b) {
    complex *c = __div__(b);
    return __sub__(b*((__ss_int)c->real));
}

tuple2<complex *, complex *> *complex::__divmod__(complex *b) {
    return new tuple2<complex *, complex *>(2, __floordiv__(b), __mod__(b));
}
tuple2<complex *, complex *> *complex::__divmod__(double b) {
    return new tuple2<complex *, complex *>(2, __floordiv__(b), __mod__(b));
}

__ss_bool complex::__eq__(pyobj *p) {
    if(p->__class__ != cl_complex)
        return False;
    return __mbool(real == ((complex *)p)->real && imag == ((complex *)p)->imag);
}

int complex::__hash__() {
    return ((__ss_int)imag)*1000003+((__ss_int)real);
}

__ss_bool complex::__nonzero__() {
    return __mbool(real != 0 || imag != 0);
}

str *complex::__repr__() {
    str *left, *middle, *right;
    if(real==0)
        return __modct(new str("%gj"), 1, ___box(imag));
    left = __modct(new str("(%g"), 1, ___box(real));
    if(imag<0)
        middle = new str("");
    else
        middle = new str("+");
    right = __modct(new str("%gj)"), 1, ___box(imag));
    return __add_strs(3, left, middle, right);
}

/* str methods */

str::str() : hash(-1) {
    __class__ = cl_str_;
}

str::str(const char *s) : unit(s), hash(-1) {
    __class__ = cl_str_;
}

str::str(__GC_STRING s) : unit(s), hash(-1) {
    __class__ = cl_str_;
}

str::str(const char *s, int size) : unit(s, size), hash(-1) { /* '\0' delimiter in C */
    __class__ = cl_str_;
}

str *str::__str__() { // weg?
    return this;
}

str *str::__repr__() {
    std::stringstream ss;
    __GC_STRING sep = "\\\n\r\t";
    __GC_STRING let = "\\nrt";

    const char *quote = "'";
    int hasq = unit.find("'");
    int hasd = unit.find("\"");

    if (hasq != -1 && hasd != -1) {
        sep += "'"; let += "'";
    }
    if (hasq != -1 && hasd == -1)
        quote = "\"";

    ss << quote;
    for(unsigned int i=0; i<unit.size(); i++)
    {
        char c = unit[i];
        int k;

        if((k = sep.find_first_of(c)) != -1)
            ss << "\\" << let[k];
        else {
            int j = (int)((unsigned char)c);

            if(j<16)
                ss << "\\x0" << std::hex << j;
            else if(j>=' ' && j<='~')
                ss << (char)j;
            else
                ss << "\\x" << std::hex << j;
        }
    }
    ss << quote;

    return new str(ss.str().c_str());
}

str *str::__join(pyseq<str *> *l, bool only_ones, int total) {
    int unitsize = unit.size();
    int elems = len(l);
    if(elems==1)
        return l->units[0];
    str *s = new str();
    if(unitsize == 0 and only_ones) {
        s->unit.resize(total);
        for(int j=0; j<elems; j++)
            s->unit[j] = l->units[j]->unit[0];
    }
    else if(elems) {
        total += (elems-1)*unitsize;
        s->unit.resize(total);
        int tsz;
        int k = 0;
        for(int m = 0; m<elems; m++) {
            str *t = l->units[m];
            tsz = t->unit.size();
            if (tsz == 1)
                s->unit[k] = t->unit[0];
            else
                memcpy((void *)(s->unit.data()+k), t->unit.data(), tsz);
            k += tsz;
            if (unitsize && m < elems-1) {
                if (unitsize==1)
                    s->unit[k] = unit[0];
                else
                    memcpy((void *)(s->unit.data()+k), unit.data(), unit.size());
                k += unitsize;
            }
        }
    }
    return s;
}

str * str::join(list<str *> *l) {
    int lsz = len(l);
    if(lsz==1)
        return l->units[0];
    int sz, total;
    bool only_ones = true;
    total = 0;
    for(int i=0; i<lsz; i++) {
        sz = l->units[i]->unit.size();
        if(sz!=1)
            only_ones = false;
        total += sz;
    }
    return __join(l, only_ones, total);
}

str * str::join(tuple2<str *, str *> *l) { /* XXX merge */
    int lsz = len(l);
    int sz, total;
    bool only_ones = true;
    total = 0;
    for(int i=0; i<lsz; i++) {
        sz = l->units[i]->unit.size();
        if(sz!=1)
            only_ones = false;
        total += sz;
    }
    return __join(l, only_ones, total);
}

__ss_int str::__int__() {
    return __int(this);
}

__ss_bool str::__contains__(str *s) {
    return __mbool(unit.find(s->unit) != -1);
}

__ss_bool str::__ctype_function(int (*cfunc)(int))
{
  int i, l = unit.size();
  if(!l)
      return False;

  for(i = 0; i < l; i++)
      if(!cfunc((int)unit[i])) return False;

  return True;
}

__ss_bool str::isspace() { return __mbool(unit.size() && (unit.find_first_not_of(ws) == -1)); }
__ss_bool str::isdigit() { return __ctype_function(&::isdigit); }
__ss_bool str::isalpha() { return __ctype_function(&::isalpha); }
__ss_bool str::isalnum() { return __ctype_function(&::isalnum); }
__ss_bool str::islower() { return __ctype_function(&::islower); }
__ss_bool str::isupper() { return __ctype_function(&::isupper); }

str *str::ljust(int width, str *s) {
    if(width<=__len__()) return this;
    if(!s) s = sp;
    return __add__(s->__mul__(width-__len__()));
}

str *str::rjust(int width, str *s) {
    if(width<=__len__()) return this;
    if(!s) s = sp;
    return s->__mul__(width-__len__())->__add__(this);
}

str *str::zfill(int width) {
    if(width<=__len__()) return this;
    return (new str("0"))->__mul__(width-__len__())->__add__(this);
}

str *str::expandtabs(int width) {
    int i;
    __GC_STRING r = unit;
    while((i = r.find("\t")) != -1)
        r.replace(i, 1, (new str(" "))->__mul__(width-i%width)->unit);
    return new str(r);
}

str *str::strip(str *chars) {
    return lstrip(chars)->rstrip(chars);
}

str *str::lstrip(str *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    int first = unit.find_first_not_of(remove);
    if( first == -1 )
        return new str("");
    return new str(unit.substr(first,unit.size()-first));
}



tuple2<str *, str *> *str::partition(str *sep)
{
    int i;

    i = unit.find(sep->unit);
    if(i != -1)
        return new tuple2<str *, str *>(3, new str(unit.substr(0, i)), new str(sep->unit), new str(unit.substr(i + sep->unit.length())));
    else
        return new tuple2<str *, str *>(3, new str(unit), new str(""), new str(""));
}

tuple2<str *, str *> *str::rpartition(str *sep)
{
    int i;

    i = unit.rfind(sep->unit);
    if(i != -1)
        return new tuple2<str *, str *>(3, new str(unit.substr(0, i)), new str(sep->unit), new str(unit.substr(i + sep->unit.length())));
    else
        return new tuple2<str *, str *>(3, new str(unit), new str(""), new str(""));
}

list<str *> *str::rsplit(str *sep, int maxsep)
{
    __GC_STRING ts;
    list<str *> *r = new list<str *>();
    int i, j, curi, tslen;

    curi = 0;
    i = j = unit.size() - 1;

    //split by whitespace
    if(!sep)
    {
        while(i > 0 && j > 0 && (curi < maxsep || maxsep < 0))
        {
            j = unit.find_last_not_of(ws, i);
            if(j == -1) break;

            i = unit.find_last_of(ws, j);

            //this works out pretty nicely; i will be -1 if no more is found, and thus i + 1 will be 0th index
            r->append(new str(unit.substr(i + 1, j - i)));
            curi++;
        }

        //thus we only bother about extra stuff here if we *have* found more whitespace
        if(i > 0 && j >= 0 && (j = unit.find_last_not_of(ws, i)) >= 0) r->append(new str(unit.substr(0, j)));
    }

    //split by seperator
    else
    {
        ts = sep->unit;
        tslen = ts.length();

        i++;
        while(i > 0 && j > 0 && (curi < maxsep || maxsep < 0))
        {
            j = i;
            i--;

            i = unit.rfind(ts, i);
            if(i == -1)
            {
                i = j;
                break;
            }

            r->append(new str(unit.substr(i + tslen, j - i - tslen)));

            curi++;
        }

        //either left over (beyond max) or very last match (see loop break)
        if(i >= 0) r->append(new str(unit.substr(0, i)));
    }

    r->reverse();

    return r;
}

__ss_bool str::istitle()
{
    int i, len;

    len = unit.size();
    if(!len)
        return False;

    for(i = 0; i < len; )
    {
        for( ; !::isalpha((int)unit[i]) && i < len; i++) ;
        if(i == len) break;

        if(!::isupper((int)unit[i])) return False;
        i++;

        for( ; ::islower((int)unit[i]) && i < len; i++) ;
        if(i == len) break;

        if(::isalpha((int)unit[i])) return False;
    }

    return True;
}

list<str *> *str::splitlines(int keepends)
{
    list<str *> *r = new list<str *>();
    int i, endlen;
    unsigned int j;
    const char *ends = "\r\n";

    endlen = i = 0;
    do
    {
        j = i + endlen;
        i = unit.find_first_of(ends, j);
        if(i == -1) break;

        //for all we know the character sequence could change mid-way...
        if(unit[i] == '\r' && unit[i + 1] == '\n') endlen = 2;
        else endlen = 1;

        r->append(new str(unit.substr(j, i - j + (keepends ? endlen : 0))));
    }
    while(i >= 0);

    if(j != unit.size()) r->append(new str(unit.substr(j)));

    return r;
}

str *str::rstrip(str *chars) {
    __GC_STRING remove;
    if(chars) remove = chars->unit;
    else remove = ws;
    int last = unit.find_last_not_of(remove);
    if( last == -1 )
        return new str("");
    return new str(unit.substr(0,last+1));
}

list<str *> *str::split(str *sp, int max_splits) {
    __GC_STRING s = unit;
    int num_splits = 0;
    unsigned int sep_iter, tmp, chunk_iter = 0;
    list<str *> *result = new list<str *>();
    if (sp == NULL)
    {
#define next_separator(iter) (s.find_first_of(ws, (iter)))
#define skip_separator(iter) (s.find_first_not_of(ws, (iter)))

        if(skip_separator(chunk_iter) == -1) /* XXX */
            return result;
        if(next_separator(chunk_iter) == 0)
            chunk_iter = skip_separator(chunk_iter);
        while((max_splits < 0 or num_splits < max_splits)
              and ((sep_iter = next_separator(chunk_iter)) != -1))
        {
            result->append(new str(s.substr(chunk_iter, sep_iter - chunk_iter)));
            if((tmp = skip_separator(sep_iter)) == -1) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));
        else if(sep_iter == -1)
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));

#undef next_separator
#undef skip_separator

    } else { /* given separator (slightly different algorithm required)
              * (python is very inconsistent in this respect) */
        const char *sep = sp->unit.c_str();
        int sep_size = sp->unit.size();

#define next_separator(iter) s.find(sep, (iter))
#define skip_separator(iter) ((iter + sep_size) > s.size()? -1 : (iter + sep_size))

        if (max_splits == 0) {
            result->append(this);
            return result;
        }
        if(next_separator(chunk_iter) == 0) {
            chunk_iter = skip_separator(chunk_iter);
            result->append(new str());
            ++num_splits;
        }
        while((max_splits < 0 or num_splits < max_splits)
              and (sep_iter = next_separator(chunk_iter)) != -1)
        {
            result->append(new str(s.substr(chunk_iter, sep_iter - chunk_iter)));
            if((tmp = skip_separator(sep_iter)) == -1) {
                chunk_iter = sep_iter;
                break;
            } else
                chunk_iter = tmp;
            ++num_splits;
        }
        if(not (max_splits < 0 or num_splits < max_splits))
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));
        else if(sep_iter == -1)
            result->append(new str(s.substr(chunk_iter, s.size()-chunk_iter)));


#undef next_separator
#undef skip_separator

    }

    return result;
}

str *str::translate(str *table, str *delchars) {
    if(len(table) != 256)
        throw new ValueError(new str("translation table must be 256 characters long"));

    str *newstr = new str();

    int self_size = unit.size();
    for(int i = 0; i < self_size; i++) {
        char c = unit[i];
        if(!delchars || delchars->unit.find(c) == -1)
            newstr->unit.push_back(table->unit[(unsigned char)c]);
    }

    return newstr;
}

str *str::swapcase() {
    str *r = new str(unit);
    int len = __len__();

    for(int i = 0; i < len; i++) {
        char c = unit[i];
        if( c >= 'a' && c <= 'z' )
            r->unit[i] = ::toupper(c);
        else if( c >= 'A' && c <= 'Z' )
            r->unit[i] = ::tolower(c);
    }

    return r;
}

str *str::center(int w, str *fill) {
    int len = __len__();
    if(w<=len)
        return this;

    if(!fill) fill = sp;
    str *r = fill->__mul__(w);

    int j = (w-len)/2;
    for(int i=0; i<len; i++)
        r->unit[j+i] = unit[i];

    return r;
}

__ss_int str::__cmp__(pyobj *p) {
    if (!p) return 1;
    str *b = (str *)p;
    int r = unit.compare(b->unit);
    if( r < 0 ) return -1;
    else if( r > 0 ) return 1;
    return 0;
}

__ss_bool str::__eq__(pyobj *p) {
    return __mbool(unit == ((str *)p)->unit);
}

str *str::__mul__(__ss_int n) { /* optimize */
    str *r = new str();
    if(n<=0) return r;
    __GC_STRING &s = r->unit;
    __ss_int ulen = unit.size();

    if(ulen == 1)
       r->unit = __GC_STRING(n, unit[0]);
    else {
        s.resize(ulen*n);

        for(__ss_int i=0; i<ulen*n; i+=ulen)
            s.replace(i, ulen, unit);
    }

    return r;
}
str *str::__imul__(__ss_int n) {
    return __mul__(n);
}

int str::__hash__() {
    if(hash != -1)
        return hash;
    long x;
    const unsigned char *data = (unsigned char *)unit.data();
    int len = __len__();
#ifdef __SS_FASTHASH
//-----------------------------------------------------------------------------
// MurmurHash2, by Austin Appleby
// http://sites.google.com/site/murmurhash/

// All code is released to the public domain. 
// For business purposes, Murmurhash is under the MIT license. 

// Note - This code makes a few assumptions about how your machine behaves -

// 1. We can read a 4-byte value from any address without crashing
// 2. sizeof(int) == 4

// And it has a few limitations -

// 1. It will not work incrementally.
// 2. It will not produce the same results on little-endian and big-endian
//    machines.

// 'm' and 'r' are mixing constants generated offline.
// They're not really 'magic', they just happen to work well.
    unsigned int seed = 12345678; /* XXX */
	const unsigned int m = 0x5bd1e995;
	const int r = 24;

	// Initialize the hash to a 'random' value

	x = seed ^ len;

	// Mix 4 bytes at a time into the hash

	while(len >= 4)
	{
		unsigned int k = *(unsigned int *)data;

		k *= m; 
		k ^= k >> r; 
		k *= m; 
		
		x *= m; 
		x ^= k;

		data += 4;
		len -= 4;
	}
	
	// Handle the last few bytes of the input array

	switch(len)
	{
        case 3: x ^= data[2] << 16;
        case 2: x ^= data[1] << 8;
        case 1: x ^= data[0];
                x *= m;
	};

	// Do a few final mixes of the hash to ensure the last few
	// bytes are well-incorporated.

	x ^= x >> 13;
	x *= m;
	x ^= x >> 15;
#else
    /* modified from CPython */
    x = *data << 7;
    while (--len >= 0)
        x = (1000003*x) ^ *data++;
    x ^= __len__();
    if (x == -1)
        x = -2;
#endif
    hash = x;
    return x; 
}

str *str::__add__(str *b) {
    str *s = new str();

    s->unit.reserve(unit.size()+b->unit.size());
    s->unit.append(unit);
    s->unit.append(b->unit);

    return s;
}
str *str::__iadd__(str *b) {
    return __add__(b);
}

str *__add_strs(int, str *a, str *b, str *c) {
    str *result = new str();
    int asize = a->unit.size();
    int bsize = b->unit.size();
    int csize = c->unit.size();
    if(asize == 1 && bsize == 1 && csize == 1) {
        result->unit.resize(3);
        result->unit[0] = a->unit[0];
        result->unit[1] = b->unit[0];
        result->unit[2] = c->unit[0];
    }
    else {
        result->unit.resize(asize+bsize+csize);
        memcpy((void *)(result->unit.data()), a->unit.data(), asize);
        int pos = asize;
        memcpy((void *)(result->unit.data()+pos), b->unit.data(), bsize);
        pos += bsize;
        memcpy((void *)(result->unit.data()+pos), c->unit.data(), csize);
    }
    return result;
}

str *__add_strs(int, str *a, str *b, str *c, str *d) {
    str *result = new str();
    int asize = a->unit.size();
    int bsize = b->unit.size();
    int csize = c->unit.size();
    int dsize = d->unit.size();
    if(asize == 1 && bsize == 1 && csize == 1 && dsize == 1) {
        result->unit.resize(4);
        result->unit[0] = a->unit[0];
        result->unit[1] = b->unit[0];
        result->unit[2] = c->unit[0];
        result->unit[3] = d->unit[0];
    }
    else {
        result->unit.resize(asize+bsize+csize+dsize);
        memcpy((void *)(result->unit.data()), a->unit.data(), asize);
        int pos = asize;
        memcpy((void *)(result->unit.data()+pos), b->unit.data(), bsize);
        pos += bsize;
        memcpy((void *)(result->unit.data()+pos), c->unit.data(), csize);
        pos += csize;
        memcpy((void *)(result->unit.data()+pos), d->unit.data(), dsize);
    }
    return result;
}

str *__add_strs(int, str *a, str *b, str *c, str *d, str *e) {
    str *result = new str();
    int asize = a->unit.size();
    int bsize = b->unit.size();
    int csize = c->unit.size();
    int dsize = d->unit.size();
    int esize = e->unit.size();
    if(asize == 1 && bsize == 1 && csize == 1 && dsize == 1 && esize == 1) {
        result->unit.resize(5);
        result->unit[0] = a->unit[0];
        result->unit[1] = b->unit[0];
        result->unit[2] = c->unit[0];
        result->unit[3] = d->unit[0];
        result->unit[4] = e->unit[0];
    }
    else {
        result->unit.resize(asize+bsize+csize+dsize+esize);
        memcpy((void *)(result->unit.data()), a->unit.data(), asize);
        int pos = asize;
        memcpy((void *)(result->unit.data()+pos), b->unit.data(), bsize);
        pos += bsize;
        memcpy((void *)(result->unit.data()+pos), c->unit.data(), csize);
        pos += csize;
        memcpy((void *)(result->unit.data()+pos), d->unit.data(), dsize);
        pos += dsize;
        memcpy((void *)(result->unit.data()+pos), e->unit.data(), esize);
    }
    return result;
}

str *__add_strs(int n, ...) {
    va_list ap;
    va_start(ap, n);

    int size;
    str *result = new str();

    size = 0;
    for(int i=0; i<n; i++) {
        size += len(va_arg(ap, str *));
    }
    va_end(ap);

    result->unit.resize(size);

    va_start(ap, n);
    size = 0;
    int pos = 0;
    for(int i=0; i<n; i++) {
        str *s = va_arg(ap, str *);

        memcpy((void *)(result->unit.data()+pos), s->unit.data(), s->unit.size());
        pos += s->unit.size();
    }
    va_end(ap);

    return result;
}

str *str::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    slicenr(x, l, u, s, __len__());

    if(s == 1)
        return new str(unit.substr(l, u-l));
    else {
        __GC_STRING r;
        if(!(x&1) && !(x&2) && s==-1) {
            int sz = unit.size();
            r.resize(sz);
            for(int i=0; i<sz; i++)
                r[i] = unit[sz-i-1];
        }
        else if(s > 0)
            for(int i=l; i<u; i += s)
                r += unit[i];
        else
            for(int i=l; i>u; i += s)
                r += unit[i];
        return new str(r);
    }
}

int str::__fixstart(int a, int b) {
    if(a == -1) return a;
    return a+b;
}

int str::find(str *s, int a) { return __fixstart(unit.substr(a, unit.size()-a).find(s->unit), a); }
int str::find(str *s, int a, int b) { return __fixstart(unit.substr(a, b-a).find(s->unit), a); }

int str::rfind(str *s, int a) { return __fixstart(unit.substr(a, unit.size()-a).rfind(s->unit), a); }
int str::rfind(str *s, int a, int b) { return __fixstart(unit.substr(a, b-a).rfind(s->unit), a); }

int str::__checkneg(int i) {
    if(i == -1)
        throw new ValueError(new str("substring not found"));
    return i;
}

int str::index(str *s, int a) { return __checkneg(find(s, a)); }
int str::index(str *s, int a, int b) { return __checkneg(find(s, a, b)); }

int str::rindex(str *s, int a) { return __checkneg(find(s, a)); }
int str::rindex(str *s, int a, int b) { return __checkneg(find(s, a, b)); }

__ss_int str::count(str *s, __ss_int start) { return count(s, start, __len__()); }
__ss_int str::count(str *s, __ss_int start, __ss_int end) {
    __ss_int i, count, one = 1;
    slicenr(7, start, end, one, __len__());

    i = start; count = 0;
    while( ((i = unit.find(s->unit, i)) != -1) && (i <= end-len(s)) )
    {
        i += len(s);
        count++;
    }

    return count;
}

__ss_bool str::startswith(str *s, __ss_int start) { return startswith(s, start, __len__()); }
__ss_bool str::startswith(str *s, __ss_int start, __ss_int end) {
    __ss_int i, j, one = 1;
    slicenr(7, start, end, one, __len__());

    for(i = start, j = 0; i < end && j < len(s); )
        if (unit[i++] != s->unit[j++])
            return False;

    return __mbool(j == len(s));
}

__ss_bool str::endswith(str *s, __ss_int start) { return endswith(s, start, __len__()); }
__ss_bool str::endswith(str *s, __ss_int start, __ss_int end) {
    __ss_int i, j, one = 1;
    slicenr(7, start, end, one, __len__());

    for(i = end, j = len(s); i > start && j > 0; )
        if (unit[--i] != s->unit[--j])
            return False;

    return True;
}

str *str::replace(str *a, str *b, int c) {
    __GC_STRING s = unit;
    int i, j, p;
    int asize = a->unit.size();
    int bsize = b->unit.size();
    j = p = 0;
    while( ((c==-1) || (j++ != c)) && (i = s.find(a->unit, p)) != -1 ) {
      s.replace(i, asize, b->unit);
      p = i + bsize + (asize?0:1);
    }
    return new str(s);
}

str *str::upper() {
    if(unit.size() == 1)
        return __char_cache[::toupper(unit[0])];

    str *toReturn = new str(*this);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), toupper);

    return toReturn;
}

str *str::lower() {
    if(unit.size() == 1)
        return __char_cache[::tolower(unit[0])];

    str *toReturn = new str(*this);
    std::transform(toReturn->unit.begin(), toReturn->unit.end(), toReturn->unit.begin(), tolower);

    return toReturn;
}

str *str::title() {
    str *r = new str(unit);
    unsigned int i = 0;
    while( (i != -1) && (i<unit.size()) )
    {
        r->unit[i] = ::toupper(r->unit[i]);
        i = unit.find(" ", i);
        if (i != -1)
            i++;
    }
    return r;
}

str *str::capitalize() {
    str *r = new str(unit);
    r->unit[0] = ::toupper(r->unit[0]);
    return r;
}

#ifdef __SS_BIND
str::str(PyObject *p) : hash(0) {
    if(!PyString_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (string expected)"));

    __class__ = cl_str_;
    unit = __GC_STRING(PyString_AsString(p), PyString_Size(p));
}

PyObject *str::__to_py__() {
    return PyString_FromStringAndSize(unit.c_str(), unit.size());
}
#endif

class_::class_(const char *name, int low, int high) {
    this->__name__ = new str(name);
    this->low = low; this->high = high;
}

str *class_::__repr__() {
    return (new str("class "))->__add__(__name__);
}

__ss_bool class_::__eq__(pyobj *c) {
    return __mbool(c == this);
}

/* file methods */

file::file() {
    print_opt.endoffile = print_opt.space = 0;
    print_opt.lastchar = '\n';
    universal_mode = false;
}

file::file(FILE *g) {
    f = g;
    print_opt.endoffile = print_opt.space = 0;
    print_opt.lastchar = '\n';
    universal_mode = false;
}

file::file(str *name, str *flags) {
    universal_mode = false;
    cr = false;
    if (!flags) {
        flags = new str("r");
    } else {
        for (__GC_STRING::iterator it = flags->unit.begin(); it != flags->unit.end(); ++it) {
            if (*it == 'u' || *it == 'U') {
                universal_mode = true;
                break;
            }
        }
    }
    f = fopen(name->unit.c_str(), flags->unit.c_str());
    this->name = name;
    this->mode = flags;
    if (!f)
        throw new IOError(__modct(new str("No such file or directory: '%s'"), 1, name));
    print_opt.endoffile = print_opt.space = 0;
    print_opt.lastchar = '\n';
}

file *open(str *name, str *flags) {
    return new file(name, flags);
}

int file::getchar() {
    int r;
    __check_closed();
    r = fgetc(f);

    if(ferror(f))
        throw new IOError();

    if (universal_mode) {
        if (r == '\r') {
            cr = true;
            return '\n';
        } else if (cr && r == '\n') {
            r = fgetc(f);
            if (ferror(f))
                throw new IOError();
            cr = (r == '\r');
        }
    }

    return r;
}

void *file::putchar(int c) {
    __check_closed();
    fputc(c, f);
    if(ferror(f))
        throw new IOError();
    return NULL;
}

void *file::write(str *s) {
    __check_closed();
  //  fputs(s->unit.c_str(), f);

    for(unsigned int i = 0; i < s->unit.size(); i++)
        putchar(s->unit[i]);

    return NULL;
}

void file::__check_closed() {
    if(closed)
        throw new ValueError(new str("I/O operation on closed file"));
}

void *file::seek(__ss_int i, __ss_int w) {
    __check_closed();
    fseek(f, i, w);
    print_opt.endoffile = 0; /* XXX add check */
    return NULL;
}

int file::tell() {
    __check_closed();
    return ftell(f);
}

void *file::writelines(pyseq<str *> *l) {
    __check_closed();
    for(int i=0; i<len(l); i++)
        write(l->__getitem__(i));
    return NULL;
}

str *file::readline(int n) {
    __check_closed();
    int i = 0;
    str *r = new str();

    while((n==-1) || (i < n)) {
        int c = getchar();
        if(c == EOF) {
            print_opt.endoffile = 1;
            break;
        }
        r->unit += c;
        if(c == '\n')
            break;
        i += 1;
    }

    return r;
}

str *file::read(int n) {
    __check_closed();
    int i = 0;
    str *r = new str();

    while((n==-1) || (i < n)) {
        int c = getchar();
        if(c == EOF) {
            print_opt.endoffile = 1;
            break;
        }
        r->unit += c;
        i += 1;
    }

    return r;
}

list<str *> *file::readlines() {
    __check_closed();
    list<str *> *lines = new list<str *>();
    while(!print_opt.endoffile) {
        str *line = readline();
        if(print_opt.endoffile && !len(line))
            break;
        lines->append(line);
    }

    return lines;
}

void *file::flush() {
    __check_closed();
    fflush(f);
    return NULL;
}

void *file::close() {
    fclose(f);
    closed = 1;
    return NULL;
}

int file::__ss_fileno() {
    __check_closed();
    return fileno(f);
}

str *file::__repr__() {
    return (new str("file '"))->__add__(name)->__add__(new str("'"));
}

void file::__enter__() { }

void file::__exit__() {
    close();
}

/* builtin functions */

str *pyobj::__repr__() {
    return __add_strs(3, new str("<"), __class__->__name__, new str(" instance>"));
}

str *raw_input(str *msg) {
    __GC_STRING s;
    if(msg)
        std::cout << msg->unit;
    std::getline(std::cin, s);
    if(std::cin.eof())
        throw new EOFError();
    return new str(s);
}

__ss_int __int(str *s, __ss_int base) {
    char *cp;
    __ss_int i;
#ifdef __SS_LONG
    i = strtoll(s->unit.c_str(), &cp, base);
#else
    i = strtol(s->unit.c_str(), &cp, base);
#endif
    if(*cp != '\0') {
        s = s->rstrip();
        #ifdef __SS_LONG
            i = strtoll(s->unit.c_str(), &cp, base);
        #else
            i = strtol(s->unit.c_str(), &cp, base);
        #endif
        if(*cp != '\0')
            throw new ValueError(new str("invalid literal for int()"));
    }
    return i;
}

template<> double __float(str *s) {
    return atof((char *)(s->unit.c_str()));
}

__ss_bool isinstance(pyobj *p, class_ *c) {
    int classnr = p->__class__->low;
    return __mbool(((classnr >= c->low) && (classnr <= c->high)));
}

__ss_bool isinstance(pyobj *p, tuple2<class_ *, class_ *> *t) {
    int classnr = p->__class__->low;
    for(int i = 0; i < t->__len__(); i++)
    {
       class_ *c = t->__getitem__(i);
       if ((classnr >= c->low) && (classnr <= c->high))
           return True;
    }
    return False;
}

static int range_len(int lo, int hi, int step) {
    /* modified from CPython */
    int n = 0;
    if ((lo < hi) && (step>0)) {
        unsigned int uhi = (unsigned int)hi;
        unsigned int ulo = (unsigned int)lo;
        unsigned int diff = uhi - ulo - 1;
        n = (int)(diff / (unsigned int)step + 1);
    }
    else {
        if ((lo > hi) && (step<0)) {
            unsigned int uhi = (unsigned int)lo;
            unsigned int ulo = (unsigned int)hi;
            unsigned int diff = uhi - ulo - 1;
            n = (int)(diff / (unsigned int)(-step) + 1);
        }
    }
    return n;
}

list<__ss_int> *range(__ss_int a, __ss_int b, __ss_int s) {
    list<__ss_int> *r;
    __ss_int i;
    int pos;

    r = new list<__ss_int>();
    pos = 0;
    i = a;

    if(s==0)
        __throw_range_step_zero();

    if(s==1) {
        r->units.resize(b-a);
        for(; i<b;i++)
            r->units[pos++] = i;

        return r;
    }

    r->units.resize(range_len(a,b,s));

    if(s>0) {
        while((i<b)) {
            r->units[pos++] = i;
            i += s;
        }
    }
    else {
        while((i>b)) {
            r->units[pos++] = i;
            i += s;
        }
    }

    return r;
}

list<__ss_int> *range(__ss_int n) {
    return range(0, n);
}

class __rangeiter : public __iter<__ss_int> {
public:
    __ss_int i, a, b, s;

    __rangeiter(__ss_int a, __ss_int b, __ss_int s) {
        this->__class__ = cl_rangeiter;

        this->a = a;
        this->b = b;
        this->s = s;
        i = a;
        if(s==0)
            throw new ValueError(new str("xrange() arg 3 must not be zero"));
    }

    __ss_int next() {
        if(s>0) {
            if(i<b) {
                i += s;
                return i-s;
            }
        }
        else if(i>b) {
                i += s;
                return i-s;
        }

        throw new StopIteration();
    }

};

__xrange::__xrange(__ss_int a, __ss_int b, __ss_int s) {
    this->a = a;
    this->b = b;
    this->s = s;
}

__iter<__ss_int> *__xrange::__iter__() {
    return new __rangeiter(a, b, s);
}

__ss_int __xrange::__len__() {
   return range_len(a, b, s);
}

str *__xrange::__repr__() {
    if(s==1) {
        if(a==0)
            return __modct(new str("xrange(%d)"), 1, ___box(b));
        else
            return __modct(new str("xrange(%d, %d)"), 2, ___box(a), ___box(b));
    }
    return __modct(new str("xrange(%d, %d, %d)"), 3, ___box(a), ___box(b), ___box(s)); /* XXX */
}

__xrange *xrange(__ss_int a, __ss_int b, __ss_int s) { return new __xrange(a,b,s); }
__xrange *xrange(__ss_int n) { return new __xrange(0, n, 1); }

__iter<__ss_int> *reversed(__xrange *x) {
   return new __rangeiter(x->a+(range_len(x->a,x->b,x->s)-1)*x->s, x->a-x->s, -x->s);
}

int ord(str *s) {
    if(len(s) != 1)
        throw new TypeError(__modct(new str("ord() expected a character, but string of length %d found"), 1, ___box(len(s))));
    return (unsigned char)(s->unit[0]);
}

/* representation */

template<> str *repr(double d) { return __str(d); }
#ifdef __SS_LONG
template<> str *repr(__ss_int i) { return __str(i); }
#endif
template<> str *repr(int i) { return __str(i); }
template<> str *repr(__ss_bool b) { return b.value?(new str("True")):(new str("False")); }
template<> str *repr(void *) { return new str("None"); }

str *__str(void *) { return new str("void"); }

/* get class pointer */

template<> class_ *__type(int) { return cl_int_; }
template<> class_ *__type(double) { return cl_float_; }

/* pow */

template<> __ss_int __power(__ss_int a, __ss_int b) {
    __ss_int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = (res*tmp);
        }
        tmp = (tmp*tmp);
        b = (b/2);
    }
    return res;
}

#ifdef __SS_LONG
__ss_int __power(__ss_int a, __ss_int b, __ss_int c) {
    __ss_int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = ((res*tmp)%c);
        }
        tmp = ((tmp*tmp)%c);
        b = (b/2);
    }
    return res;
}
#endif

int __power(int a, int b, int c) {
    int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = ((res*tmp)%c);
        }
        tmp = ((tmp*tmp)%c);
        b = (b/2);
    }
    return res;
}

complex *__power(complex *a, complex *b) {
    complex *r = new complex();
    double vabs, len, at, phase;
    if(b->real == 0 && b->imag == 0) {
        r->real = 1;
        r->imag = 0;
    }
    else if(a->real == 0 && a->imag == 0) {
        r->real = 0;
        r->imag = 0;
    }
    else {
        vabs = a->__abs__();
        len = std::pow(vabs,b->real);
        at = std::atan2(a->imag, a->real);
        phase = at*b->real;
        if (b->imag != 0.0) {
            len /= std::exp(at*b->imag);
            phase += b->imag*std::log(vabs);
        }
        r->real = len*std::cos(phase);
        r->imag = len*std::sin(phase);
    }
    return r;
}
complex *__power(complex *a, __ss_int b) {
    return __power(a, new complex(b, 0));
}
complex *__power(complex *a, double b) {
    return __power(a, new complex(b, 0));
}

/* division */

tuple2<complex *, complex *> *divmod(complex *a, double b) { return a->__divmod__(b); }
tuple2<complex *, complex *> *divmod(complex *a, __ss_int b) { return a->__divmod__(b); }

/* slicing */

void slicenr(__ss_int x, __ss_int &l, __ss_int &u, __ss_int &s, __ss_int len) {
    if((x&4) && (s == 0))
        throw new ValueError(new str("slice step cannot be zero"));

    if (!(x&4))
        s = 1;

    if (l>=len)
        l = len;
    else if (l<0) {
        l = len+l;
        if(l<0)
            l = 0;
    }
    if (u>=len)
        u = len;
    else if (u<0) {
        u = len+u;
        if(u<0)
            u = 0;
    }

    if(s<0) {
        if (!(x&1))
            l = len-1;
        if (!(x&2))
            u = -1;
    }
    else {
        if (!(x&1))
            l = 0;
        if (!(x&2))
            u = len;
    }
}

#ifdef __SS_LONG
str *__str(__ss_int i, __ss_int base) {
    if(i<10 && i>=0 && base==10)
        return __char_cache['0'+i];
    char buf[24];
    char *psz = buf+23;
/*    if(i==INT_MIN)
        return new str("-2147483648"); */
    int neg = i<0;
    *psz = 0;
    if(neg) i = -i;
    if(base == 10) {
        int pos;
        while(i > 999) {
            pos = 4*(i%1000);
            i = i/1000;
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
            *(--psz) = __str_cache[pos+2];
        }
        pos = 4*i;
        if(i>99) {
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
            *(--psz) = __str_cache[pos+2];
        }
        else if(i>9) {
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
        }
        else
            *(--psz) = __str_cache[pos];
    }
    else do {
        *(--psz) = "0123456789abcdefghijklmnopqrstuvwxyz"[i%base];
        i = i/base;
    } while(i);
    if(neg) *(--psz) = '-';
    return new str(psz, buf+23-psz);
}
#endif

str *__str(int i, int base) {
    if(base==10 && i<10 && i>=0)
        return __char_cache['0'+i];

    char buf[12];
    char *psz = buf+11;
    if(i==INT_MIN)
        return new str("-2147483648");
    int neg = i<0;
    *psz = 0;
    if(neg) i = -i;
    if(base == 10) {
        int pos;
        while(i > 999) {
            pos = 4*(i%1000);
            i = i/1000;
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
            *(--psz) = __str_cache[pos+2];
        }
        pos = 4*i;
        if(i>99) {
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
            *(--psz) = __str_cache[pos+2];
        }
        else if(i>9) {
            *(--psz) = __str_cache[pos];
            *(--psz) = __str_cache[pos+1];
        }
        else
            *(--psz) = __str_cache[pos];
    }
    else do {
        *(--psz) = "0123456789abcdefghijklmnopqrstuvwxyz"[i%base];
        i = i/base;
    } while(i);
    if(neg) *(--psz) = '-';
    return new str(psz, buf+11-psz);
}

str *__str(__ss_bool b) {
    if(b) return new str("True");
    return new str("False");
}

template<> str *hex(int i) {
    if(i<0)
        return (new str("-0x"))->__add__(__str(-i, 16));
    else
        return (new str("0x"))->__add__(__str(i, 16));
}
template<> str *hex(__ss_bool b) { return hex(b.value); }

template<> str *oct(int i) {
    if(i<0)
        return (new str("-0"))->__add__(__str(-i, 8));
    else if(i>0)
        return (new str("0"))->__add__(__str(i, 8));
    else
      return new str("0");
}
template<> str *oct(__ss_bool b) { return oct(b.value); }

template<> str *bin(int i) {
    if(i<0)
        return (new str("-0b"))->__add__(__str(-i, 2));
    else
        return (new str("0b"))->__add__(__str(i, 2));
}
template<> str *bin(__ss_bool b) { return bin(b.value); }

str *__str() { return new str(""); } /* XXX optimize */

template<> str *__str(double t) {
    std::stringstream ss;
    ss.precision(12);
    ss << std::showpoint << t;
    __GC_STRING s = ss.str().c_str();
    if(s.find('e') == -1)
    {
        unsigned int j = s.find_last_not_of("0");
        if( s[j] == '.') j++;
        s = s.substr(0, j+1);
    }
    return new str(s);
}

/* mod helpers */

#if defined(WIN32) || defined(__sun)
#   if defined (_MSC_VER)
#       define va_copy(dest, src) ((void)((dest) = (src)))
#   endif
int vasprintf(char **ret, const char *format, va_list ap)
{
    va_list ap2;
    int len= 100;        /* First guess at the size */
    if ((*ret= (char *)malloc(len)) == NULL) return -1;
    while (1)
    {
        int nchar;
        va_copy(ap2, ap);
        nchar= vsnprintf(*ret, len, format, ap2);
        if (nchar > -1 && nchar < len) return nchar;
        if (nchar > len)
            len= nchar+1;
        else
            len*= 2;
        if ((*ret= (char *)realloc(*ret, len)) == NULL)
        {
            free(*ret);
            return -1;
        }
    }
}

int asprintf(char **ret, const char *format, ...)
{
    va_list ap;
    int nc;
    va_start (ap, format);
    nc= vasprintf(ret, format, ap);
    va_end(ap);
    return nc;
}
#endif

int __fmtpos(str *fmt) {
    int i = fmt->unit.find('%');
    if(i == -1)
        return -1;
    return fmt->unit.find_first_not_of(__fmtchars, i+1);
}

int __fmtpos2(str *fmt) {
    unsigned int i = 0;
    while((i = fmt->unit.find('%', i)) != -1) {
        if(i != fmt->unit.size()-1) {
            char nextchar = fmt->unit[i+1];
            if(nextchar == '%')
                i++;
            else if(nextchar == '(')
                return i;
        }
        i++;
    }
    return -1;
}

template<class T> str *do_asprintf(const char *fmt, T t, pyobj *a1, pyobj *a2) {
    char *d;
    int x;
    str *r;
    if(a2)
        x = asprintf(&d, fmt, ((int)(((int_ *)a1)->unit)), ((int)(((int_ *)a2)->unit)), t);
    else if(a1)
        x = asprintf(&d, fmt, ((int)(((int_ *)a1)->unit)), t);
    else
        x = asprintf(&d, fmt, t);
    r = new str(d);
    free(d);
    return r;
}

void __modfill(str **fmt, pyobj *t, str **s, pyobj *a1, pyobj *a2) {
    char c;
    int i = (*fmt)->unit.find('%');
    int j = __fmtpos(*fmt);
    *s = new str((*s)->unit + (*fmt)->unit.substr(0, i));
    str *add;

    c = (*fmt)->unit[j];
    if(c == 's' or c == 'r') {
        if(c == 's') add = __str(t);
        else add = repr(t);
        (*fmt)->unit[j] = 's';
        add = do_asprintf((*fmt)->unit.substr(i, j+1-i).c_str(), add->unit.c_str(), a1, a2);
    } else if(c  == 'c')
        add = __str(t);
    else if(c == '%')
        add = new str("%");
    else if(t->__class__ == cl_int_) {
#ifdef __SS_LONG
        add = do_asprintf(((*fmt)->unit.substr(i, j-i)+__GC_STRING("ll")+(*fmt)->unit[j]).c_str(), ((int_ *)t)->unit, a1, a2);
#else
        add = do_asprintf((*fmt)->unit.substr(i, j+1-i).c_str(), ((int_ *)t)->unit, a1, a2);
#endif
    } else { /* cl_float_ */
        if(c == 'H') {
            (*fmt)->unit.replace(j, 1, ".12g");
            j += 3;
        }
        add = do_asprintf((*fmt)->unit.substr(i, j+1-i).c_str(), ((float_ *)t)->unit, a1, a2);
        if(c == 'H' && ((float_ *)t)->unit-((int)(((float_ *)t)->unit)) == 0)
            add->unit += ".0";
    }
    *s = (*s)->__add__(add);
    *fmt = new str((*fmt)->unit.substr(j+1, (*fmt)->unit.size()-j-1));
}

pyobj *modgetitem(list<pyobj *> *vals, int i) {
    if(i==len(vals))
        throw new TypeError(new str("not enough arguments for format string"));
    return vals->__getitem__(i);
}

str *__mod4(str *fmts, list<pyobj *> *vals) {
    int i, j;
    str *r = new str();
    str *fmt = new str(fmts->unit);
    i = 0;
    while((j = __fmtpos(fmt)) != -1) {
        pyobj *p, *a1, *a2;

        int asterisks = std::count(fmt->unit.begin(), fmt->unit.begin()+j, '*');
        a1 = a2 = NULL;
        if(asterisks==1) {
            a1 = modgetitem(vals, i++);
        } else if(asterisks==2) {
            a1 = modgetitem(vals, i++);
            a2 = modgetitem(vals, i++);
        }

        char c = fmt->unit[j];
        if(c != '%')
            p = modgetitem(vals, i++);
    
        switch(c) {
            case 'c':
                __modfill(&fmt, mod_to_c2(p), &r, a1, a2);
                break;
            case 's': 
            case 'r':
                __modfill(&fmt, p, &r, a1, a2);
                break;
            case 'd':
            case 'i':
            case 'o':
            case 'u':
            case 'x':
            case 'X':
                __modfill(&fmt, mod_to_int(p), &r, a1, a2);
                break;
            case 'e':
            case 'E':
            case 'f':
            case 'F':
            case 'g':
            case 'G':
            case 'H':
                __modfill(&fmt, mod_to_float(p), &r, a1, a2);
                break;
            case '%':
                __modfill(&fmt, NULL, &r, a1, a2);
                break;
            default:
                throw new ValueError(new str("unsupported format character"));
        }
    }
    if(i!=len(vals))
        throw new TypeError(new str("not all arguments converted during string formatting"));

    r->unit += fmt->unit;
    return r;
}

str *__mod5(list<pyobj *> *vals, str *sep) {
    __mod5_cache->units.resize(0);
    for(int i=0;i<len(vals);i++) {
        pyobj *p = vals->__getitem__(i);
        if(p == NULL)
            __mod5_cache->append(__fmt_s);
        else if(p->__class__ == cl_float_)
            __mod5_cache->append(__fmt_H);
        else if(p->__class__== cl_int_)
            __mod5_cache->append(__fmt_d);
        else
            __mod5_cache->append(__fmt_s);
    }
    str *s = __mod4(sep->join(__mod5_cache), vals);
    return s;
}

str *__modcd(str *fmt, list<str *> *names, ...) {
    int i;
    list<pyobj *> *vals = new list<pyobj *>();
    va_list args;
    va_start(args, names);
    for(i=0; i<len(names); i++)
        vals->append(va_arg(args, pyobj *));
    va_end(args);

    str *naam;
    int pos, pos2;
    dict<str *, pyobj *> *d = new dict<str *, pyobj *>(__zip(2, names, vals));
    str *const_6 = new str(")");
    list<pyobj *> *values = new list<pyobj *>();

    while((pos = __fmtpos2(fmt)) != -1) {
        pos2 = fmt->find(const_6, pos);
        naam = fmt->__slice__(3, (pos+2), pos2, 0);
        values->append(d->__getitem__(naam));
        fmt = (fmt->__slice__(2, 0, (pos+1), 0))->__add__(fmt->__slice__(1, (pos2+1), 0, 0));
    }

    return __mod4(fmt, values);
}

/* mod */

str *mod_to_c2(pyobj *t) {
    if(t == NULL)
        throw new TypeError(new str("an integer is required"));
    if(t->__class__ == cl_str_) {
        if(len((str *)t) == 1)
            return (str *)t;
        else
            throw new TypeError(new str("%c requires int or char"));
    }
    int value;
    if(t->__class__ == cl_int_)
        value = ((int_ *)t)->unit;
    else if(t->__class__ == cl_float_)
        value = ((int)(((float_ *)t)->unit));
    else
        value = t->__int__();
    if(value < 0)
        throw new OverflowError(new str("unsigned byte integer is less than minimum"));
    else if(value > 255)
        throw new OverflowError(new str("unsigned byte integer is greater than minimum"));
    return chr(value);
}

int_ *mod_to_int(pyobj *t) {
    if(t == NULL)
        throw new TypeError(new str("int argument required"));
    if(t->__class__ == cl_int_)
        return (int_ *)t;
    else if(t->__class__ == cl_float_)
        return new int_(((int)(((float_ *)t)->unit)));
    else
        return new int_(t->__int__());
}

float_ *mod_to_float(pyobj *t) {
    if(t == NULL)
        throw new TypeError(new str("float argument required"));
    if(t->__class__ == cl_float_)
        return (float_ *)t;
    else if(t->__class__ == cl_int_)
        return new float_(((int_ *)t)->unit);
    throw new TypeError(new str("float argument required"));
}

str *__modct(str *fmt, int n, ...) {
     list<pyobj *> *vals = new list<pyobj *>();
     va_list args;
     va_start(args, n);
     for(int i=0; i<n; i++)
         vals->append(va_arg(args, pyobj *));
     va_end(args);
     str *s = __mod4(fmt, vals);
     return s;
}

#ifdef __SS_LONG
int_ *___box(__ss_int i) {
    return new int_(i);
}
#endif
int_ *___box(int i) {
    return new int_(i);
}
int_ *___box(unsigned int i) {
    return new int_(i);
}
int_ *___box(unsigned long i) {
    return new int_(i);
}
int_ *___box(unsigned long long i) {
    return new int_(i);
}
bool_ *___box(__ss_bool b) {
    return new bool_(b);
}
float_ *___box(double d) {
    return new float_(d);
}

/* print .., */

void __ss_exit(int code) {
    throw new SystemExit(code);
}

void __start(void (*initfunc)()) {
    int code = 0;
    try {
        initfunc();
    } catch (SystemExit *s) {
        if(s->message)
            print2(NULL, 0, 1, s->message);
        code = s->code;
    }
    if(__ss_stdout->print_opt.lastchar != '\n')
        __ss_stdout->write(nl);
    std::exit(code);
}

void print(int n, file *f, str *end, str *sep, ...) {
    __print_cache->units.resize(0);
    va_list args;
    va_start(args, sep);
    for(int i=0; i<n; i++)
        __print_cache->append(va_arg(args, pyobj *));
    va_end(args);
    str *s = __mod5(__print_cache, sep?sep:sp);
    if(!end)
        end = nl;
    if(f) {
        f->write(s);
        f->write(end);
    }
    else 
        printf("%s%s", s->unit.c_str(), end->unit.c_str());
}

void print2(file *f, int comma, int n, ...) {
    __print_cache->units.resize(0);
    va_list args;
    va_start(args, n);
    for(int i=0; i<n; i++)
        __print_cache->append(va_arg(args, pyobj *));
    va_end(args);
    if (!f)
        f = __ss_stdout;
    print_options *p_opt = &f->print_opt;
    str *s = __mod5(__print_cache, sp);
    if(len(s)) {
        if(p_opt->space && (!isspace(p_opt->lastchar) || p_opt->lastchar==' ') && s->unit[0] != '\n') 
            f->write(sp); /* space */
        f->write(s);
        p_opt->lastchar = s->unit[len(s)-1];
    }
    else if (comma)
        p_opt->lastchar = ' ';
    if(!comma) {
        f->write(nl); /* newline */
        p_opt->lastchar = '\n';
    }
    p_opt->space = comma;
}

/* str, file iteration */

__iter<str *> *str::__iter__() {
    return new __striter(this);
}

__striter::__striter(str *p) {
    this->p = p;
    counter = 0;
    size = p->unit.size();
}

str *__striter::next() {
    if(counter == size)
        throw new StopIteration();
    return __char_cache[((unsigned char)(p->unit[counter++]))];
}

__iter<str *> *file::__iter__() {
    return new __fileiter(this);
}

str *file::next() {
    if(print_opt.endoffile)
        throw new StopIteration();
    str *line = readline();
    if(print_opt.endoffile && !len(line))
        throw new StopIteration();
    return line;
}

__fileiter::__fileiter(file *p) {
    this->p = p;
}

str *__fileiter::next() {
    return p->next();
}

/* map, filter, reduce */

str *filter(void *func, str *a) { return filter(((int(*)(str *))(func)), a); }

str *reduce(str *(*func)(str *, str *), str *a) { return reduce(func, (pyiter<str *> *)a); }
str *reduce(str *(*func)(str *, str *), str *a, str *initial) { return reduce(func, (pyiter<str *> *)a, initial); }

/* glue */

#ifdef __SS_BIND
#ifdef __SS_LONG
template<> PyObject *__to_py(__ss_int i) { return PyLong_FromLongLong(i); }
#endif
template<> PyObject *__to_py(int i) { return PyInt_FromLong(i); }
template<> PyObject *__to_py(__ss_bool i) { return PyBool_FromLong(i.value); }
template<> PyObject *__to_py(double d) { return PyFloat_FromDouble(d); }
template<> PyObject *__to_py(void *v) { Py_INCREF(Py_None); return Py_None; }

#ifdef __SS_LONG
template<> __ss_int __to_ss(PyObject *p) {
    if(PyLong_Check(p))
        return PyLong_AsLongLong(p);
    else if (PyInt_Check(p))
        return PyInt_AsLong(p);
    else
        throw new TypeError(new str("error in conversion to Shed Skin (integer expected)"));
}
#endif

template<> int __to_ss(PyObject *p) {
    if(!PyInt_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (integer expected)"));
    return PyInt_AsLong(p);
}

template<> __ss_bool __to_ss(PyObject *p) {
    if(!PyBool_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (boolean expected)"));
    return (p==Py_True)?(__mbool(true)):(__mbool(false));
}

template<> double __to_ss(PyObject *p) {
    if(!PyInt_Check(p) and !PyFloat_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (float or int expected)"));
    return PyFloat_AsDouble(p);
}

template<> void * __to_ss(PyObject *p) {
    if(p!=Py_None)
        throw new TypeError(new str("error in conversion to Shed Skin (None expected)"));
    return NULL;
}
#endif

/* Exceptions */
OSError::OSError(str *filename) {
    this->filename = filename;
    __ss_errno = errno;
    message = new str("");
    strerror = new str(::strerror(__ss_errno));
}
str *OSError::__str__() {
    return __add_strs(7, new str("[Errno "), __str(__ss_errno), new str("] "), strerror, new str(": '"), filename, new str("'"));
}
str *OSError::__repr__() {
    return __add_strs(5, new str("OSError("), __str(__ss_errno), new str(", '"), strerror, new str("')"));
}

template <> void *myallocate<__ss_int>(int n) { return GC_MALLOC_ATOMIC(n); }
template <> void *myallocate<__ss_int, __ss_int>(int n) { return GC_MALLOC_ATOMIC(n); }

template<> int __none() { throw new TypeError(new str("mixing None with int")); }
template<> double __none() { throw new TypeError(new str("mixing None with float")); }

list<tuple2<void *, void *> *> *__zip(int) {
    return new list<tuple2<void *, void *> *>();
}

/* pyobj */

str *pyobj::__str__() { return __repr__(); }

int pyobj::__hash__() {
#if defined( _MSC_VER )
    return std::hash<intptr_t>()((intptr_t)this);
#else
    return __gnu_cxx::hash<intptr_t>()((intptr_t)this);
#endif
}

__ss_int pyobj::__cmp__(pyobj *p) {
    return __cmp<void *>(this, p);
}

__ss_bool pyobj::__eq__(pyobj *p) { return __mbool(this == p); }
__ss_bool pyobj::__ne__(pyobj *p) { return __mbool(!__eq__(p)); }

__ss_bool pyobj::__gt__(pyobj *p) { return __mbool(__cmp__(p) == 1); }
__ss_bool pyobj::__lt__(pyobj *p) { return __mbool(__cmp__(p) == -1); }
__ss_bool pyobj::__ge__(pyobj *p) { return __mbool(__cmp__(p) != -1); }
__ss_bool pyobj::__le__(pyobj *p) { return __mbool(__cmp__(p) != 1); }

pyobj *pyobj::__copy__() { return this; }
pyobj *pyobj::__deepcopy__(dict<void *, pyobj *> *) { return this; }

__ss_int pyobj::__len__() { return 1; } /* XXX exceptions? */
__ss_int pyobj::__int__() { return 0; }

__ss_bool pyobj::__nonzero__() { return __mbool(__len__() != 0); }

/* object */

object::object() { this->__class__ = cl_object; }

#ifdef __SS_BIND
PyObject *__ss__newobj__(PyObject *, PyObject *args, PyObject *kwargs) {
    PyObject *cls = PyTuple_GetItem(args, 0);
    PyObject *__new__ = PyObject_GetAttrString(cls, "__new__");
    return PyObject_Call(__new__, args, kwargs);
}
#endif

} // namespace __shedskin__
