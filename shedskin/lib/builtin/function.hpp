/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* sum */

template<class A> struct __sumtype1 { typedef A type; };
template<> struct __sumtype1<__ss_bool> { typedef int type; };

template<class A, class B> struct __sumtype2 { typedef A type; };
template<> struct __sumtype2<__ss_bool, __ss_bool> { typedef __ss_int type; };
template<> struct __sumtype2<__ss_bool, __ss_int> { typedef __ss_int type; };
template<> struct __sumtype2<__ss_bool, __ss_float> { typedef __ss_float type; };
template<> struct __sumtype2<__ss_int, __ss_float> { typedef __ss_float type; };

template <class U> typename __sumtype1<typename U::for_in_unit>::type __sum(U *iter) {
    typename __sumtype1<typename U::for_in_unit>::type result;
    result = __zero<typename __sumtype1<typename U::for_in_unit>::type>();
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    bool first = true;
    FOR_IN(e,iter,1,2,3)
        if(first) {
            result = (typename __sumtype1<typename U::for_in_unit>::type)e;
            first = false;
        }
        else
            result = __add(result, (typename __sumtype1<typename U::for_in_unit>::type)e);
    END_FOR
    return result;
}

template <class U, class B> typename __sumtype2<typename U::for_in_unit,B>::type __sum(U *iter, B b) {
    typename __sumtype1<typename U::for_in_unit>::type result1 = __sum(iter);
    return __add((typename __sumtype2<typename U::for_in_unit,B>::type)b, (typename __sumtype2<typename U::for_in_unit,B>::type)result1);
}

/* max */

template<class A, class B> typename A::for_in_unit ___max(int, B (*key)(typename A::for_in_unit), A *iter) {
    typename A::for_in_unit max;
    B maxkey, maxkey2;
    max = __zero<typename A::for_in_unit>(); 
    maxkey = __zero<B>(); 
    maxkey2 = __zero<B>();;
    int first = 1;
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN(e,iter,1,2,3)
        if(key) {
            maxkey2 = key(e);
            if(first || __cmp(maxkey2, maxkey) == 1) {
                max = e;
                maxkey = maxkey2;
            }
        } else if(first || __cmp(e, max) == 1)
            max = e;
        if(first)
            first = 0;
    END_FOR
    if(first)
        throw new ValueError(new str("max() arg is an empty sequence"));
    return max;
}

/* XXX copy-pasto */
template<class A, class B> typename A::for_in_unit ___max(int, pycall1<B, typename A::for_in_unit> *key, A *iter) {
    typename A::for_in_unit max;
    B maxkey, maxkey2;
    int first = 1;
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN(e,iter,1,2,3)
        if(key) {
            maxkey2 = key->__call__(e);
            if(first || __cmp(maxkey2, maxkey) == 1) {
                max = e;
                maxkey = maxkey2;
            }
        } else if(first || __cmp(e, max) == 1)
            max = e;
        if(first)
            first = 0;
    END_FOR
    if(first)
        throw new ValueError(new str("max() arg is an empty sequence"));
    return max;
}
template<class A> typename A::for_in_unit ___max(int nn, int, A *iter) { return ___max(nn, (int (*)(typename A::for_in_unit))0, iter); }

template<class T, class B> inline T ___max(int, B (*key)(T), T a, T b) { return (__cmp(key(a), key(b))==1)?a:b; }
template<class T> inline  T ___max(int, int, T a, T b) { return (__cmp(a, b)==1)?a:b; }

template<class T, class B> inline void update_max(T &m, B (*key)(T), T a) {
    if(__cmp(key(a),key(m))==1)
        m=a;
}

template<class T, class B, class ... Args> T ___max(int n, B (*key)(T), T a, T b, T c, Args ... args) {
    T m = a;
    update_max(m, key, b);
    update_max(m, key, c);
    (update_max(m, key, args), ...);
    return m;
}

template<class T> inline void update_max(T &m, int key, T a) {
    if(__cmp(a,m)==1)
        m=a;
}

template<class T, class ... Args> T ___max(int n, int key, T a, T b, T c, Args ... args) {
    T m = a;
    update_max(m, key, b);
    update_max(m, key, c);
    (update_max(m, key, args), ...);
    return m;
}

/* min */

template<class A, class B> typename A::for_in_unit ___min(int, B (*key)(typename A::for_in_unit), A *iter) {
    typename A::for_in_unit min;
    B minkey, minkey2;
    min = __zero<typename A::for_in_unit>(); 
    minkey = __zero<B>(); 
    minkey2 = __zero<B>();
    int first = 1;
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN(e,iter,1,2,3)
        if(key) {
            minkey2 = key(e);
            if(first || __cmp(minkey2, minkey) == -1) {
                min = e;
                minkey = minkey2;
            }
        } else if(first || __cmp(e, min) == -1)
            min = e;
        if(first)
            first = 0;
    END_FOR
    if(first)
        throw new ValueError(new str("min() arg is an empty sequence"));
    return min;
}
template<class A> typename A::for_in_unit ___min(int nn, int, A *iter) { return ___min(nn, (int (*)(typename A::for_in_unit))0, iter); }

template<class T, class B> inline T ___min(int, B (*key)(T), T a, T b) { return (__cmp(key(a), key(b))==-1)?a:b; }
template<class T> inline  T ___min(int, int, T a, T b) { return (__cmp(a, b)==-1)?a:b; }

template<class T, class B> inline void update_min(T &m, B (*key)(T), T a) {
    if(__cmp(key(a),key(m))==-1)
        m=a;
}

template<class T, class B, class ... Args> T ___min(int n, B (*key)(T), T a, T b, T c, Args ... args) {
    T m = a;
    update_min(m, key, b);
    update_min(m, key, c);
    (update_min(m, key, args), ...);
    return m;
}

template<class T> inline void update_min(T &m, int key, T a) {
    if(__cmp(a,m)==-1)
        m=a;
}

template<class T, class ... Args> T ___min(int n, int key, T a, T b, T c, Args ... args) {
    T m = a;
    update_min(m, key, b);
    update_min(m, key, c);
    (update_min(m, key, args), ...);
    return m;
}

/* sorted */

template <class U, class V, class W> list<typename U::for_in_unit> *sorted(U *iter, V cmp, W key, __ss_int reverse) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    list<typename U::for_in_unit> *l = new list<typename U::for_in_unit>();
    FOR_IN(e,iter,1,2,3)
        l->units.push_back(e);
    END_FOR
    l->sort(cmp, key, reverse);
    return l;
}

template <class A, class V, class W> list<A> *sorted(list<A> *x, V cmp, W key, __ss_int reverse) {
    list<A> *l = new list<A>();
    l->units = x->units;
    l->sort(cmp, key, reverse);
    return l;
}

template <class A, class V, class W> list<A> *sorted(tuple2<A,A> *x, V cmp, W key, __ss_int reverse) {
    list<A> *l = new list<A>();
    l->units = x->units;
    l->sort(cmp, key, reverse);
    return l;
}

template <class V, class W> list<str *> *sorted(str *x, V cmp, W key, __ss_int reverse) {
    list<str *> *l = new list<str *>(x);
    l->sort(cmp, key, reverse);
    return l;
}

/* reversed */

template<class A> class __ss_reverse : public __iter<A> {
public:
    pyseq<A> *p;
    __ss_int i;
    __ss_reverse(pyseq<A> *p) {
        this->p = p;
        i = len(p);
    }

    A __get_next() {
        if(i>0)
            return p->__getitem__(--i); /* XXX avoid wrap, str spec? */
        this->__stop_iteration = true;
        return __zero<A>();
    }
};

template <class A> __ss_reverse<A> *reversed(pyiter<A> *x) {
    return new __ss_reverse<A>(new list<A>(x));
}
template <class A> __ss_reverse<A> *reversed(pyseq<A> *x) {
    return new __ss_reverse<A>(x);
}
__iter<__ss_int> *reversed(__xrange *x);

/* enumerate */

template<class A> class __enumiter : public __iter<tuple2<__ss_int, A> *> {
public:
    __iter<A> *p;
    __ss_int i;

    __enumiter(pyiter<A> *p, __ss_int start=0) {
        this->p = ___iter(p);
        i = start;
    }

    tuple2<__ss_int, A> *__next__() {
        return new tuple2<__ss_int, A>(2, i++, p->__next__());
    }

    inline str *__str__() {
        return new str("<enumerate object>");
    }
};

template <class A> __iter<tuple2<__ss_int, A> *> *enumerate(pyiter<A> *x) {
    return new __enumiter<A>(x);
}

template <class A> __iter<tuple2<__ss_int, A> *> *enumerate(pyiter<A> *x, __ss_int start) {
    return new __enumiter<A>(x, start);
}

/* zip */

template<class T, class U> class izipiter : public __iter<tuple2<T, U> *> {
public:
    bool exhausted;
    __ss_bool strict;

    __iter<T> *first;
    __iter<U> *second;

    izipiter(__ss_bool strict);
    izipiter(__ss_bool strict, pyiter<T> *iterable1, pyiter<U> *iterable2);

    tuple2<T, U> *__next__();

    inline str *__str__() { return new str("<zip object>"); }
};

template<class T, class U> inline izipiter<T, U>::izipiter(__ss_bool strict) {
    this->exhausted = true;
    this->strict = strict;
}
template<class T, class U> inline izipiter<T, U>::izipiter(__ss_bool strict, pyiter<T> *iterable1, pyiter<U> *iterable2) {
    this->exhausted = false;
    this->strict = strict;
    this->first = iterable1->__iter__();
    this->second = iterable2->__iter__();
}

template<class T, class U> tuple2<T, U> *izipiter<T, U>::__next__() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    tuple2<T, U> *tuple = new tuple2<T, U>;

    size_t n_exhausted = 0;

    try  {
        tuple->first = this->first->__next__();
    } catch (StopIteration *) {
        n_exhausted += 1;
    }
    try  {
        tuple->second = this->second->__next__();
    } catch (StopIteration *) {
        n_exhausted += 1;
    }

    if (n_exhausted) {
        this->exhausted = true;
        if (this->strict and n_exhausted != 2)
            throw new ValueError(new str("zip() arguments of different lengths"));
        else
            throw new StopIteration();
    }

    return tuple;
}

template<class T> class izipiter<T, T> : public __iter<tuple2<T, T> *> {
public:
    bool exhausted;
    __ss_bool strict;

    __GC_VECTOR(__iter<T> *) iters;

    izipiter(__ss_bool strict);
    izipiter(__ss_bool strict, pyiter<T> *iterable);
    izipiter(__ss_bool strict, pyiter<T> *iterable1, pyiter<T> *iterable2);

    void push_iter(pyiter<T> *iterable);

    tuple2<T, T> *__next__();

    inline str *__str__() { return new str("<zip object>"); }

};

template<class T> inline izipiter<T, T>::izipiter(__ss_bool strict) {
    this->exhausted = true;
    this->strict = strict;
}
template<class T> inline izipiter<T, T>::izipiter(__ss_bool strict, pyiter<T> *iterable) {
    this->exhausted = false;
    this->strict = strict;
    this->push_iter(iterable);
}
template<class T> inline izipiter<T, T>::izipiter(__ss_bool strict, pyiter<T> *iterable1, pyiter<T> *iterable2) {
    this->exhausted = false;
    this->strict = strict;
    this->push_iter(iterable1);
    this->push_iter(iterable2);
}
template<class T> void izipiter<T, T>::push_iter(pyiter<T> *iterable) {
    this->iters.push_back(iterable->__iter__());
}

template<class T> tuple2<T, T> *izipiter<T, T>::__next__() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    tuple2<T, T> *tuple = new tuple2<T, T>;
    size_t n_exhausted = 0;

    for (unsigned int i = 0; i < this->iters.size(); ++i) {
        try  {
            tuple->units.push_back(this->iters[i]->__next__());
        } catch (StopIteration *) {
            n_exhausted += 1;
        }
    }

    if (n_exhausted) {
        this->exhausted = true;
        if (this->strict and n_exhausted != this->iters.size())
            throw new ValueError(new str("zip() arguments of different lengths"));
        else
            throw new StopIteration();
    }

    return tuple;
}

inline izipiter<void*, void*> *__zip(int iterable_count, __ss_bool strict) {
    return new izipiter<void*, void*>(strict);
}
template<class T> inline izipiter<T, T> *__zip(int iterable_count, __ss_bool strict, pyiter<T> *iterable1) {
    izipiter<T, T> *iter = new izipiter<T, T>(strict, iterable1);
    return iter;
}
template<class T, class U> inline izipiter<T, U> *__zip(int iterable_count, __ss_bool strict, pyiter<T> *iterable1, pyiter<U> *iterable2) {
    return new izipiter<T, U>(strict, iterable1, iterable2);
}
template<class T, class ... Args> inline izipiter<T, T> *__zip(int iterable_count, __ss_bool strict, pyiter<T> *iterable, pyiter<T> *iterable2, pyiter<T> *iterable3, Args ... args) {
    izipiter<T, T> *iter = new izipiter<T, T>(strict, iterable);

    iter->push_iter(iterable2);
    iter->push_iter(iterable3);
    (iter->push_iter(reinterpret_cast<pyiter<T> *>(args)), ...);

    return iter;
}

/* next */

template <class A> A next(__iter<A> *iter1, A fillvalue) {
    try {
        return iter1->__next__();
    } catch(StopIteration *) {
        return fillvalue;
    }
}
template <class A> A next(__iter<A> *iter1, void *) { return next(iter1, __zero<A>()); }
template <class A> A next(__iter<A> *iter1) { return iter1->__next__(); }

/* map */

#define I(N, TP, FP, RP, AP, DP, CP, VP)                                                                 \
template<class R, TP> class imapiter##N : public __iter<R> {                                             \
public:                                                                                                  \
    bool exhausted;                                                                                      \
    R (*function)(FP);                                                                                   \
    RP                                                                                                   \
                                                                                                         \
    imapiter##N();                                                                                       \
    imapiter##N(R (*function)(FP), DP);                                                                  \
                                                                                                         \
    R __next__();                                                                                        \
    inline str * __str__() { return new str("<map object>"); }                                           \
};                                                                                                       \
                                                                                                         \
template<class R, TP> inline imapiter##N<R, FP>::imapiter##N() {                                         \
    this->exhausted = true;                                                                              \
}                                                                                                        \
template<class R, TP> inline imapiter##N<R, FP>::imapiter##N(R (*function)(FP), DP) {                    \
    this->exhausted = false;                                                                             \
    this->function = function;                                                                           \
    AP                                                                                                   \
}                                                                                                        \
                                                                                                         \
template<class R, TP> R imapiter##N<R, FP>::__next__() {                                                 \
    if (this->exhausted) {                                                                               \
        throw new StopIteration();                                                                       \
    }                                                                                                    \
                                                                                                         \
    try  {                                                                                               \
        return this->function(CP);                                                                       \
    } catch (StopIteration *) {                                                                          \
        this->exhausted = true;                                                                          \
        throw;                                                                                           \
    }                                                                                                    \
}                                                                                                        \
                                                                                                         \
template<class R, TP> inline imapiter##N<R, FP> *map(int /* iterable_count */, R (*function)(FP), DP) {  \
    return new imapiter##N<R, FP>(function, VP);                                                         \
}

#define S ,
#define L(P) class T##P
#define F(P) T##P
#define E(P) __iter<T##P> *iter##P;
#define A(P) this->iter##P = iterable##P->__iter__();
#define D(P) pyiter<T##P> *iterable##P
#define C(P) this->iter##P->__next__()
#define V(P) iterable##P

I(1, L(1), F(1), E(1), A(1), D(1), C(1), V(1))
I(2, L(1) S L(2), F(1) S F(2), E(1) E(2), A(1) A(2), D(1) S D(2), C(1) S C(2), V(1) S V(2))
I(3, L(1) S L(2) S L(3), F(1) S F(2) S F(3), E(1) E(2) E(3), A(1) A(2) A(3), D(1) S D(2) S D(3), C(1) S C(2) S C(3), V(1) S V(2) S V(3))

#undef S
#undef L
#undef F
#undef E
#undef A
#undef D
#undef C
#undef V
#undef I

/* filter */

template<class T> static bool _identity(T value) {
    return value;
}

template<class T, class B> class ifilteriter : public __iter<T> {
public:
    B (*predicate)(T);
    __iter<T> *iter;

    ifilteriter();
    ifilteriter(B (*predicate)(T), pyiter<T> *iterable);

    T __next__();

    inline str *__str__() {
        return new str("<filter object>");
    }

};

template<class T, class B> inline ifilteriter<T, B>::ifilteriter() {}
template<class T, class B> inline ifilteriter<T, B>::ifilteriter(B (*predicate)(T), pyiter<T> *iterable) {
    this->predicate = predicate;
    this->iter = iterable->__iter__();
}

template<class T, class B> T ifilteriter<T, B>::__next__() {
    for (; ; ) {
        const T& value = this->iter->__next__();
        if (this->predicate(value)) {
            return value;
        }
    }

 //   assert(false && "unreachable");
}

template<class T, class B> inline ifilteriter<T, B> *filter(B (*predicate)(T), pyiter<T> *iterable) {
    return new ifilteriter<T, B>(predicate, iterable);
}
template<class T> inline ifilteriter<T, bool> *filter(void * /* null */, pyiter<T> *iterable) {
    return new ifilteriter<T, bool>(_identity, iterable);
}


/* any */

template<class A> __ss_bool any(A *iter) {
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN(e,iter,1,2,3)
        if(___bool(e))
            return True;
    END_FOR
    return False;
}

/* all */

template<class A> __ss_bool all(A *iter) {
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN(e,iter,1,2,3)
        if(!___bool(e))
            return False;
    END_FOR
    return True;
}

/* ord, chr, hex, oct, bin */

static void __throw_ord_exc(size_t s) { /* improve inlining */
    throw new TypeError(__mod6(new str("ord() expected a character, but string of length %d found"), 1, s));
}

inline __ss_int ord(str *s) {
    size_t len = s->unit.size();
    if(len != 1)
        __throw_ord_exc(len);
    return (unsigned char)(s->c_str()[0]);
}

inline __ss_int ord(bytes *s) {
    size_t len = s->unit.size();
    if(len != 1)
        __throw_ord_exc(len);
    return (unsigned char)(s->c_str()[0]);
}

static void __throw_chr_out_of_range() { /* improve inlining */
    throw new ValueError(new str("chr() arg not in range(256)"));
}
inline str *chr(int i) {
    if(i < 0 || i > 255)
        __throw_chr_out_of_range();
    return __char_cache[i];
}
inline str *chr(__ss_bool b) { return chr(b.value); }

template<class T> inline str *chr(T t) {
    return chr(t->__int__());
}

#ifdef __SS_LONG
inline str *chr(__ss_int i) {
    return chr((int)i);
}

template<> inline str *hex(__ss_int i) {
    if(i<0)
        return (new str("-0x"))->__add__(__str(-i, (__ss_int)16));
    else
        return (new str("0x"))->__add__(__str(i, (__ss_int)16));
}
template<> inline str *oct(__ss_int i) {
    if(i<0)
        return (new str("-0o"))->__add__(__str(-i, (__ss_int)8));
    else if(i>0)
        return (new str("0o"))->__add__(__str(i, (__ss_int)8));
    else
        return new str("0o0");
}
template<> inline str *bin(__ss_int i) {
    if(i<0)
        return (new str("-0b"))->__add__(__str(-i, (__ss_int)2));
    else
        return (new str("0b"))->__add__(__str(i, (__ss_int)2));
}
#endif

/* id */

template <class T> __ss_int id(T t) { 
    return (__ss_int)(intptr_t)t;
}
template <> __ss_int id(__ss_int);
template <> __ss_int id(__ss_float);
template <> __ss_int id(__ss_bool);

/* type */

template<class T> class_ *__type(T t) { return t->__class__; }
template<> class_ *__type(int i);
template<> class_ *__type(__ss_float d);

/* print .., */

template<class T> void __print_elem(str *result, T t, size_t &count, str *sep) {
    result->unit += __str(t)->unit;
    count--;
    if(count != 0)
        result->unit += sep->unit;
}

template<class ... Args> void print(int n, file *f, str *end, str *sep, Args ... args) {
    str *s = new str();
    size_t count = sizeof...(args);
    if(!sep)
        sep = sp;

    (__print_elem(s, args, count, sep), ...);

    if(!end)
        end = nl;

    if(f) {
        f->write(s);
        f->write(end);
    }
    else {
        for(unsigned int i=0; i<s->unit.size(); i++)
            printf("%c", s->unit[i]);
        for(unsigned int i=0; i<end->unit.size(); i++)
            printf("%c", end->unit[i]);
    }
}
