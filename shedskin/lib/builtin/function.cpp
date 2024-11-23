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

__ss_int __int(str *s, __ss_int base) {
    char *cp;
    __ss_int i;
#ifdef __SS_LONG
    i = (__ss_int)strtoll(s->c_str(), &cp, base);
#else
    i = (__ss_int)strtol(s->c_str(), &cp, base);
#endif
    if(*cp != '\0') {
        s = s->rstrip();
        #ifdef __SS_LONG
            i = (__ss_int)strtoll(s->c_str(), &cp, base);
        #else
            i = (__ss_int)strtol(s->c_str(), &cp, base);
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
    i = (__ss_int)strtoll(s->c_str(), &cp, base);
#else
    i = (__ss_int)strtol(s->c_str(), &cp, base);
#endif
    if(*cp != '\0') {
        s = s->rstrip();
        #ifdef __SS_LONG
            i = (__ss_int)strtoll(s->c_str(), &cp, base);
        #else
            i = (__ss_int)strtol(s->c_str(), &cp, base);
        #endif
        if(*cp != '\0')
            throw new ValueError(new str("invalid literal for int()"));
    }
    return i;
}

/* float */

template<> __ss_float __float(str *s) {
    __ss_float d = strtod(s->c_str(), NULL);
    if(std::isnan(d))
        d = NAN; // avoid "-nan" (test 194)
    return d;
}

/* id */

template<> __ss_int id(__ss_int) { throw new TypeError(new str("'id' called with integer")); }
template<> __ss_int id(__ss_float) { throw new TypeError(new str("'id' called with float")); }
template<> __ss_int id(__ss_bool) { throw new TypeError(new str("'id' called with bool")); }

/* range */

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
    if(value < a || value >= b)
        return 0;
    if((value - a) % s == 0)
        return 1;
    return 0;
}

__ss_int __xrange::index(__ss_int value) {
    if(value < a || value >= b)
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
    if(s > 0 and (i < a or i >= b))
        return False;
    else if(s < 0 and (i > a or i <= b))
        return False;
    else if((i-a)%s != 0)
        return False;

    return True;
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

/* isinstance */

__ss_bool isinstance(pyobj *p, class_ *cl) {
    return __mbool(p->__class__ == cl);
}

/* get class pointer */

template<> class_ *__type(int) { return cl_int_; }
template<> class_ *__type(__ss_float) { return cl_float_; }
