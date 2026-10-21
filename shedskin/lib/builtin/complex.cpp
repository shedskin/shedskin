/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* complex methods */

static bool __complex_scan_float(const char *&p, __ss_float &d) {
    __GC_STRING clean;
    if(not __float_scan_number(p, clean))
        return false;
    d = strtod(clean.c_str(), NULL);
    if(std::isnan(d))
        d = NAN; // avoid "-nan"
    return true;
}

/* follows CPython's complex_from_string_inner */
complex mcomplex(str *s) {
    __GC_STRING a = __ss_ascii_numeric(s); /* unicode digits/whitespace */
    const char *p = a.c_str();
    __ss_float real = 0, imag = 0, z;
    bool bracket = false;

    while(isspace((unsigned char)*p))
        p++;
    if(*p == '(') {
        bracket = true;
        p++;
        while(isspace((unsigned char)*p))
            p++;
    }

    if(__complex_scan_float(p, z)) {
        if(*p == '+' or *p == '-') { /* <float><signed-float>j | <float><sign>j */
            real = z;
            if(not __complex_scan_float(p, imag))
                imag = (*p++ == '+') ? 1.0 : -1.0;
            if(*p != 'j' and *p != 'J')
                goto error;
            p++;
        } else if(*p == 'j' or *p == 'J') { /* <float>j */
            imag = z;
            p++;
        } else /* <float> */
            real = z;
    } else { /* <sign>j | j */
        if(*p == '+' or *p == '-')
            imag = (*p++ == '+') ? 1.0 : -1.0;
        else
            imag = 1.0;
        if(*p != 'j' and *p != 'J')
            goto error;
        p++;
    }

    while(isspace((unsigned char)*p))
        p++;
    if(bracket) {
        if(*p != ')')
            goto error;
        p++;
        while(isspace((unsigned char)*p))
            p++;
    }

    if(*p == '\0')
        return mcomplex(real, imag);
error:
    throw new ValueError(new str("complex() arg is a malformed string"));
}


complex complex::parsevalue(str *s) {
    complex mult;

    if ((!___bool(s))) {
        return mcomplex(0.0, 0.0);
    }
    mult = mcomplex(1.0, 0.0);
    if (__eq(s->__getitem__((-1)), new str("j"))) {
        s = s->__slice__(2, 0, (-1), 0);
        mult = mcomplex(0.0, 1.0);
    }
    if (((new list<str *>(2, new str("+"), new str("-"))))->__contains__(s)) {
        s = s->__iadd__(new str("1"));
    }
    return mult * __float(s);
}

str *complex::__repr__() {
    return __format(*this, new str()); /* see format.cpp */
}

/* power */

template<> complex __power(complex a, complex b) {
    complex r;
    __ss_float vabs, len, at, phase;
    if(b.real == 0 and b.imag == 0) {
        r.real = 1;
        r.imag = 0;
    }
    else if(a.real == 0 and a.imag == 0) {
#ifndef __SS_NOZERO
        if(b.imag != 0 || b.real < 0)
            __throw_zero_division("0.0 to a negative or complex power");
#endif
        r.real = 0;
        r.imag = 0;
    }
    else {
        vabs = __abs(a);
        len = std::pow(vabs,b.real);
        at = std::atan2(a.imag, a.real);
        phase = at*b.real;
        if (b.imag != 0.0) {
            len /= std::exp(at*b.imag);
            phase += b.imag*std::log(vabs);
        }
        r.real = len*std::cos(phase);
        r.imag = len*std::sin(phase);
    }
    return r;
}

/* glue */

#ifdef __SS_BIND
void throw_exception();

template<> complex __to_ss(PyObject *p) {
    /* both return -1.0 with an exception set on failure: a non-number, or
       an int too large for a double */
    double real = PyComplex_RealAsDouble(p);
    if (real == -1.0 && PyErr_Occurred() != NULL)
        throw_exception();
    double imag = PyComplex_ImagAsDouble(p);
    if (imag == -1.0 && PyErr_Occurred() != NULL)
        throw_exception();
    return mcomplex(real, imag);
}

template<> PyObject *__to_py(complex c) {
    return PyComplex_FromDoubles(c.real, c.imag);
}
#endif
