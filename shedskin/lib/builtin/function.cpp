/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* builtin functions */

str *input(str *msg) {
    if(msg and len(msg)) {
        __ss_stdout->write(msg);
        __ss_stdout->options.lastchar = msg->unit[len(msg)-1];
    }
    str *s = __ss_stdin->readline();
    if(len(s) and s->unit[len(s)-1] == '\n')
        s->unit.erase(s->unit.end()-1, s->unit.end());
    if(__ss_stdin->__eof())
        throw new EOFError();
    return s;
}

__ss_int __int(str *s, __ss_int base) {
    char *cp;
    __ss_int i;
#ifdef __SS_LONG
    i = strtoll(s->c_str(), &cp, base);
#else
    i = strtol(s->c_str(), &cp, base);
#endif
    if(*cp != '\0') {
        s = s->rstrip();
        #ifdef __SS_LONG
            i = strtoll(s->c_str(), &cp, base);
        #else
            i = strtol(s->c_str(), &cp, base);
        #endif
        if(*cp != '\0')
            throw new ValueError(new str("invalid literal for int()"));
    }
    return i;
}

__ss_int __int(bytes *s, __ss_int base) {
    char *cp;
    __ss_int i;
#ifdef __SS_LONG
    i = strtoll(s->c_str(), &cp, base);
#else
    i = strtol(s->c_str(), &cp, base);
#endif
    if(*cp != '\0') {
        s = s->rstrip();
        #ifdef __SS_LONG
            i = strtoll(s->c_str(), &cp, base);
        #else
            i = strtol(s->c_str(), &cp, base);
        #endif
        if(*cp != '\0')
            throw new ValueError(new str("invalid literal for int()"));
    }
    return i;
}

template<> __ss_float __float(str *s) {
    __ss_float d = strtod(s->c_str(), NULL);
    if(std::isnan(d))
        d = NAN; // avoid "-nan" (test 194)
    return d;
}

template<> __ss_int id(__ss_int) { throw new TypeError(new str("'id' called with integer")); }
template<> __ss_int id(__ss_float) { throw new TypeError(new str("'id' called with float")); }
template<> __ss_int id(__ss_bool) { throw new TypeError(new str("'id' called with bool")); }

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

__ss_int __xrange::__getitem__(__ss_int i) {
   return a + (__wrap(this, i)) * s;
}

str *__xrange::__repr__() {
    if(s==1) {
        if(a==0)
            return __modct(new str("range(%d)"), 1, ___box(b));
        else
            return __modct(new str("range(%d, %d)"), 2, ___box(a), ___box(b));
    }
    return __modct(new str("range(%d, %d, %d)"), 3, ___box(a), ___box(b), ___box(s)); /* XXX */
}

__xrange *range(__ss_int a, __ss_int b, __ss_int s) { return new __xrange(a,b,s); }
__xrange *range(__ss_int n) { return new __xrange(0, n, 1); }

__iter<__ss_int> *reversed(__xrange *x) {
   return new __rangeiter(x->a+(range_len(x->a,x->b,x->s)-1)*x->s, x->a-x->s, -x->s);
}

/* representation */

template<> str *repr(__ss_float d) { return __str(d); }
#ifdef __SS_LONG
template<> str *repr(__ss_int i) { return __str(i); }
#endif
template<> str *repr(int i) { return __str(i); }
template<> str *repr(__ss_bool b) { return b.value?(new str("True")):(new str("False")); }
template<> str *repr(void *) { return new str("None"); }

str *__str(void *) { return new str("void"); }

/* get class pointer */

template<> class_ *__type(int) { return cl_int_; }
template<> class_ *__type(__ss_float) { return cl_float_; }

/* hex, oct, bin */

template<> str *hex(int i) {
    if(i<0)
        return (new str("-0x"))->__add__(__str(-i, 16));
    else
        return (new str("0x"))->__add__(__str(i, 16));
}
template<> str *hex(__ss_bool b) { return hex((int)b.value); }

template<> str *oct(int i) {
    if(i<0)
        return (new str("-0o"))->__add__(__str(-i, 8));
    else if(i>0)
        return (new str("0o"))->__add__(__str(i, 8));
    else
      return new str("0o0");
}
template<> str *oct(__ss_bool b) { return oct((int)b.value); }

template<> str *bin(int i) {
    if(i<0)
        return (new str("-0b"))->__add__(__str(-i, 2));
    else
        return (new str("0b"))->__add__(__str(i, 2));
}
template<> str *bin(__ss_bool b) { return bin((int)b.value); }
