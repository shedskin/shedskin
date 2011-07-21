/* complex methods */

/*
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

long complex::__hash__() {
    return ((__ss_int)imag)*1000003+((__ss_int)real);
}

__ss_bool complex::__nonzero__() {
    return __mbool(real != 0 || imag != 0);
}


// pow 

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

// division

tuple2<complex *, complex *> *divmod(complex *a, double b) { return a->__divmod__(b); }
tuple2<complex *, complex *> *divmod(complex *a, __ss_int b) { return a->__divmod__(b); }

*/

/* complex methods */

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

long complex::__hash__() {
    return ((__ss_int)imag)*1000003+((__ss_int)real);
}
