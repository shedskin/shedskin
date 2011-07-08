/* complex */

complex *__power(complex *a, complex *b);
complex *__power(complex *a, __ss_int b);
complex *__power(complex *a, double b);

tuple2<complex *, complex *> *divmod(complex *a, double b);
tuple2<complex *, complex *> *divmod(complex *a, __ss_int b);

template<class T> complex::complex(T t) {
    __class__ = cl_complex;
    real = __float(t);
    imag = 0;
}
