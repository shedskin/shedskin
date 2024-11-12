/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_BYTES_HPP
#define SS_BYTES_HPP

class bytes : public pyseq<__ss_int> {
protected:
public:
    __GC_STRING unit;
    long hash;
    int frozen;

    bytes(int frozen=1);
    bytes(const char *s);
    bytes(bytes *b, int frozen=1);
    bytes(__GC_STRING s, int frozen=1);
    bytes(const char *s, int size, int frozen=1); /* '\0' delimiter in C */

    inline __ss_int __getitem__(__ss_int i);
    inline __ss_int __getfast__(__ss_int i);

    template<class U> bytes *join(U *);

    inline __ss_int __len__();
    bytes *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);

    bytes *rstrip(bytes *chars=0);
    bytes *strip(bytes *chars=0);
    bytes *lstrip(bytes *chars=0);

    list<bytes *> *split(bytes *sep=0, __ss_int maxsplit=-1);
    list<bytes *> *rsplit(bytes *sep=0, __ss_int maxsplit=-1);
    tuple2<bytes *, bytes *> *rpartition(bytes *sep);
    tuple2<bytes *, bytes *> *partition(bytes *sep);
    list<bytes *> *splitlines(__ss_int keepends = 0);

    /* functions pointing to the underlying C++ implementation */
    char *c_str() const;

    __ss_int __fixstart(size_t a, __ss_int b);
    __ss_int __checkneg(__ss_int i);

    bytes *upper();
    bytes *lower();
    bytes *title();
    bytes *capitalize();

    __ss_bool istitle();
    __ss_bool isspace();
    __ss_bool isalpha();
    __ss_bool isdigit();
    __ss_bool islower();
    __ss_bool isupper();
    __ss_bool isalnum();
    __ss_bool __ss_isascii();

    __ss_bool startswith(bytes *s, __ss_int start=0);
    __ss_bool startswith(bytes *s, __ss_int start, __ss_int end);

    __ss_bool endswith(bytes *s, __ss_int start=0);
    __ss_bool endswith(bytes *s, __ss_int start, __ss_int end);

    __ss_int find(bytes *s, __ss_int a=0);
    __ss_int find(bytes *s, __ss_int a, __ss_int b);
    __ss_int find(__ss_int i, __ss_int a=0);
    __ss_int find(__ss_int i, __ss_int a, __ss_int b);

    __ss_int rfind(bytes *s, __ss_int a=0);
    __ss_int rfind(bytes *s, __ss_int a, __ss_int b);
    __ss_int rfind(__ss_int i, __ss_int a=0);
    __ss_int rfind(__ss_int i, __ss_int a, __ss_int b);

    __ss_int count(bytes *b, __ss_int start=0);
    __ss_int count(__ss_int b, __ss_int start=0);
    __ss_int count(bytes *b, __ss_int start, __ss_int end);
    __ss_int count(__ss_int b, __ss_int start, __ss_int end);

    __ss_int index(bytes *s, __ss_int a=0);
    __ss_int index(bytes *s, __ss_int a, __ss_int b);
    __ss_int index(__ss_int i, __ss_int a=0);
    __ss_int index(__ss_int i, __ss_int a, __ss_int b);

    __ss_int rindex(bytes *s, __ss_int a=0);
    __ss_int rindex(bytes *s, __ss_int a, __ss_int b);
    __ss_int rindex(__ss_int i, __ss_int a=0);
    __ss_int rindex(__ss_int i, __ss_int a, __ss_int b);

    bytes *expandtabs(__ss_int tabsize=8);

    bytes *swapcase();

    bytes *replace(bytes *a, bytes *b, __ss_int c=-1);

    bytes *center(__ss_int width, bytes *fillchar=0);

    bytes *zfill(__ss_int width);
    bytes *ljust(__ss_int width, bytes *fillchar=0);
    bytes *rjust(__ss_int width, bytes *fillchar=0);

    str *hex(str *sep=0);

    str *__str__();
    str *__repr__();

    __ss_bool __contains__(__ss_int);
    __ss_bool __contains__(bytes *);

    __ss_bool __eq__(pyobj *s);
    long __hash__();

    __ss_bool __ctype_function(int (*cfunc)(int));

    bytes *__add__(bytes *b);
    bytes *__mul__(__ss_int n);

    /* iteration */

    inline bool for_in_has_next(size_t i);
    inline __ss_int for_in_next(size_t &i);

    /* bytearray */

    void *clear();
    void *append(__ss_int i);
    __ss_int pop(__ss_int i=-1);
    bytes *copy();
    void *extend(pyiter<__ss_int> *p);
    void *reverse();
    void *insert(__ss_int index, __ss_int item);

    void *__setitem__(__ss_int i, __ss_int e);
    void *__delitem__(__ss_int i);

    void *remove(__ss_int i);

    bytes *__iadd__(bytes *b);
    bytes *__imul__(__ss_int n);

    void *__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, pyiter<__ss_int> *b);
    void *__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);

#ifdef __SS_BIND
    bytes(PyObject *p);
    PyObject *__to_py__();
#endif
};

inline __ss_int bytes::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return (unsigned char)(unit[(size_t)i]);
}

inline __ss_int bytes::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return (unsigned char)(unit[(size_t)i]);
}

inline void *bytes::__setitem__(__ss_int i, __ss_int e) {
    i = __wrap(this, i);
    if(e < 0)
        throw new ValueError(new str("byte must be in range(0, 256)"));
    unit[(size_t)i] = (char)e;
    return NULL;
}

inline __ss_int bytes::__len__() {
    return (__ss_int)this->unit.size();
}

inline bool bytes::for_in_has_next(size_t i) {
    return i < this->unit.size(); /* XXX opt end cond */
}

inline __ss_int bytes::for_in_next(size_t &i) {
    return (unsigned char)(unit[i++]);
}

template <class U> bytes *bytes::join(U *iter) {
    size_t sz, total;
    int __2;
    bool only_ones = true;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    U *__1;
    list<bytes *> __join_cache;
    __join_cache.units.resize(0);
    total = 0;
    FOR_IN(e,iter,1,2,3)
        __join_cache.units.push_back(e);
        sz = e->unit.size();
        if(sz != 1)
            only_ones = false;
        total += sz;
    END_FOR
    size_t unitsize = this->unit.size();
    size_t elems = __join_cache.units.size();
    if(elems==1)
        return __join_cache.units[0];
    bytes *s = new bytes(frozen);
    if(unitsize == 0 and only_ones) {
        s->unit.resize(total);
        for(size_t j=0; j<elems; j++)
            s->unit[j] = __join_cache.units[j]->unit[0];
    }
    else if(elems) {
        total += (elems-1)*unitsize;
        s->unit.resize(total);
        size_t tsz;
        size_t k = 0;
        for(size_t m = 0; m<elems; m++) {
            bytes *t = __join_cache.units[m];
            tsz = t->unit.size();
            if (tsz == 1)
                s->unit[k] = t->unit[0];
            else
                memcpy((void *)(s->unit.data()+k), t->unit.data(), tsz);
            k += tsz;
            if (unitsize && m < elems-1) {
                if (unitsize==1)
                    s->unit[k] = unit[0];
                else
                    memcpy((void *)(s->unit.data()+k), unit.data(), this->unit.size());
                k += unitsize;
            }
        }
    }
    return s;
}

/* bytes */

template<class T> bytes *__bytes(T *t) {
    if constexpr (std::is_base_of_v<pyiter<__ss_int>, T>) {
        bytes *b = new bytes();
        __ss_int e;
        typename T::for_in_loop __3;
        __ss_int __2;
        T *__1;
        FOR_IN(e,t,1,2,3)
            b->unit += (char)e;
        END_FOR
        return b;
    } else {
        if (!t)
            return new bytes("None");
        else
            return t->__bytes__();
    }
}

bytes *__bytes(bytes *b);
 bytes *__bytes(__ss_int t);
bytes *__bytes();

template<class T> bytes *__bytearray(T *t) {
    if constexpr (std::is_base_of_v<pyiter<__ss_int>, T>) {
        bytes *b = new bytes();
        b->frozen = 0;
        __ss_int e;
        typename pyiter<__ss_int>::for_in_loop __3;
        int __2;
        pyiter<__ss_int> *__1;
        FOR_IN(e,t,1,2,3)
            b->unit += (char)e;
        END_FOR
        return b;
    } else {
        if (!t)
            return new bytes("None");
        else
            return t->__bytes__();
    }
}

bytes *__bytearray(bytes *b);
bytes *__bytearray(__ss_int t);
bytes *__bytearray();

#endif
