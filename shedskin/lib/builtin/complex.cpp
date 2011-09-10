/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* complex methods */

complex mcomplex(str *s) {
    complex c;
    __re__::match_object *m;
    __re__::re_object *p;

    p = __re__::compile(new str("(?P<one>[+-]?([\\d\\.]+e[+-]?\\d+|[\\d\\.]*)j?)(?P<two>[+-]?([\\d\\.]+e[+-]?\\d+|[\\d\\.]*)j?)?$"));
    m = p->match(s->strip());
    if (___bool(m)) {
        c = (c.parsevalue(m->group(1, new str("one")))) + (c.parsevalue(m->group(1, new str("two"))));
    }
    else {
        throw ((new ValueError(new str("complex() arg is a malformed string"))));
    }
    return c;
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
    double vabs, len, at, phase;
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
