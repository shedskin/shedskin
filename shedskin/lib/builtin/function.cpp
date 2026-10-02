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

/* int() from a string, following CPython's PyLong_FromString: optional
 * sign, base prefix (0x/0o/0b, also with base 16/8/2), single underscores
 * between digits (or right after a prefix), no leading zeros in a non-zero
 * base 0 literal, and an OverflowError instead of silently clamping when
 * the value does not fit in __ss_int. code units are scanned in place, so
 * nothing is allocated unless an exception is thrown. */

/* code unit -> ascii; 0 means 'not valid anywhere in an int literal'.
 * for str, non-ascii whitespace becomes ' ' and non-ascii decimal digits
 * become ascii ones, as in _PyUnicode_TransformDecimalAndSpaceToASCII */
static inline unsigned __int_unit(char c) {
    unsigned char u = (unsigned char)c;
    return u < 0x80 ? u : 0;
}

static inline unsigned __int_unit(__ss_char c) {
    if(c < 0x80)
        return c;
    if(__ss_char_space(c))
        return ' ';
    int d = __ss_char_rec(c)->decimal;
    return d >= 0 ? '0' + (unsigned)d : 0;
}

static inline bool __int_space(unsigned c) {
    return c == ' ' or (c >= '\t' and c <= '\r');
}

/* ascii -> digit value, 99 if not a digit in any base */
struct __int_digit_table {
    unsigned char v[128];
    constexpr __int_digit_table() : v() {
        for(int i = 0; i < 128; i++)
            v[i] = 99;
        for(int i = 0; i < 10; i++)
            v['0' + i] = (unsigned char)i;
        for(int i = 0; i < 26; i++)
            v['a' + i] = v['A' + i] = (unsigned char)(10 + i);
    }
};
static constexpr __int_digit_table __int_digits;

template<class U, class T> static __ss_int __int_parse(const U *p, const U *end, T orig, __ss_int base) {
    if(base != 0 and (base < 2 or base > 36))
        throw new ValueError(new str("int() base must be >= 2 and <= 36, or 0"));
    __ss_int orig_base = base;

    while(p < end and __int_space(__int_unit(*p)))
        p++;

    bool neg = false;
    if(p < end) {
        unsigned c = __int_unit(*p);
        if(c == '-' or c == '+') {
            neg = (c == '-');
            p++;
        }
    }

    /* base prefix */
    bool after_prefix = false; /* an underscore may directly follow it */
    bool zero_rule = false; /* base 0 literal starting with '0' */
    if(p < end and __int_unit(*p) == '0') {
        unsigned c = (p+1 < end) ? (__int_unit(p[1]) | 0x20) : 0;
        if(c == 'x' and (base == 0 or base == 16))
            base = 16;
        else if(c == 'o' and (base == 0 or base == 8))
            base = 8;
        else if(c == 'b' and (base == 0 or base == 2))
            base = 2;
        else
            c = 0;
        if(c) {
            p += 2;
            after_prefix = true;
        } else if(base == 0) {
            base = 10;
            zero_rule = true;
        }
    } else if(base == 0)
        base = 10;

    /* digits: accumulate the magnitude unsigned, detecting overflow as strtol does */
    unsigned ubase = (unsigned)base;
    __ss_uint limit = ((__ss_uint)-1 >> 1) + (neg ? 1 : 0); /* max, or -min */
    __ss_uint cutoff = limit / ubase;
    unsigned cutlim = (unsigned)(limit % ubase);
    __ss_uint acc = 0;
    bool any = false, overflow = false;

    for(; p < end; p++) {
        unsigned c = __int_unit(*p);
        if(c == '_') {
            if(not (any or after_prefix) or p+1 == end)
                throw new ValueError(__int_error(orig, orig_base));
            c = __int_unit(*++p);
            if(__int_digits.v[c] >= ubase)
                throw new ValueError(__int_error(orig, orig_base));
        }
        unsigned d = __int_digits.v[c];
        if(d >= ubase)
            break;
        if(acc > cutoff or (acc == cutoff and d > cutlim))
            overflow = true;
        else
            acc = acc * ubase + d;
        any = true;
    }

    if(not any)
        throw new ValueError(__int_error(orig, orig_base));
    while(p < end and __int_space(__int_unit(*p)))
        p++;
    if(p != end or (zero_rule and (acc != 0 or overflow)))
        throw new ValueError(__int_error(orig, orig_base));
    if(overflow)
        throw new OverflowError(__add_strs(2, new str("int too large to convert: "), repr(orig)));

    return neg ? (__ss_int)(0 - acc) : (__ss_int)acc;
}

__ss_int __int(str *s, __ss_int base) {
    const __ss_char *p = s->unit.data();
    return __int_parse(p, p + s->unit.size(), s, base);
}

__ss_int __int(bytes *s, __ss_int base) {
    const char *p = s->unit.data();
    return __int_parse(p, p + s->unit.size(), s, base);
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
