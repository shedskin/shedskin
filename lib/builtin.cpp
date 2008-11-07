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

class_ *cl_class_, *cl_none, *cl_str_, *cl_int_, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict, *cl_set, *cl_object, *cl_rangeiter;

str *sp;
__GC_STRING ws, __fmtchars;
__GC_VECTOR(str *) __char_cache;


void __init() {
    GC_INIT();
#ifdef __SS_BIND
    Py_Initialize();
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

    ws = " \n\r\t\f\v";
    __fmtchars = "diouxXeEfFgGhcrs%";
    sp = new str(" ");

    for(int i=0;i<256;i++) {
        char c = i;
        __char_cache.push_back(new str(&c, 1));
    }
}

double __portableround(double x) {
    if(x<0) return ceil(x-0.5);
    return floor(x+0.5);
}

/* int_ methods */

int_::int_(int i) {
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
    if (__bool(m)) {
        complex *c = (parsevalue(m->group(new str("one"))))->__add__(parsevalue(m->group(new str("two"))));
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

    if ((!__bool(s))) {
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
    c->real = ((int)c->real);
    c->imag = 0;
    return c;
}
complex *complex::__floordiv__(double b) {
    complex *c = __div__(b);
    c->real = ((int)c->real);
    c->imag = 0;
    return c;
}

complex *complex::__mod__(complex *b) {
    complex *c = __div__(b);
    return __sub__(b->__mul__(((int)c->real)));
}
complex *complex::__mod__(double b) {
    complex *c = __div__(b);
    return __sub__(b*((int)c->real));
}

tuple2<complex *, complex *> *complex::__divmod__(complex *b) {
    return new tuple2<complex *, complex *>(2, __floordiv__(b), __mod__(b));
}
tuple2<complex *, complex *> *complex::__divmod__(double b) {
    return new tuple2<complex *, complex *>(2, __floordiv__(b), __mod__(b));
}

int complex::__eq__(pyobj *p) {
    if(p->__class__ != cl_complex)
        return 0;
    return real == ((complex *)p)->real && imag == ((complex *)p)->imag;
}

int complex::__hash__() {
    return ((int)imag)*1000003+((int)real);
}

int complex::__nonzero__() {
    return real != 0 || imag != 0;
}

str *complex::__repr__() {
    str *left, *middle, *right;
    if(real==0) 
        return __modct(new str("%gj"), 1, __box(imag));
    left = __modct(new str("(%g"), 1, __box(real));
    if(imag<0) 
        middle = new str("");
    else
        middle = new str("+");
    right = __modct(new str("%gj)"), 1, __box(imag));
    return __add_strs(3, left, middle, right);
}

/* str methods */

str::str() : cached_hash(0) {
    __class__ = cl_str_;
}

str::str(const char *s) : unit(s), cached_hash(0) {
    __class__ = cl_str_;
}

str::str(__GC_STRING s) : unit(s), cached_hash(0) {
    __class__ = cl_str_;
}

str::str(const char *s, int size) : cached_hash(0), unit(__GC_STRING(s, size)) { /* '\0' delimiter in C */
    __class__ = cl_str_;
}

str *str::__getitem__(int i) {
    i = __wrap(this, i);
    return __char_cache[(unsigned char)unit[i]];
}
str *str::__getfirst__() {
    return __getitem__(0);
}
str *str::__getsecond__() {
    return __getitem__(1);
}

int str::__len__() {
    return unit.size();
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
    for(int i=0; i<unit.size(); i++)
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

int str::__contains__(str *s) {
    return unit.find(s->unit) != -1;
}

int str::isspace() {
    return unit.size() && (unit.find_first_not_of(ws) == -1);
}

int str::isdigit() {
    return __ctype_function(&::isdigit);
}

int str::isalpha() {
    return __ctype_function(&::isalpha);
}

int str::isalnum() {
    return __ctype_function(&::isalnum);
}

int str::__ctype_function(int (*cfunc)(int))
{
  int i, l = unit.size();
  if(!l) 
      return 0;
  
  for(i = 0; i < l; i++) 
      if(!cfunc((int)unit[i])) return 0;
  
  return 1;
}

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

int str::islower() {
    return __ctype_function(&::islower);
}
int str::isupper() {
    return __ctype_function(&::isupper);
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

int str::istitle(void)
{
    int i, len;
    
    len = unit.size();
    if(!len)
        return 0;

    for(i = 0; i < len; )
    {
        for( ; !::isalpha((int)unit[i]) && i < len; i++) ;
        if(i == len) break;
        
        if(!::isupper((int)unit[i])) return 0;
        i++;
        
        for( ; ::islower((int)unit[i]) && i < len; i++) ;
        if(i == len) break;
        
        if(::isalpha((int)unit[i])) return 0;
    }
    
    return 1;
}

list<str *> *str::splitlines(int keepends)
{
    list<str *> *r = new list<str *>();
    int i, j, endlen;
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
    int sep_iter, chunk_iter = 0, tmp, num_splits = 0;
    list<str *> *result = new list<str *>();

    if (sp == NULL)
    {
#define next_separator(iter) (s.find_first_of(ws, (iter)))
#define skip_separator(iter) (s.find_first_not_of(ws, (iter)))

        if(next_separator(chunk_iter) == 0) 
            chunk_iter = skip_separator(chunk_iter);
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

int str::__cmp__(pyobj *p) {
    str *b = (str *)p;
    int r = unit.compare(b->unit);
    if( r < 0 ) return -1;
    else if( r > 0 ) return 1;
    return 0;
}

int str::__eq__(pyobj *p) {
    return unit == ((str *)p)->unit;
}

str *str::__mul__(int n) { /* optimize */
    str *r = new str();
    if(n<=0) return r;
    __GC_STRING &s = r->unit;
    int ulen = unit.size();

    if(ulen == 1)
       r->unit = __GC_STRING(n, unit[0]);
    else {
        s.resize(ulen*n);

        for(int i=0; i<ulen*n; i+=ulen)
            s.replace(i, ulen, unit);
    }

    return r;
}
str *str::__imul__(int n) { 
    return __mul__(n);
}

/* ======================================================================== */

/* (C) 2004, 2005 Paul Hsieh. Covered under the Paul Hsieh derivative license.
   http://www.azillionmonkeys.com/qed/{hash,weblicense}.html  */

#define get16bits(d) (*((const uint16_t *) (d)))

static inline uint32_t SuperFastHash (const char * data, int len) {
    uint32_t hash = 0, tmp;
    int rem;

    if (len <= 0 || data == NULL) return 0;

    rem = len & 3;
    len >>= 2;

    /* Main loop */
    for (;len > 0; len--) {
        hash  += get16bits (data);
        tmp    = (get16bits (data+2) << 11) ^ hash;
        hash   = (hash << 16) ^ tmp;
        data  += 2*sizeof (uint16_t);
        hash  += hash >> 11;
    }

    /* Handle end cases */
    switch (rem) {
        case 3: hash += get16bits (data);
                hash ^= hash << 16;
                hash ^= data[sizeof (uint16_t)] << 18;
                hash += hash >> 11;
                break;
        case 2: hash += get16bits (data);
                hash ^= hash << 11;
                hash += hash >> 17;
                break;
        case 1: hash += *data;
                hash ^= hash << 10;
                hash += hash >> 1;
    }

    /* Force "avalanching" of final 127 bits */
    hash ^= hash << 3;
    hash += hash >> 5;
    hash ^= hash << 4;
    hash += hash >> 17;
    hash ^= hash << 25;
    hash += hash >> 6;

    return hash;
}

/* ======================================================================== */

int str::__hash__() {
    if(cached_hash) 
        return cached_hash;
    cached_hash = SuperFastHash(unit.c_str(), unit.size());
    return cached_hash;

    //return __gnu_cxx::hash<char *>()(unit.c_str());
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

str *str::__join(pyseq<str *> *l, int total_len) {
    __GC_STRING s;
    s.resize(total_len);
    int k = 0;
    for(int i = 0; i < len(l); i++) {
        __GC_STRING &t = l->units[i]->unit;

        memcpy((void *)(s.data()+k), t.data(), t.size());
        k += t.size();

        if(unit.size()) {
            memcpy((void *)(s.data()+k), unit.data(), unit.size());
            k += unit.size();
        } 
    }
    return new str(s);
}

str *str::join(pyiter<str *> *l) { 
    list<str *> *rl = new list<str *>();
    str *i;
    int count, total_len;
    count = total_len = 0;
    __iter<str *> *__0;
    FOR_IN(i, l, 0)
        rl->append(i);
        total_len += i->unit.size();
        ++count;
    END_FOR
    if(total_len)
        total_len += (count-1)*unit.size();
    return __join(rl, total_len);
} 

str *str::join(pyseq<str *> *l) {
    int total_len = 0;
    __GC_VECTOR(str *)::const_iterator it;
    for(it = l->units.begin(); it < l->units.end(); it++)
        total_len += (*it)->unit.size();
    if(total_len)
        total_len += (len(l)-1)*unit.size();
    return __join(l, total_len);
}

str *str::__slice__(int x, int l, int u, int s) {
    __GC_STRING r;
    slicenr(x, l, u, s, __len__());

    if(s > 0)
        for(int i=l; i<u; i += s)
            r += unit[i];
    else
        for(int i=l; i>u; i += s)
            r += unit[i];

    return new str(r);
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

int str::count(str *s, int start) { return count(s, start, __len__()); }
int str::count(str *s, int start, int end) {
    int i, count, one = 1;
    slicenr(7, start, end, one, __len__());

    i = start; count = 0;
    while( ((i = unit.find(s->unit, i)) != -1) && (i <= end-len(s)) )
    {
        i += len(s);
        count++;
    }

    return count; 
}

int str::startswith(str *s, int start) { return startswith(s, start, __len__()); }
int str::startswith(str *s, int start, int end) {
    int i, j, one = 1;
    slicenr(7, start, end, one, __len__());

    for(i = start, j = 0; i < end && j < len(s); )
        if (unit[i++] != s->unit[j++])
            return 0;

    return j == len(s); 
}

int str::endswith(str *s, int start) { return endswith(s, start, __len__()); }
int str::endswith(str *s, int start, int end) {
    int i, j, one = 1;
    slicenr(7, start, end, one, __len__());

    for(i = end, j = len(s); i > start && j > 0; )
        if (unit[--i] != s->unit[--j])
            return 0; 

    return 1;
}

str *str::replace(str *a, str *b, int c) {
    __GC_STRING s = unit;
    int i, j = 0;
    while( ((c==-1) || (j++ != c)) && (i = s.find(a->unit)) != -1 ) 
        s.replace(i, a->unit.size(), b->unit);
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
    int i = 0;
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

/* str *str::sorted() {
    str *s = new str(unit);
    sort(s->unit.begin(), s->unit.end());
    return s;
} */

#ifdef __SS_BIND
str::str(PyObject *p) : cached_hash(0) {
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

int class_::__eq__(pyobj *c) {
    return c == this;
}

/* file methods */

file::file() {
    endoffile=print_space=0;
    print_lastchar='\n';
}

file::file(FILE *g) {
    f = g;
    endoffile=print_space=0;
    print_lastchar='\n';
}

file::file(str *name, str *flags) {
    if (!flags)
        flags = new str("r");
    f = fopen(name->unit.c_str(), flags->unit.c_str());
    this->name = name;
    this->mode = flags;
    if(!f) 
       throw new IOError(__modct(new str("No such file or directory: '%s'"), 1, name));
    endoffile=print_space=0;
    print_lastchar='\n';
}

file *open(str *name, str *flags) {
    return new file(name, flags);
}

int file::getchar() {
    __check_closed();
    return fgetc(f);
}

void *file::putchar(int c) {
    __check_closed();
    fputc(c, f);
    return NULL;
}

void *file::write(str *s) {
    __check_closed();
  //  fputs(s->unit.c_str(), f);

    for(int i = 0; i < s->unit.size(); i++)
        putchar(s->unit[i]);

    return NULL;
}

void file::__check_closed() {
    if(closed)
        throw new ValueError(new str("I/O operation on closed file"));
}

void *file::seek(int i, int w) {
    __check_closed();
    fseek(f, i, w);
    endoffile = 0; /* XXX add check */
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
            endoffile = 1;
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
            endoffile = 1;
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
    while(!endoffile) {
        str *line = readline(); 
        if(endoffile && !len(line))
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

/* builtin functions */

str *pyobj::__repr__() {
    return __class__->__name__->__add__(new str(" instance"));
}

int whatsit(__GC_STRING &s) {
    int i = -1;
    int count = 0;

    while((i = s.find("%", i+1)) > -1)
    {
        int j = s.find_first_of("diouxXeEfFgGhcrs", i);
        s.replace(i, j-i+1, "%s");
        count += 1;
    }

    return count;
}

str *raw_input(str *msg) {
    __GC_STRING s;
    if(msg)
        std::cout << msg->unit;
    std::getline(std::cin, s);
    return new str(s); 
}

int __int() { return 0; }

template<> int __int(str *s) { return __int(s, 10); }
template<> int __int(int i) { return i; }
template<> int __int(bool b) { return b; }
template<> int __int(double d) { return (int)d; }

int __int(str *s, int base) {
    char *cp;
    s = s->strip();
    int i = strtol(s->unit.c_str(), &cp, base);
    if(cp != s->unit.c_str()+s->unit.size())
        throw new ValueError(new str("invalid literal for int()"));
    return i;
}

double __float() { return 0; }
template<> double __float(int p) { return p; }
template<> double __float(bool b) { return __float((int)b); }
template<> double __float(double d) { return d; }
template<> double __float(str *s) {
    return atof((char *)(s->unit.c_str()));
}

int isinstance(pyobj *p, class_ *c) {
    int classnr = p->__class__->low;
    return ((classnr >= c->low) && (classnr <= c->high));
}

int isinstance(pyobj *p, tuple2<class_ *, class_ *> *t) {
    int classnr = p->__class__->low;
    for(int i = 0; i < t->__len__(); i++)
    {
       class_ *c = t->__getitem__(i);
       if ((classnr >= c->low) && (classnr <= c->high))
           return 1;
    }
    return 0;
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

list<int> *range(int a, int b, int s) {
    list<int> *r;
    int i, pos;

    r = new list<int>();
    pos = 0;
    i = a;

    if(s==0)
        throw new ValueError(new str("range() step argument must not be zero"));

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

list<int> *range(int n) {
    return range(0, n);
}

class __rangeiter : public __iter<int> {
public:
    int i, a, b, s;

    __rangeiter(int a, int b, int s) {
        this->__class__ = cl_rangeiter;

        this->a = a;
        this->b = b;
        this->s = s;
        i = a;
        if(s==0)
            throw new ValueError(new str("xrange() arg 3 must not be zero"));
    }

    int next() {
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

    int __len__() {
        return range_len(a,b,s);
    }
};

__iter<int> *xrange(int a, int b, int s) { return new __rangeiter(a,b,s); }
__iter<int> *xrange(int n) { return new __rangeiter(0, n, 1); }

__iter<int> *reversed(__rangeiter *x) {
   return new __rangeiter(x->a+(range_len(x->a,x->b,x->s)-1)*x->s, x->a-x->s, -x->s);
}

int ord(str *s) {
    return (unsigned char)(s->unit[0]);
}

str *chr(int i) {
    return __char_cache[i];
}

/* copy, deepcopy */

template<> int __deepcopy(int i, dict<void *, pyobj *> *) { return i; }
template<> double __deepcopy(double d, dict<void *, pyobj *> *) { return d; }
template<> void *__deepcopy(void *d, dict<void *, pyobj *> *) { return d; }

template<> int __copy(int i) { return i; }
template<> double __copy(double d) { return d; }
template<> void *__copy(void *d) { return d; }

/* representation */

template<> str *repr(double d) { return __str(d); }
template<> str *repr(int i) { return __str(i); }
template<> str *repr(bool b) { return __str((int)b); }
template<> str *repr(void *v) { return new str("None"); }

str *__str(void *v) { return new str("void"); }

/* equality, comparison, math operators */

template<> int __eq(int a, int b) { return a == b; }
template<> int __eq(double a, double b) { return a == b; }
template<> int __eq(void *a, void *b) { return a == b; }
template<> int __ne(int a, int b) { return a != b; }
template<> int __ne(double a, double b) { return a != b; }
template<> int __ne(void *a, void *b) { return a != b; }
template<> int __gt(int a, int b) { return a > b; }
template<> int __gt(double a, double b) { return a > b; }
template<> int __ge(int a, int b) { return a >= b; }
template<> int __ge(double a, double b) { return a >= b; }
template<> int __lt(int a, int b) { return a < b; }
template<> int __lt(double a, double b) { return a < b; }
template<> int __le(int a, int b) { return a <= b; }
template<> int __le(double a, double b) { return a <= b; }

template<> int __add(int a, int b) { return a + b; }
template<> double __add(double a, double b) { return a + b; }

/* get class pointer */

template<> class_ *__type(int i) { return cl_int_; }
template<> class_ *__type(double d) { return cl_float_; }

/* hashing */

template<> int hasher(int a) { return a; }
template<> int hasher(double v) {
    int hipart, expo; /* modified from CPython */
    v = frexp(v, &expo);
    v *= 32768.0; /* 2**15 */
    hipart = (int)v;   /* take the top 16 bits */
    v = (v - (double)hipart) * 32768.0; /* get the next 16 bits */
    return hipart + (int)v + (expo << 15);
}
template<> int hasher(void *a) { return (intptr_t)a; }

/* pow */

template<> double __power(double a, double b) { return pow(a,b); }
template<> double __power(int a, double b) { return pow(a,b); }
template<> double __power(double a, int b) { return pow(a,b); }

template<> int __power(int a, int b) {
    int res, tmp;

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

int __power2(int a) { return a*a; }
double __power2(double a) { return a*a; }
int __power3(int a) { return a*a*a; }
double __power3(double a) { return a*a*a; }

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
complex *__power(complex *a, int b) {
    return __power(a, new complex(b, 0));
}
complex *__power(complex *a, double b) {
    return __power(a, new complex(b, 0));
}

/* division */

template<> double __divs(double a, double b) { return a/b; }
template<> double __divs(int a, double b) { return (double)a/b; }
template<> double __divs(double a, int b) { return a/((double)b); }
template<> int __divs(int a, int b) { return (int)floor(((double)a)/b); }

template<> double __floordiv(double a, double b) { return floor(a/b); }
template<> double __floordiv(int a, double b) { return floor((double)a/b); }
template<> double __floordiv(double a, int b) { return floor(a/((double)b)); }
template<> int __floordiv(int a, int b) { return (int)floor((double)a/b); }

template<> tuple2<double, double> *divmod(double a, double b) {
    return new tuple2<double, double>(2, __floordiv(a,b), __mods(a,b));
}
template<> tuple2<double, double> *divmod(double a, int b) { return divmod(a, (double)b); } 
template<> tuple2<double, double> *divmod(int a, double b) { return divmod((double)a, b); }

tuple2<complex *, complex *> *divmod(complex *a, double b) { return a->__divmod__(b); }
tuple2<complex *, complex *> *divmod(complex *a, int b) { return a->__divmod__(b); }

template<> tuple2<int, int> *divmod(int a, int b) {
    return new tuple2<int, int>(2, __floordiv(a,b), __mods(a,b));
}

/* slicing */

void slicenr(int x, int &l, int&u, int&s, int len) {
    if((x&4) && (s == 0))
        throw new ValueError(new str("slice step cannot be zero"));

    if (!(x&4))
        s = 1;

    if (l<0)
        l = len+l;
    if (u<0)
        u = len+u;

    if (l<0)
        l = 0;
    if (u>=len)
        u = len;

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

/* cmp */

template<> int __cmp(int a, int b) { 
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
} 

template<> int __cmp(double a, double b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}
template<> int __cmp(void *a, void *b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}

str *__str(int i, int base) {
    if(i<10 && i>=0 && base==10)
        return __char_cache['0'+i];

    char asc[] = "0123456789abcdefghijklmnopqrstuvwxyz";
    char buf[12];
    char *psz = buf+11;
    if(i==INT_MIN)
        return new str("-2147483648");
    int neg = i<0;
    *psz = 0;
    if(neg) i = -i;
    do {
        unsigned lsd = i%base;
        i = i/base;
        *(--psz) = asc[lsd];
    }
    while(i != 0);
    if(neg) *(--psz) = '-';
    return new str(psz);
}

str *__str(bool b) {
    return __str((int)b);
}

template<> str *hex(int i) {
    return (new str("0x"))->__add__(__str(i, 16));
}
template<> str *hex(bool b) { return hex((int)b); }

template<> str *oct(int i) {
    if(i==0) return new str("0");
    return (new str("0"))->__add__(__str(i, 8));
}
template<> str *oct(bool b) { return oct((int)b); }

str *__str() { return new str(""); } /* XXX optimize */

template<> str *__str(double t) {
    std::stringstream ss;
    ss.precision(12);
    ss << std::showpoint << t;
    __GC_STRING s = ss.str().c_str();
    if( s.find('e') == -1)
    {
        int j = s.find_last_not_of("0");
        if( s[j] == '.') j++;
        s = s.substr(0, j+1);
    }

    return new str(s);
}

double ___round(double a) {
    return __portableround(a);
}
double ___round(double a, int n) {
    return __portableround(pow(10,n)*a)/pow(10,n);
}

/* bool */

int __bool() { return 0; }

template<> int __bool(int x) {
    return x;
}
template<> int __bool(bool x) {
    return (int)x;
}
template<> int __bool(double x) {
    return x!=0;
}

/* sum */

int __sum(pyseq<int> *l, int b) { return accumulate(l->units.begin(), l->units.end(), b); }
double __sum(pyseq<double> *l, double b) { return accumulate(l->units.begin(), l->units.end(), b); }

/* min, max */

int __min(pyseq<int> *l) { return __minimum(l); }
double __min(pyseq<double> *l) { return __minimum(l); }
int __max(pyseq<int> *l) { return __maximum(l); }
double __max(pyseq<double> *l) { return __maximum(l); }

#define __ss_max(a,b) ((a) > (b) ? (a) : (b))
#define __ss_max3(a,b,c) (__ss_max((a), __ss_max((b), (c))))

template<> int __max(int a, int b) { return __ss_max(a,b); }
template<> int __max(int a, int b, int c) { return __ss_max3(a,b,c); }
template<> double __max(double a, double b) { return __ss_max(a,b); }
template<> double __max(double a, double b, double c) { return __ss_max3(a,b,c); }

#define __ss_min(a,b) ((a) < (b) ? (a) : (b))
#define __ss_min3(a,b,c) (__ss_min((a), __ss_min((b), (c))))

template<> int __min(int a, int b) { return __ss_min(a,b); }
template<> int __min(int a, int b, int c) { return __ss_min3(a,b,c); }
template<> double __min(double a, double b) { return __ss_min(a,b); }
template<> double __min(double a, double b, double c) { return __ss_min3(a,b,c); }

/* abs */

template<> int __abs(int a) { return a<0?-a:a; }
template<> double __abs(double a) { return a<0?-a:a; }
int __abs(bool b) { return __abs((int)b); }

/* list */

list<str *> *__list(str *s) {
    list<str *> *r = new list<str *>();
    r->units.resize(len(s));
    int sz = s->unit.size();
    for(int i=0; i<sz; i++) 
        r->units[i] = __char_cache[s->unit[i]];
    return r;
}

/* sorted */

list<str *> *sorted(str *t, int (*cmp)(str *, str *), int key, int reverse) {
    list<str *> *l = __list(t);
    l->sort(cmp, key, reverse);
    return l;
}
list<str *> *sorted(str *t, int cmp, int key, int reverse) {
    return sorted(t, (int (*)(str *, str *))0, key, reverse);
}

/* mod helpers */

#if defined(WIN32) || defined(__sun)
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
    return fmt->unit.find_first_of(__fmtchars, i+1);
}

int __fmtpos2(str *fmt) {
    int i = 0;
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

void __fmtcheck(str *fmt, int l) {
    int i = 0, j = 0;
    while((j = fmt->unit.find('%', j)) != -1) {
        char c = fmt->unit[j+1];
        if(c != '%')
            i++;    
        j += 2;
    }

    if(i < l)
        throw new TypeError(new str("not all arguments converted during string formatting"));
    if(i > l)
        throw new TypeError(new str("not enough arguments for format string"));

}

void __modfill(str **fmt, pyobj *t, str **s) {
    char *d;
    char c;
    int i = (*fmt)->unit.find('%');
    int j = __fmtpos(*fmt);

    *s = new str((*s)->unit + (*fmt)->unit.substr(0, i));

    c = (*fmt)->unit[j];

    if(c == 's' or c == 'r') {
        str *add;
        if(c == 's') add = __str(t);
        else add = repr(t);

        if((*fmt)->unit[i+1] == '.') {
            int maxlen = __int(new str((*fmt)->unit.substr(i+2, j-i-2)));
            if(maxlen < len(add))
                add = new str(add->unit.substr(0, maxlen));
        }

        *s = new str((*s)->unit + add->unit);
    }
    else if(c  == 'c')
        *s = new str((*s)->unit + __str(t)->unit);
    else if(c == '%')
        *s = new str((*s)->unit + '%');
    else {
        if(c == 'h') {
            //(*fmt)->unit[j] = 'g'; 
            (*fmt)->unit.replace(j, 1, ".12g");
            j += 3;
        }
        if(t->__class__ == cl_int_)
            asprintf(&d, (*fmt)->unit.substr(i, j+1-i).c_str(), ((int_ *)t)->unit);
        else if(t->__class__== cl_float_)
            asprintf(&d, (*fmt)->unit.substr(i, j+1-i).c_str(), ((float_ *)t)->unit);
        else
            asprintf(&d, (*fmt)->unit.substr(i, j+1-i).c_str(), 0); /* XXX */

        *s = new str((*s)->unit + d);
        if(c == 'h' && t->__class__ == cl_float_ && ((float_ *)t)->unit-((int)(((float_ *)t)->unit)) == 0)
            (*s)->unit += ".0";   
        free(d); 
    }

    *fmt = new str((*fmt)->unit.substr(j+1, (*fmt)->unit.size()-j-1));
}

str *__mod4(str *fmts, list<pyobj *> *vals) {
    /* XXX fmtchecks */
    int i, j;
    str *r = new str();
    str *fmt = new str(fmts->unit);
    i = 0;
    while((j = __fmtpos(fmt)) != -1) {
        char c = fmt->unit[j];
        pyobj *p;
        if(c != '%')
            p = vals->__getitem__(i++);
        if(c == 'c') 
            __modfill(&fmt, mod_to_c2(p), &r);
        else if(c == 's' || c == 'r')
            __modfill(&fmt, p, &r);
        else if(c == '%')
            __modfill(&fmt, NULL, &r); /* XXX heh */
        else if(__GC_STRING("diouxX").find(c) != -1)
            __modfill(&fmt, mod_to_int(p), &r);
        else if(__GC_STRING("eEfFgGh").find(c) != -1)
            __modfill(&fmt, mod_to_float(p), &r);
        else
            break;
    }

    r->unit += fmt->unit;
    return r;
}

str *__mod5(list<pyobj *> *vals, int newline) {
    list<str *> *fmt = new list<str *>(); 
    for(int i=0;i<len(vals);i++) {
        pyobj *p = vals->__getitem__(i);
        if(p == NULL)
            fmt->append(new str("%s"));
        else if(p->__class__ == cl_float_)
            fmt->append(new str("%h"));
        else if(p->__class__== cl_int_)
            fmt->append(new str("%d"));
        else
            fmt->append(new str("%s"));
    }
    str *s = (new str(" "))->join(fmt);
    if(newline)
        s = s->__add__(new str("\n"));
    return __mod4(s, vals);
}

str *__modcd(str *fmt, list<str *> *names, ...) {
    int i, j;
    list<pyobj *> *vals = new list<pyobj *>();
    va_list args;
    va_start(args, names);
    for(i=0; i<len(names); i++)
        vals->append(va_arg(args, pyobj *));
    va_end(args);

    str *naam;
    int pos, pos2;
    dict<str *, pyobj *> *d;

    d = __dict(__zip2(names, vals));

    str *const_5 = new str("%("), *const_6 = new str(")");

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
    if(t->__class__ == cl_int_)
        return chr(((int_ *)t)->unit); 
    else if(t->__class__ == cl_float_)
        return chr(((float_ *)t)->unit); 
    else if(t->__class__ == cl_str_)
        return __str(t); 
    return new str("crap");
}

int_ *mod_to_int(pyobj *t) { 
    if(t->__class__ == cl_int_)
        return (int_ *)t;
    else if(t->__class__ == cl_float_)
        return new int_(((float_ *)t)->unit); 
    return new int_(0);
}

float_ *mod_to_float(pyobj *t) { 
    if(t->__class__ == cl_float_)
        return (float_ *)t;
    else if(t->__class__ == cl_int_)
        return new float_(((int_ *)t)->unit); 
    return new float_(0);
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

int_ *__box(int i) {
    return new int_(i);
}
int_ *__box(bool b) {
    return new int_(b);
}
float_ *__box(double d) {
    return new float_(d);
}

/* print .., */

char print_lastchar = '\n';
int print_space = 0;

void __exit() {
    if(print_lastchar != '\n')
        std::cout << '\n';
}

void print(int n, ...) { // XXX merge four functions 
     list<pyobj *> *vals = new list<pyobj *>();
     va_list args;
     va_start(args, n);
     for(int i=0; i<n; i++)
         vals->append(va_arg(args, pyobj *));
     va_end(args);
     str *s = __mod5(vals, 1);
     if(print_space && print_lastchar != '\n' && !(len(s) && s->unit[0] == '\n'))
         std::cout << " ";
     std::cout << s->unit;
     print_lastchar = s->unit[len(s)-1];
     print_space = 0;
}

void print(file *f, int n, ...) {
     list<pyobj *> *vals = new list<pyobj *>();
     va_list args;
     va_start(args, n);
     for(int i=0; i<n; i++)
         vals->append(va_arg(args, pyobj *));
     va_end(args);
     str *s = __mod5(vals, 1);
     if(f->print_space && f->print_lastchar != '\n' && !(len(s) && s->unit[0] == '\n'))
         f->putchar(' ');
     f->write(s);
     f->print_lastchar = s->unit[len(s)-1];
     f->print_space = 0;
}

void printc(int n, ...) {
     list<pyobj *> *vals = new list<pyobj *>();
     va_list args;
     va_start(args, n);
     for(int i=0; i<n; i++)
         vals->append(va_arg(args, pyobj *));
     va_end(args);
     str *s = __mod5(vals, 0);
     if(print_space && print_lastchar != '\n' && !(len(s) && s->unit[0] == '\n'))
         std::cout << " ";
     std::cout << s->unit;
     if(len(s)) print_lastchar = s->unit[len(s)-1];
     else print_lastchar = ' ';
     print_space = 1;
}

void printc(file *f, int n, ...) {
     list<pyobj *> *vals = new list<pyobj *>();
     va_list args;
     va_start(args, n);
     for(int i=0; i<n; i++)
         vals->append(va_arg(args, pyobj *));
     va_end(args);
     str *s = __mod5(vals, 0);
     if(f->print_space && f->print_lastchar != '\n' && !(len(s) && s->unit[0] == '\n'))
         f->putchar(' ');
     f->write(s);
     if(len(s)) f->print_lastchar = s->unit[len(s)-1];
     else f->print_lastchar = ' ';
     f->print_space = 1;
}

/* str, file iteration */

__seqiter<str *> *str::__iter__() {
    return new __striter(this);
}

__striter::__striter(str *p) {
    this->p = p;
    counter = 0;
}

str *__striter::next() {
   if(counter == p->unit.size())
       throw new StopIteration();
   return p->__getitem__(counter++); 
}

__iter<str *> *file::__iter__() {
    return new __fileiter(this);
}

__fileiter::__fileiter(file *p) {
    this->p = p;
}

str *__fileiter::next() {
    if(p->endoffile)
        throw new StopIteration();
    str *line = p->readline();
    if(p->endoffile && !len(line))
        throw new StopIteration();
    return line;
}

/* mod */

template<> double __mods(double a, double b) {
    double f = fmod(a,b);
    if((f<0 && b>0)||(f>0 && b<0)) f+=b;
    return f;
}
template<> double __mods(int a, double b) { return __mods((double)a, b); }
template<> double __mods(double a, int b) { return __mods(a, (double)b); }

template<> int __mods(int a, int b) {
    int m = a%b;
    if((m<0 && b>0)||(m>0 && b<0)) m+=b;
    return m;
}

/* binding */

#ifdef __SS_BIND
PyObject *__import(char *mod, char *method) {
    PyObject *m = PyImport_ImportModule(mod);
    PyObject *d = PyObject_GetAttrString(m, (char *)"__dict__");
    return PyDict_GetItemString(d, method);
}

PyObject *__call(PyObject *obj, PyObject *args) {
    return PyObject_CallObject(obj, args);
}

PyObject *__call(PyObject *obj, char *name, PyObject *args) {
    PyObject *method = PyObject_GetAttrString(obj, name);
    PyObject *x = PyObject_CallObject(method, args);
    return x;
}

PyObject *__args(int n, ...) {
    va_list ap;
    va_start(ap, n);

    PyObject *p = PyTuple_New(n);

    for(int i=0; i<n; i++) {
        PyObject *t = va_arg(ap, PyObject *);
        PyTuple_SetItem(p, i, t);
    }
    va_end(ap);
    return p;
}

template<> PyObject *__to_py(int i) { return PyInt_FromLong(i); }   
template<> PyObject *__to_py(double d) { return PyFloat_FromDouble(d); }
template<> PyObject *__to_py(void *v) { return Py_None; }

template<> int __to_ss(PyObject *p) { 
    if(!PyInt_Check(p)) 
        throw new TypeError(new str("error in conversion to Shed Skin (integer expected)"));
    return PyInt_AsLong(p);
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

// Exceptions
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

template <> void *myallocate<int>(int n) { return GC_MALLOC_ATOMIC(n); }

} // namespace __shedskin__

