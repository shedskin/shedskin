/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

/* input */

str *input(str *msg) {
    if(msg and len(msg)) {
        __ss_stdout->write(msg);
        __ss_stdout->options.lastchar = msg->unit[msg->unit.size()-1];
    }
    str *s = __ss_stdin->readline();
    if(s->unit.size() and s->unit[s->unit.size()-1] == '\n')
        s->unit.erase(s->unit.end()-1, s->unit.end());
    if(__ss_stdin->__eof())
        throw new EOFError();
    return s;
}

/* int */

template<class T> static str *__int_error(T s, __ss_int base) {
    return __add_strs(4, new str("invalid literal for int() with base "), __str(base), new str(": "), repr(s));
}

template<class T> static __ss_int __int_parse(const char *start, T orig, __ss_int base) {
    char *cp;
    __ss_int i;
#ifdef __SS_LONG
    i = (__ss_int)strtoll(start, &cp, (int)base);
#else
    i = (__ss_int)strtol(start, &cp, (int)base);
#endif
    /* no digits at all: strtol happily returns 0 for '' or '   ' */
    if(cp == start)
        throw new ValueError(__int_error(orig, base));
    while(*cp and isspace((unsigned char)*cp))
        cp++;
    if(*cp != '\0')
        throw new ValueError(__int_error(orig, base));
    return i;
}

__ss_int __int(str *s, __ss_int base) {
    /* unicode digits and whitespace -> ascii (see __ss_ascii_numeric) */
    __GC_STRING a = __ss_ascii_numeric(s);
    return __int_parse(a.c_str(), s, base);
}

__ss_int __int(bytes *s, __ss_int base) {
    return __int_parse(s->c_str(), s, base);
}

/* float */

/* strtod is much more permissive than CPython's float(): it stops at the
 * first character it cannot use (so 'inf', '1.5x' and '' all convert
 * happily) and it also accepts hexadecimal literals such as '0x10'. so
 * scan the string ourselves first, copying out a strtod-digestible version
 * along the way (underscores between digits are dropped, as in CPython). */

static bool __float_word(const char *p, const char *word) {
    while(*word) {
        if(tolower((unsigned char)*p) != *word)
            return false;
        p++;
        word++;
    }
    return true;
}

/* one run of decimal digits, with underscores allowed between digits */
static bool __float_scan_digits(const char *&p, __GC_STRING &clean) {
    bool any = false;
    while(true) {
        if(*p >= '0' and *p <= '9') {
            clean += *p++;
            any = true;
        } else if(*p == '_' and any and p[1] >= '0' and p[1] <= '9') {
            p++;
        } else
            break;
    }
    return any;
}

static bool __float_scan(const char *p, __GC_STRING &clean) {
    while(*p and isspace((unsigned char)*p))
        p++;

    if(*p == '+' or *p == '-')
        clean += *p++;

    if(__float_word(p, "infinity")) {
        clean += "inf";
        p += 8;
    } else if(__float_word(p, "inf")) {
        clean += "inf";
        p += 3;
    } else if(__float_word(p, "nan")) {
        clean += "nan";
        p += 3;
    } else {
        bool digits = __float_scan_digits(p, clean);
        if(*p == '.') {
            clean += *p++;
            if(__float_scan_digits(p, clean))
                digits = true;
        }
        if(not digits)
            return false;
        if(*p == 'e' or *p == 'E') {
            clean += 'e';
            p++;
            if(*p == '+' or *p == '-')
                clean += *p++;
            if(not __float_scan_digits(p, clean))
                return false;
        }
    }

    while(*p and isspace((unsigned char)*p))
        p++;

    return *p == '\0';
}

template<> __ss_float __float(str *s) {
    __GC_STRING clean;
    __GC_STRING a = __ss_ascii_numeric(s); /* unicode digits/whitespace */
    if(not __float_scan(a.c_str(), clean))
        throw new ValueError(__add_strs(0, new str("could not convert string to float: "), repr(s)));
    __ss_float d = strtod(clean.c_str(), NULL);
    if(std::isnan(d))
        d = NAN; // avoid "-nan" (test 194)
    return d;
}

/* id */

template<> __ss_int id(__ss_int) { throw new TypeError(new str("'id' called with integer")); }
template<> __ss_int id(__ss_float) { throw new TypeError(new str("'id' called with float")); }
template<> __ss_int id(__ss_bool) { throw new TypeError(new str("'id' called with bool")); }

/* range */

__ss_int range_len(__ss_int lo, __ss_int hi, __ss_int step) {
    /* modified from CPython. The intermediate difference is computed in
     * __ss_uint because hi-lo can exceed the signed range even when the
     * resulting length does not. */
    __ss_int n = 0;
    if ((lo < hi) && (step>0)) {
        __ss_uint uhi = (__ss_uint)hi;
        __ss_uint ulo = (__ss_uint)lo;
        __ss_uint diff = uhi - ulo - 1;
        n = (__ss_int)(diff / (__ss_uint)step + 1);
    }
    else {
        if ((lo > hi) && (step<0)) {
            __ss_uint uhi = (__ss_uint)lo;
            __ss_uint ulo = (__ss_uint)hi;
            __ss_uint diff = uhi - ulo - 1;
            n = (__ss_int)(diff / __ss_magnitude(step) + 1);
        }
    }
    return n;
}

class __rangeiter : public __iter<__ss_int> {
public:
    __ss_int i, a, b, s;

    __rangeiter(__ss_int a_, __ss_int b_, __ss_int s_) {
        this->__class__ = cl_rangeiter;

        a = a_;
        b = b_;
        s = s_;
        i = a;
    }

    __ss_int __next__() {
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

__xrange::__xrange(__ss_int a_, __ss_int b_, __ss_int s_) {
    if(s_==0)
        throw new ValueError(new str("range() arg 3 must not be zero"));

    this->a = this->start = a_;
    this->b = this->stop = b_;
    this->s = this->step = s_;
}

__ss_int __xrange::count(__ss_int value) {
    if(s > 0 ? (value < a || value >= b) : (value > a || value <= b))
        return 0;
    if((value - a) % s == 0)
        return 1;
    return 0;
}

__ss_int __xrange::index(__ss_int value) {
    if(s > 0 ? (value < a || value >= b) : (value > a || value <= b))
        throw new ValueError(new str("value not in range"));
    if((value - a) % s != 0)
        throw new ValueError(new str("value not in range"));
    return (value - a) / s;
}

__iter<__ss_int> *__xrange::__iter__() {
    return new __rangeiter(a, b, s);
}

__ss_int __xrange::__len__() {
    return range_len(a, b, s);
}

__ss_int __xrange::__getitem__(__ss_int i) {
    return a + (__wrap(this, i)) * s;
}

__ss_bool __xrange::__contains__(__ss_int i) {
    return __ss_in_range(i, a, b, s);
}

str *__xrange::__repr__() {
    if(s==1) {
        if(a==0)
            return __mod6(new str("range(%d)"), 1, b);
        else
            return __mod6(new str("range(%d, %d)"), 2, a, b);
    }
    return __mod6(new str("range(%d, %d, %d)"), 3, a, b, s); /* XXX */
}

__xrange *__xrange::__slice__(__ss_int x, __ss_int start, __ss_int stop, __ss_int step) {
    __ss_int lower, upper;
    __ss_int rangelen = this->__len__();

    /* lower, upper bounds */
    if(!(x&4)) {
        step = 1;
    }

    if(step < 0) {
        lower = -1;
        upper = lower + rangelen;
    } else {
        lower = 0;
        upper = rangelen;
    }

    /* start */
    if (!(x&1)) {
        start = step < 0 ? upper : lower;
    } else if (start < 0) {
        start += rangelen;
        if(start < lower) {
            start = lower;
        }
    } else if (start > upper) {
        start = upper;
    }

    /* end */
    if (!(x&2)) {
        stop = step < 0 ? lower : upper;
    } else if (stop < 0) {
        stop += rangelen;
        if(stop < lower) {
            stop = lower;
        }
    } else if (stop > upper) {
        stop = upper;
    }

    /* return sliced range object */
    start = a+start*s;
    stop = a+stop*s;
    step = step*s;

    return new __xrange(start, stop, step);
}

__xrange *range(__ss_int a, __ss_int b, __ss_int s) { return new __xrange(a,b,s); }
__xrange *range(__ss_int n) { return new __xrange(0, n, 1); }

__iter<__ss_int> *reversed(__xrange *x) {
   return new __rangeiter(x->a+(range_len(x->a,x->b,x->s)-1)*x->s, x->a-x->s, -x->s);
}

/* ascii */

str *__ascii(str *s) {
    static const char *hexdigits = "0123456789abcdef";
    const __GC_STR &u = s->unit;
    size_t i = 0, n = u.size();
    while (i < n && (uint32_t)u[i] < 0x80)
        i++;
    if (i == n)
        return s; /* common case: already pure ASCII */
    __GC_STR r(u, 0, i);
    for (; i < n; i++) {
        uint32_t c = (uint32_t)u[i];
        if (c < 0x80) {
            r += u[i];
            continue;
        }
        int digits;
        r += (__ss_char)'\\';
        if (c < 0x100) {
            r += (__ss_char)'x';
            digits = 2;
        } else if (c < 0x10000) {
            r += (__ss_char)'u';
            digits = 4;
        } else {
            r += (__ss_char)'U';
            digits = 8;
        }
        for (int d = digits - 1; d >= 0; d--)
            r += (__ss_char)hexdigits[(c >> (4 * d)) & 0xf];
    }
    return new str(r);
}

/* repr */

template<> str *repr(__ss_float d) { return __str(d); }
#ifdef __SS_LONG
template<> str *repr(__ss_int i) { return __str(i); }
#endif
template<> str *repr(int i) { return __str(i); }
template<> str *repr(__ss_bool b) { return b.value?(new str("True")):(new str("False")); }
template<> str *repr(void *) { return new str("None"); }
template<> str *repr(long unsigned int) { return new str("?"); } /* ? */
#ifdef WIN32
template<> str *repr(size_t i) { return repr((__ss_int)i); }
#endif

/* str */

str *__str(void *) { return new str("None"); }
str *__str(bytes *b, str *encoding, str *errors) { return b->decode(encoding, errors); }

/* isinstance */

__ss_bool isinstance(pyobj *p, class_ *cl) {
    return __mbool(p->__class__ == cl);
}

/* get class pointer */

template<> class_ *__type(int) { return cl_int_; }
#ifdef __SS_LONG
template<> class_ *__type(__ss_int) { return cl_int_; }
#endif
template<> class_ *__type(__ss_float) { return cl_float_; }
