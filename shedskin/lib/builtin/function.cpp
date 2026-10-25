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

__ss_int __int_float_checked(__ss_float d) { /* slow path of __int(__ss_float) */
    if(std::isnan(d))
        throw new ValueError(new str("cannot convert float NaN to integer"));
    if(!std::isfinite(d))
        throw new OverflowError(new str("cannot convert float infinity to integer"));
    /* out-of-range float-to-int conversion is undefined behaviour (in
       practice INT64_MIN); the limit is a power of two, so exact as a float */
    const __ss_float limit = std::ldexp((__ss_float)1, (int)(8*sizeof(__ss_int)-1));
    __ss_float t = std::trunc(d);
    if(t < -limit || t >= limit)
        throw new OverflowError(new str("float too large to convert to integer"));
    return (__ss_int)t;
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

/* a float without surrounding whitespace; on success, advance p past it
 * and append a strtod-digestible version to clean (also used by complex) */
bool __float_scan_number(const char *&p, __GC_STRING &clean) {
    const char *q = p;
    __GC_STRING c;

    if(*q == '+' or *q == '-')
        c += *q++;

    if(__float_word(q, "infinity")) {
        c += "inf";
        q += 8;
    } else if(__float_word(q, "inf")) {
        c += "inf";
        q += 3;
    } else if(__float_word(q, "nan")) {
        c += "nan";
        q += 3;
    } else {
        bool digits = __float_scan_digits(q, c);
        if(*q == '.') {
            c += *q++;
            if(__float_scan_digits(q, c))
                digits = true;
        }
        if(not digits)
            return false;
        if(*q == 'e' or *q == 'E') {
            c += 'e';
            q++;
            if(*q == '+' or *q == '-')
                c += *q++;
            if(not __float_scan_digits(q, c))
                return false;
        }
    }

    p = q;
    clean += c;
    return true;
}

static bool __float_scan(const char *p, __GC_STRING &clean) {
    while(*p and isspace((unsigned char)*p))
        p++;

    if(not __float_scan_number(p, clean))
        return false;

    while(*p and isspace((unsigned char)*p))
        p++;

    return *p == '\0';
}

static __ss_float __float_parse(const char *p, pyobj *s) {
    __GC_STRING clean;
    if(not __float_scan(p, clean))
        throw new ValueError(__add_strs(0, new str("could not convert string to float: "), s->__repr__()));
    __ss_float d = strtod(clean.c_str(), NULL);
    if(std::isnan(d))
        d = NAN; // avoid "-nan" (test 194)
    return d;
}

template<> __ss_float __float(str *s) {
    __GC_STRING a = __ss_ascii_numeric(s); /* unicode digits/whitespace */
    return __float_parse(a.c_str(), s);
}

template<> __ss_float __float(bytes *s) {
    /* only ascii digits/whitespace; nul and non-ascii bytes are rejected */
    __GC_STRING a;
    a.reserve(s->unit.size());
    for(unsigned char c : s->unit)
        a += (c == 0 || c >= 0x80) ? '?' : (char)c;
    return __float_parse(a.c_str(), s);
}

/* zip, map: CPython's message for strict=True, for example 'zip() argument 2
   is shorter than argument 1' or 'map() argument 3 is longer than arguments 1-2' */

ValueError *__strict_length_error(const char *name, size_t i, bool shorter) {
    std::string msg = std::string(name) + "() argument " + std::to_string(i + 1) +
        (shorter ? " is shorter than argument" : " is longer than argument") +
        (i == 1 ? " 1" : "s 1-" + std::to_string(i));
    return new ValueError(new str(msg.c_str()));
}

/* id */

template<> __ss_int id(__ss_int) { throw new TypeError(new str("'id' called with integer")); }
template<> __ss_int id(__ss_float) { throw new TypeError(new str("'id' called with float")); }
template<> __ss_int id(__ss_bool) { throw new TypeError(new str("'id' called with bool")); }

/* range */

__ss_uint range_ulen(__ss_int lo, __ss_int hi, __ss_int step) {
    /* modified from CPython. this is computed in __ss_uint because hi-lo,
     * and the length itself, can exceed the signed range */
    if ((lo < hi) && (step>0))
        return ((__ss_uint)hi - (__ss_uint)lo - 1) / (__ss_uint)step + 1;
    if ((lo > hi) && (step<0))
        return ((__ss_uint)lo - (__ss_uint)hi - 1) / __ss_magnitude(step) + 1;
    return 0;
}

static void __throw_range_overflow() {
    throw new OverflowError(new str("Python int too large to convert to C ssize_t"));
}

__ss_int range_len(__ss_int lo, __ss_int hi, __ss_int step) {
    __ss_uint n = range_ulen(lo, hi, step);
    if(n > (__ss_uint)std::numeric_limits<__ss_int>::max()) /* as in CPython */
        __throw_range_overflow();
    return (__ss_int)n;
}

/* the i-th value of range(a, .., s), for 0 <= i < length. this is computed
   in __ss_uint, where wrapping is defined and gives the right value */
static inline __ss_int __range_value(__ss_int a, __ss_uint i, __ss_int s) {
    return (__ss_int)((__ss_uint)a + i * (__ss_uint)s);
}

/* out = a + k*s, unless that does not fit in __ss_int */
static bool __range_point(__ss_int a, __ss_int k, __ss_int s, __ss_int &out) {
    __ss_uint mk = __ss_magnitude(k), ms = __ss_magnitude(s);
    if(mk != 0 && ms > std::numeric_limits<__ss_uint>::max() / mk)
        return false;
    __ss_uint p = mk * ms;
    if((k < 0) != (s < 0)) {
        if(p > (__ss_uint)a - (__ss_uint)std::numeric_limits<__ss_int>::min())
            return false;
        out = (__ss_int)((__ss_uint)a - p);
    } else {
        if(p > (__ss_uint)std::numeric_limits<__ss_int>::max() - (__ss_uint)a)
            return false;
        out = (__ss_int)((__ss_uint)a + p);
    }
    return true;
}

class __rangeiter : public __iter<__ss_int> {
public:
    __ss_int i, s;
    __ss_uint n; /* values left: can exceed the signed range */

    __rangeiter(__ss_int start, __ss_int step, __ss_uint count) {
        this->__class__ = cl_rangeiter;

        i = start;
        s = step;
        n = count;
    }

    __ss_int __next__() {
        if(n == 0)
            throw new StopIteration();
        n--;
        __ss_int r = i;
        i = __range_value(i, 1, s); /* may wrap after the last value */
        return r;
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
    return __ss_in_range(value, a, b, s) ? 1 : 0;
}

__ss_int __xrange::index(__ss_int value) {
    if(!__ss_in_range(value, a, b, s))
        throw new ValueError(new str("value not in range"));
    __ss_uint n = __ss_magnitude_diff(value, a) / __ss_magnitude(s);
    if(n > (__ss_uint)std::numeric_limits<__ss_int>::max())
        __throw_range_overflow();
    return (__ss_int)n;
}

__iter<__ss_int> *__xrange::__iter__() {
    return new __rangeiter(a, s, range_ulen(a, b, s));
}

__ss_int __xrange::__len__() {
    return range_len(a, b, s);
}

__ss_int __xrange::__getitem__(__ss_int i) {
    /* not __wrap: the length may not fit in __ss_int */
    __ss_uint n = range_ulen(a, b, s);
    __ss_uint j = (i < 0) ? n - __ss_magnitude(i) : (__ss_uint)i;
    if(i < 0 ? __ss_magnitude(i) > n : j >= n)
        __throw_index_out_of_range("range object index out of range");
    return __range_value(a, j, s);
}

__ss_bool __xrange::__contains__(__ss_int i) {
    return __ss_in_range(i, a, b, s);
}

/* as in CPython, ranges are equal when they produce the same sequence: so only
   the length counts for empty ranges, and the step only past a single element */
__ss_bool __xrange::__eq__(pyobj *p) {
    __xrange *r = (__xrange *)p;
    __ss_uint n = range_ulen(a, b, s);
    if(n != range_ulen(r->a, r->b, r->s))
        return False;
    if(n == 0)
        return True;
    if(a != r->a)
        return False;
    if(n == 1)
        return True;
    return __mbool(s == r->s);
}

__ss_int __xrange::__hash__() {
    __ss_uint n = range_ulen(a, b, s);
    __ss_int seed = hash_combine(0, (__ss_int)n);
    if(n > 0)
        seed = hash_combine(seed, a);
    if(n > 1)
        seed = hash_combine(seed, s);
    return seed;
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

    /* return sliced range object. as in CPython if it can be represented,
       else stop just past the last value (e.g. range(0, 2**63-1, 2)[-2:]) */
    __ss_int first, last, nstop, nstep;
    __ss_uint n = range_ulen(start, stop, step);
    if(__range_point(a, start, s, first) && __range_point(a, stop, s, nstop) && __range_point(0, step, s, nstep))
        return new __xrange(first, nstop, nstep);
    if(n == 0)
        return new __xrange(a, a, s);
    first = __range_value(a, (__ss_uint)start, s);
    last = __range_value(a, (__ss_uint)(start + (__ss_int)(n-1) * step), s);
    if(n == 1)
        nstep = (step > 0) == (s > 0) ? 1 : -1;
    else if(!__range_point(0, step, s, nstep))
        __throw_range_overflow();
    if(!__range_point(last, 1, nstep > 0 ? 1 : -1, nstop))
        __throw_range_overflow();
    return new __xrange(first, nstop, nstep);
}

__xrange *range(__ss_int a, __ss_int b, __ss_int s) { return new __xrange(a,b,s); }
__xrange *range(__ss_int n) { return new __xrange(0, n, 1); }

__iter<__ss_int> *reversed(__xrange *x) {
   __ss_uint n = range_ulen(x->a, x->b, x->s);
   if(n == 0)
       return new __rangeiter(x->a, x->s, 0);
   /* -s wraps for s == -2**63, but adding it in __range_value is still right */
   return new __rangeiter(__range_value(x->a, n-1, x->s), (__ss_int)((__ss_uint)0 - (__ss_uint)x->s), n);
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
