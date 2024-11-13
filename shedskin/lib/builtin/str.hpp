/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_STR_HPP
#define SS_STR_HPP

class str : public pyseq<str *> {
protected:
public:
    __GC_STRING unit;
    long hash;
    bool charcache;

    str();
    str(const char *s);
    str(__GC_STRING s);
    str(const char *s, size_t size); /* '\0' delimiter in C */

    __ss_bool __contains__(str *s);
    str *strip(str *chars=0);
    str *lstrip(str *chars=0);
    str *rstrip(str *chars=0);
    __ss_bool __eq__(pyobj *s);
    str *__add__(str *b);

    template<class U> str *join(U *);

    /* operators */
    //inline void operator+= (const char *c);
    str *operator+ (const char *c);
    str *operator+ (const char &c);
    void operator+= (const char *c);
    void operator+= (const char &c);
    //str *operator+ (const char c);
    //str *operator+ (str *c);
    //str *operator+ (basic_string c);

    /* functions pointing to the underlying C++ implementation */
    char *c_str() const;

    str *__str__();
    str *__repr__();
    str *__mul__(__ss_int n);
    inline str *__getitem__(__ss_int n);
    inline str *__getfast__(__ss_int i);
    inline __ss_int __len__();
    str *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);

    list<str *> *split(str *sep=0, __ss_int maxsplit=-1);
    list<str *> *rsplit(str *sep=0, __ss_int maxsplit=-1);
    tuple2<str *, str *> *rpartition(str *sep);
    tuple2<str *, str *> *partition(str *sep);
    list<str *> *splitlines(__ss_int keepends = 0);

    __ss_int __fixstart(size_t a, __ss_int b);
    __ss_int __checkneg(__ss_int i);

    __ss_int find(str *s, __ss_int a=0);
    __ss_int find(str *s, __ss_int a, __ss_int b);
    __ss_int rfind(str *s, __ss_int a=0);
    __ss_int rfind(str *s, __ss_int a, __ss_int b);

    __ss_int index(str *s, __ss_int a=0);
    __ss_int index(str *s, __ss_int a, __ss_int b);
    __ss_int rindex(str *s, __ss_int a=0);
    __ss_int rindex(str *s, __ss_int a, __ss_int b);

    __ss_int count(str *s, __ss_int start=0);
    __ss_int count(str *s, __ss_int start, __ss_int end);

    str *upper();
    str *lower();
    str *title();
    str *capitalize();
    str *casefold();

    str *replace(str *a, str *b, __ss_int c=-1);
    str *translate(str *table, str *delchars=0);
    str *swapcase();
    str *center(__ss_int width, str *fillchar=0);

    __ss_bool __ctype_function(int (*cfunc)(int));

    __ss_bool istitle();
    __ss_bool isspace();
    __ss_bool isalpha();
    __ss_bool isdigit();
    __ss_bool islower();
    __ss_bool isupper();
    __ss_bool isalnum();
    __ss_bool isprintable();
    __ss_bool isnumeric();
    __ss_bool __ss_isascii();
    __ss_bool isdecimal();
    __ss_bool isidentifier();

    __ss_bool startswith(str *s, __ss_int start=0);
    __ss_bool startswith(str *s, __ss_int start, __ss_int end);
    __ss_bool endswith(str *s, __ss_int start=0);
    __ss_bool endswith(str *s, __ss_int start, __ss_int end);

    str *zfill(__ss_int width);
    str *expandtabs(__ss_int tabsize=8);

    str *ljust(__ss_int width, str *fillchar=0);
    str *rjust(__ss_int width, str *fillchar=0);

    __ss_int __cmp__(pyobj *p);
    long __hash__();

    __ss_int __int__(); /* XXX compilation warning for int(pyseq<str *> *) */

    str *__iadd__(str *b);
    str *__imul__(__ss_int n);

    /* iteration */

    inline bool for_in_has_next(size_t i);
    inline str *for_in_next(size_t &i);

#ifdef __SS_BIND
    str(PyObject *p);
    PyObject *__to_py__();
#endif
};

inline str *str::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return __char_cache[((unsigned char)(unit[(size_t)i]))];
}

inline str *str::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return __char_cache[((unsigned char)(unit[(size_t)i]))];
}

inline __ss_int str::__len__() {
    return (__ss_int)this->unit.size();
}

inline bool str::for_in_has_next(size_t i) {
    return i < this->unit.size(); /* XXX opt end cond */
}

inline str *str::for_in_next(size_t &i) {
    return __char_cache[((unsigned char)(unit[i++]))];
}

template <class U> str *str::join(U *iter) {
    size_t sz, total;
    int __2;
    bool only_ones = true;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    U *__1;
    list<str *> __join_cache;
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
    str *s = new str();
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
            str *t = __join_cache.units[m];
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

template<class ... Args> str *__add_strs(int, Args ... args) {
    str *result = new str();
    result->unit = (args->unit + ...); /* XXX need to optimize? */
    return result;
}

#endif
