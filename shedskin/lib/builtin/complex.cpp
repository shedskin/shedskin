/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* complex methods */

complex mcomplex(str *s) {
    const char *ptr = s->strip()->c_str();
    char *ptr2;
    __ss_float real, imag = 0;

    if (*ptr == 0) {
        goto error;
    }

    real = strtod(ptr, &ptr2);
    if (ptr != ptr2 && *ptr2 == 'j') {
        if (ptr2[1] != 0) {
            goto error;
        }
        imag = real;
        real = 0;
    } else if (*ptr2 != 0) {
        char *ptr3;
        imag = strtod(ptr2, &ptr3);
        if (ptr2 == ptr3) {
            // No number before 'j', but possibly sign. Or completely malformed string
            imag = 1;
            if (*ptr3 == '-') {
                imag = -1;
                ptr3++;
            } else if (*ptr3 == '+') {
                ptr3++;
            }
        }
        if (*ptr3 != 'j' || ptr3[1] != 0) {
error:
            throw ((new ValueError(new str("complex() arg is a malformed string"))));
        }
    }

    return mcomplex(real, imag);
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

/* power */

template<> complex __power(complex a, complex b) {
    complex r;
    __ss_float vabs, len, at, phase;
    if(b.real == 0 and b.imag == 0) {
        r.real = 1;
        r.imag = 0;
    }
    else if(a.real == 0 and a.imag == 0) {
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
template<> complex __to_ss(PyObject *p) {
    return mcomplex(PyComplex_RealAsDouble(p), PyComplex_ImagAsDouble(p));
}

template<> PyObject *__to_py(complex c) {
    return PyComplex_FromDoubles(c.real, c.imag);
}
#endif

/* boxed methods */

complex_::complex_(complex c) {
    unit = c;
    __class__ = cl_complex;
}

str *complex_::__repr__() {
    return unit.__repr__();
}

__ss_bool complex_::__nonzero__() {
    return __mbool(unit.real == 0 and unit.imag == 0);
}
