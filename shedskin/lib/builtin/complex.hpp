/* complex */

/*
complex *__power(complex *a, complex *b);
complex *__power(complex *a, __ss_int b);
complex *__power(complex *a, double b);

tuple2<complex *, complex *> *divmod(complex *a, double b);
tuple2<complex *, complex *> *divmod(complex *a, __ss_int b);

*/


inline double __abs(complex c) { return 1.0; };

template<> inline __ss_bool ___bool(complex c) { return False; }

template<> inline complex __floordiv(complex a, complex b) { return a.__floordiv__(b); }
inline complex __floordiv(complex a, int b) { return a.__floordiv__(b); }
inline complex __floordiv(complex a, double b) { return a.__floordiv__(b); }
inline complex __floordiv(int a, complex b) { return ((complex)(a)).__floordiv__(b); }
inline complex __floordiv(double a, complex b) { return ((complex)(a)).__floordiv__(b); }

tuple2<complex, complex> *divmod(complex a, complex b);
tuple2<complex, complex> *divmod(complex a, int b);
