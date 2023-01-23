/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* hashing */

static inline long hash_combine(long seed, long other) {
    return seed ^ (other + 0x9e3779b9 + (seed << 6) + (seed >> 2));
}

template<class T> inline long hasher(T t) {
    if(t == NULL) return 0;
    return t->__hash__();
}
#ifdef __SS_LONG
template<> inline long hasher(__ss_int a) { return (a==-1)?-2:a; }
#endif
template<> inline long hasher(int a) { return (a==-1)?-2:a; }
template<> inline long hasher(__ss_bool a) { return a.value; }
template<> inline long hasher(void *a) { return (intptr_t)a; }
template<> inline long hasher(__ss_float v) {
    long hipart, x; /* modified from CPython */
    int expo;
    v = frexp(v, &expo);
    v *= 2147483648.0; /* 2**31 */
    hipart = (long)v;   /* take the top 32 bits */
    v = (v - (__ss_float)hipart) * 2147483648.0; /* get the next 32 bits */
    x = hipart + (long)v + (expo << 15);
    if (x== -1)
        x = -2;
    return x;
}
