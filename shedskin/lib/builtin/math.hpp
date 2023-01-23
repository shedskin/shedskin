/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* pow */

inline __ss_float __power(__ss_int a, __ss_float b) { return pow(a,b); }
inline __ss_float __power(__ss_float a, __ss_int b) { 
    if(b==2) return a*a;
    else if(b==3) return a*a*a;
    else return pow(a,b); 
}

template<class A> A __power(A a, A b);
template<> inline __ss_float __power(__ss_float a, __ss_float b) { return pow(a,b); }

template<> inline __ss_int __power(__ss_int a, __ss_int b) {
    switch(b) {
        case 2: return a*a;
        case 3: return a*a*a;
        case 4: return a*a*a*a;
        case 5: return a*a*a*a*a;
        case 6: return a*a*a*a*a*a;
        case 7: return a*a*a*a*a*a*a;
        case 8: return a*a*a*a*a*a*a*a;
        case 9: return a*a*a*a*a*a*a*a*a;
        case 10: return a*a*a*a*a*a*a*a*a*a;
    }
    __ss_int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = (res*tmp);
        }
        tmp = (tmp*tmp);
        b = (b/2);
    }
    return res;
}

#ifdef __SS_LONG
inline __ss_int __power(__ss_int a, __ss_int b, __ss_int c) {
    __ss_int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = ((res*tmp)%c);
        }
        tmp = ((tmp*tmp)%c);
        b = (b/2);
    }
    return res;
}
#endif

inline int __power(int a, int b, int c) {
    long long res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = ((res*tmp)%c);
        }
        tmp = ((tmp*tmp)%c);
        b = (b/2);
    }
    return (int)res;
}

/* division */

template<class A> A __divs(A a, A b);
template<> inline __ss_float __divs(__ss_float a, __ss_float b) { return a/b; }
#ifdef __SS_LONG
template<> inline __ss_int __divs(__ss_int a, __ss_int b) {
    if(a<0 && b>0) return (a-b+1)/b;
    else if(b<0 && a>0) return (a-b-1)/b;
    else return a/b;
}
#endif

template<class A, class B> __ss_float __divs(A a, B b);
template<> inline __ss_float __divs(__ss_int a, __ss_float b) { return (__ss_float)a/b; }
template<> inline __ss_float __divs(__ss_float a, __ss_int b) { return a/((__ss_float)b); }

inline __ss_float __divs(__ss_int a, __ss_int b) { return a/((__ss_float)b); }

template<class A> inline A __floordiv(A a, A b) { return a->__floordiv__(b); }
template<> inline __ss_float __floordiv(__ss_float a, __ss_float b) { return floor(a/b); }

#ifdef __SS_LONG /* XXX */
template<> inline __ss_int __floordiv(__ss_int a, __ss_int b) { return (__ss_int)floor((__ss_float)a/b); } /* XXX */
#endif
template<> inline int __floordiv(int a, int b) { return (int)floor((__ss_float)a/b); } /* XXX */

inline __ss_float __floordiv(__ss_int a, __ss_float b) { return floor((__ss_float)a/b); }
inline __ss_float __floordiv(__ss_float a, __ss_int b) { return floor(a/((__ss_float)b)); }

/* modulo */

template<class A> A __mods(A a, A b);
#ifdef __SS_LONG /* XXX */
template<> inline __ss_int __mods(__ss_int a, __ss_int b) {
    int m = a%b;
    if((m<0 && b>0)||(m>0 && b<0)) m+=b;
    return m;
}
#endif
template<> inline int __mods(int a, int b) {
    int m = a%b;
    if((m<0 && b>0)||(m>0 && b<0)) m+=b;
    return m;
}
template<> inline __ss_float __mods(__ss_float a, __ss_float b) {
    __ss_float f = fmod(a,b);
    if((f<0 && b>0)||(f>0 && b<0)) f+=b;
    return f;
}

template<class A, class B> __ss_float __mods(A a, B b);
#ifdef __SS_LONG
template<> inline __ss_float __mods(__ss_int a, __ss_float b) { return __mods((__ss_float)a, b); }
template<> inline __ss_float __mods(__ss_float a, __ss_int b) { return __mods(a, (__ss_float)b); }
#endif
template<> inline __ss_float __mods(int a, __ss_float b) { return __mods((__ss_float)a, b); }
template<> inline __ss_float __mods(__ss_float a, int b) { return __mods(a, (__ss_float)b); }

/* divmod */

template<class A> inline tuple2<A, A> *divmod(A a, A b) { return a->__divmod__(b); }
template<> inline tuple2<__ss_float, __ss_float> *divmod(__ss_float a, __ss_float b) {
    return new tuple2<__ss_float, __ss_float>(2, __floordiv(a,b), __mods(a,b));
}
#ifdef __SS_LONG
template<> inline tuple2<__ss_int, __ss_int> *divmod(__ss_int a, __ss_int b) {
    return new tuple2<__ss_int, __ss_int>(2, __floordiv(a,b), __mods(a,b));
}
#endif
template<> inline tuple2<int, int> *divmod(int a, int b) {
    return new tuple2<int, int>(2, __floordiv(a,b), __mods(a,b));
}

inline tuple2<__ss_float, __ss_float> *divmod(__ss_float a, __ss_int b) { return divmod(a, (__ss_float)b); }
inline tuple2<__ss_float, __ss_float> *divmod(__ss_int a, __ss_float b) { return divmod((__ss_float)a, b); }

/* add */

template<class T> inline T __add(T a, T b) { return a->__add__(b); }
#ifdef __SS_LONG
template<> inline __ss_int __add(__ss_int a, __ss_int b) { return a + b; }
#endif
template<> inline int __add(int a, int b) { return a + b; }
template<> inline __ss_float __add(__ss_float a, __ss_float b) { return a + b; }

/* reverse */

template<class U> U __add2(__ss_float a, U b) { return b->__add__(a); }
template<class U> U __sub2(__ss_float a, U b) { return b->__rsub__(a); }
template<class T> T __mul2(__ss_int n, T a) { return a->__mul__(n); }
template<class T> T __mul2(__ss_bool n, T a) { return a->__mul__(n.value); }
template<class T> T __mul2(__ss_float n, T a) { return a->__mul__(n); }
template<class T> T __div2(__ss_int n, T a) { return a->__rdiv__(n); }
template<class T> T __div2(__ss_float n, T a) { return a->__rdiv__(n); }

/* float.is_integer */

inline __ss_bool __ss_is_integer(__ss_float d) {
    return __mbool((long long)d == d);
}
