/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* complex */

/* constructors */

inline complex mcomplex(__ss_float real, __ss_float imag) {
    complex c;
    c.real = real; c.imag = imag;
    return c;
}

template<class T> inline complex mcomplex(T t) {
    complex c;
    c.real = __float(t); c.imag = 0;
    return c;
}

/* operators */

inline complex complex::operator+(complex b) {
    return mcomplex(real+b.real, imag+b.imag);
}
inline complex complex::operator+(__ss_float b) { return (*this) + mcomplex(b); }

inline complex complex::operator-(complex b) {
    return mcomplex(real-b.real, imag-b.imag);
}
inline complex complex::operator-(__ss_float b) { return (*this) - mcomplex(b); }

inline complex complex::operator/(complex b) {
    complex c;
    __ss_float norm = b.real*b.real+b.imag*b.imag;
    c.real = (real*b.real+imag*b.imag)/norm;
    c.imag = (imag*b.real-b.imag*real)/norm;
    return c;
}
inline complex complex::operator/(__ss_float b) { return (*this) / mcomplex(b); }

inline complex complex::operator*(complex b) {
    return mcomplex(real*b.real-imag*b.imag, real*b.imag+imag*b.real); 
}
inline complex complex::operator*(__ss_float b) { return (*this) * mcomplex(b); }

inline complex complex::operator%(complex b) {
    complex c = (*this) / b;
    return (*this) - (b * (((__ss_int)c.real)));
}
inline complex complex::operator%(__ss_float b) { return (*this) % mcomplex(b); }

inline complex complex::operator-() {
    return mcomplex(-real, -imag);
}

inline complex complex::operator+() {
    return *this;
}

inline __ss_bool complex::operator==(complex b) {
    return __mbool(real==b.real and imag==b.imag);
}
inline __ss_bool complex::operator==(__ss_float b) { return (*this) == mcomplex(b); }

inline __ss_bool complex::operator!=(complex b) {
    return __mbool(real!=b.real or imag!=b.imag);
}
inline __ss_bool complex::operator!=(__ss_float b) { return (*this) != mcomplex(b); }

inline complex& complex::operator=(__ss_float a) {
    real = a;
    imag = 0.0;
    return *this;
}

/* floordiv */

static inline complex __complexfloordiv(complex a, complex b) {
    complex c = a / b;
    c.real = ((__ss_int)c.real);
    c.imag = 0;
    return c;
}

template<> inline complex __floordiv(complex a, complex b) { return __complexfloordiv(a, b); }
inline complex __floordiv(complex a, __ss_float b) { return __complexfloordiv(a, mcomplex(b)); }
inline complex __floordiv(__ss_float a, complex b) { return __complexfloordiv(mcomplex(a), b); }

/* divmod */

static tuple2<complex, complex> *__complexdivmod(complex a, complex b) {
    return new tuple2<complex, complex>(2, __complexfloordiv(a, b), a % b);
}

template<> inline tuple2<complex, complex> *divmod(complex a, complex b) { return __complexdivmod(a, b); }
inline tuple2<complex, complex> *divmod(complex a, __ss_float b) { return __complexdivmod(a, mcomplex(b)); }
inline tuple2<complex, complex> *divmod(__ss_float a, complex b) { return __complexdivmod(mcomplex(a), b); }

/* str, repr */

inline str *__str(complex c) { return c.__repr__(); }
inline str *repr(complex c) { return c.__repr__(); }

/* comparison */

template<> inline __ss_bool __eq(complex a, complex b) { return a == b; }
template<> inline __ss_bool __ne(complex a, complex b) { return a != b; }

template<> inline __ss_int __cmp(complex a, complex b) { return __mbool(true); } /* unused, satisfy templates */
template<> inline __ss_bool __gt(complex a, complex b) { return __mbool(true); }
template<> inline __ss_bool __ge(complex a, complex b) { return __mbool(true); }
template<> inline __ss_bool __lt(complex a, complex b) { return __mbool(true); }
template<> inline __ss_bool __le(complex a, complex b) { return __mbool(true); }

/* copy, deepcopy */

template<> inline complex __copy(complex a) { return a; }
template<> inline complex __deepcopy(complex a, dict<void *, pyobj *> *) { return a; }

/* add */

template<> inline complex __add(complex a, complex b) { return a + b; }

/* abs */

inline __ss_float __abs(complex c) { return std::sqrt(c.real*c.real+c.imag*c.imag); }

/* bool */

template<> inline __ss_bool ___bool(complex c) { return __mbool(c.real != 0.0 or c.imag != 0); }

/* power */

template<> complex __power(complex a, complex b);
inline complex __power(complex a, __ss_float b) { return __power(a, mcomplex(b)); }
inline complex __power(__ss_float a, complex b) { return __power(mcomplex(a), b); }

/* hashing */

template<> inline long hasher(complex c) {
    return c.__hash__();
}
inline long complex::__hash__() { return ((__ss_int)imag)*1000003+((__ss_int)real); }

/* conjugate */

inline complex complex::conjugate() { return mcomplex(real, -imag); }

/* glue */

#ifdef __SS_BIND
template<> PyObject *__to_py(complex c);
template<> complex __to_ss(PyObject *p);
#endif

