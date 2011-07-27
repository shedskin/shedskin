/* sum */

template<class A> struct __sumtype1 { typedef A type; };
template<> struct __sumtype1<__ss_bool> { typedef int type; };

template<class A, class B> struct __sumtype2 { typedef A type; };
template<> struct __sumtype2<__ss_bool, __ss_bool> { typedef __ss_int type; };
template<> struct __sumtype2<__ss_bool, __ss_int> { typedef __ss_int type; };
template<> struct __sumtype2<__ss_bool, double> { typedef double type; };
template<> struct __sumtype2<__ss_int, double> { typedef double type; };

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

template<class T, class B> T ___max(int n, B (*key)(T), T a, T b, T c, ...) {
    T m = ___max(2, key, ___max(2, key, a, b), c);
    B maxkey = key(m);
    va_list ap;
    va_start(ap, c);
    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(key(t),maxkey)==1)
            m=t;
    }
    va_end(ap);
    return m;
}
template<class T> T ___max(int n, int key, T a, T b, T c, ...) {
    T m = ___max(2, key, ___max(2, key, a, b), c);
    va_list ap;
    va_start(ap, c);
    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(t,m)==1) m=t;
    }
    va_end(ap);
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

template<class T, class B> T ___min(int n, B (*key)(T), T a, T b, T c, ...) {
    T m = ___min(2, key, ___min(2, key, a, b), c);
    B minkey = key(m);
    va_list ap;
    va_start(ap, c);
    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(key(t),minkey)==-1)
            m=t;
    }
    va_end(ap);
    return m;
}
template<class T> T ___min(int n, int key, T a, T b, T c, ...) { /* XXX */
    T m = ___min(2, key, ___min(2, key, a, b), c);
    va_list ap;
    va_start(ap, c);
    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(t,m)==-1)
            m=t;
    }
    va_end(ap);
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

    __enumiter(pyiter<A> *p) {
        this->p = ___iter(p);
        i = 0;
    }

    tuple2<__ss_int, A> *next() {
        return new tuple2<__ss_int, A>(2, i++, p->next());
    }
};

template <class A> __iter<tuple2<__ss_int, A> *> *enumerate(pyiter<A> *x) {
    return new __enumiter<A>(x);
}

/* zip */

list<tuple2<void *, void *> *> *__zip(int nn);

template <class A> list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *> *__zip(int nn, A *iter) {
    list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *> *result = (new list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *>());
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN(e,iter,1,2,3)
        result->append((new tuple2<typename A::for_in_unit, typename A::for_in_unit>(1, e)));
    END_FOR
    return result;
}

template <class A, class B> list<tuple2<typename A::for_in_unit, typename B::for_in_unit> *> *__zip(int, A *itera, B *iterb) {
    list<tuple2<typename A::for_in_unit, typename B::for_in_unit> *> *result = (new list<tuple2<typename A::for_in_unit, typename B::for_in_unit> *>());
    tuple2<typename A::for_in_unit, typename B::for_in_unit> *tuples;
    int count = -1;
    if(A::is_pyseq && B::is_pyseq) {
        count = __SS_MIN(len(itera), len(iterb));
        tuples = new tuple2<typename A::for_in_unit, typename B::for_in_unit>[count];
        result->units.resize(count);
    }
    typename A::for_in_unit e;
    typename A::for_in_loop __3 = itera->for_in_init();
    typename B::for_in_unit f;
    typename B::for_in_loop __6 = iterb->for_in_init();
    int i = 0;
    while(itera->for_in_has_next(__3) and iterb->for_in_has_next(__6)) {
        e = itera->for_in_next(__3);
        f = iterb->for_in_next(__6);
        if(count == -1)
            result->append((new tuple2<typename A::for_in_unit, typename B::for_in_unit>(2, e, f)));
        else {
            tuples[i].__init2__(e, f);
            result->units[i] = &tuples[i];
            i++;
        }
    }
    return result;
}

template <class A, class B, class C> list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *> *__zip(int, A *itera, B *iterb, C *iterc) {
    list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *> *result = (new list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *>());
    tuple2<typename A::for_in_unit, typename A::for_in_unit> *tuples;
    int count = -1;
    if(A::is_pyseq && B::is_pyseq && C::is_pyseq) {
        count = __SS_MIN3(len(itera), len(iterb), len(iterc));
        tuples = new tuple2<typename A::for_in_unit, typename A::for_in_unit>[count];
        result->units.resize(count);
    }
    typename A::for_in_unit e;
    typename A::for_in_loop __3 = itera->for_in_init();
    typename B::for_in_unit f;
    typename B::for_in_loop __6 = iterb->for_in_init();
    typename C::for_in_unit g;
    typename C::for_in_loop __7 = iterc->for_in_init();
    int i = 0;
    while(itera->for_in_has_next(__3) and iterb->for_in_has_next(__6) and iterc->for_in_has_next(__7)) {
        e = itera->for_in_next(__3);
        f = iterb->for_in_next(__6);
        g = iterc->for_in_next(__7);
        if(count == -1)
            result->append((new tuple2<typename A::for_in_unit, typename A::for_in_unit>(3, e, f, g)));
        else {
            tuples[i].units.push_back(e);
            tuples[i].units.push_back(f);
            tuples[i].units.push_back(g);
            result->units[i] = &tuples[i];
            i++;
        }
    }
    return result;
}

/* next */

template <class A> A next(__iter<A> *iter1, A fillvalue) {
    try {
        return iter1->next();
    } catch(StopIteration *) {
        return fillvalue;
    }
}
template <class A> A next(__iter<A> *iter1, void *) { return next(iter1, __zero<A>()); }
template <class A> A next(__iter<A> *iter1) { return iter1->next(); }

/* map */

template <class A, class B> list<B> *map(int, B (*func)(typename A::for_in_unit), A *iter) {
    if(!func)
        throw new ValueError(new str("'map' function argument cannot be None"));
    list<B> *result = new list<B>();
    int count = -1;
    if(A::is_pyseq) {
        count = len(iter);
        result->units.resize(count);
    }
    typename A::for_in_unit e;
    typename A::for_in_loop __3 = iter->for_in_init();
    int i = 0;
    while(iter->for_in_has_next(__3)) {
        e = iter->for_in_next(__3);
        if(count == -1)
            result->append((*func)(e));
        else
            result->units[i++] = (*func)(e);
    }
    return result;
}

template <class A, class B, class C> list<A> *map(int n, A (*func)(B, C), pyiter<B> *b, pyiter<C> *c) {
    if(!func)
        throw new ValueError(new str("'map' function argument cannot be None"));
    list<A> *result = new list<A>();
    __iter<B> *itb = b->__iter__();
    __iter<C> *itc = c->__iter__();
    B nextb;
    C nextc;
    int total;
    while(1) {
        total = 0;
        try { nextb = next(itb); total += 1; } catch (StopIteration *) { nextb = __zero<B>(); }
        try { nextc = next(itc); total += 1; } catch (StopIteration *) { nextc = __zero<C>(); }
        if(total == 0)
            break;
        result->append((*func)(nextb, nextc));
    }
    return result;
}

template <class A, class B, class C, class D> list<A> *map(int, A (*func)(B, C, D), pyiter<B> *b1, pyiter<C> *b2, pyiter<D> *b3) {
    if(!func)
        throw new ValueError(new str("'map' function argument cannot be None"));
    list<A> *result = new list<A>();
    __iter<B> *itb1 = b1->__iter__();
    __iter<C> *itb2 = b2->__iter__();
    __iter<D> *itb3 = b3->__iter__();
    B nextb1;
    C nextb2;
    D nextb3;
    int total;
    while(1)  {
        total = 0;
        try { nextb1 = next(itb1); total += 1; } catch (StopIteration *) { nextb1 = __zero<B>(); }
        try { nextb2 = next(itb2); total += 1; } catch (StopIteration *) { nextb2 = __zero<C>(); }
        try { nextb3 = next(itb3); total += 1; } catch (StopIteration *) { nextb3 = __zero<D>(); }
        if(total == 0)
            break;
        result->append((*func)(nextb1, nextb2, nextb3));
    }
    return result;
}

/* reduce */

template<class A, class B, class C> A reduce(A (*func)(A, A), B *iter, C initial) {
    A result = initial;
    typename B::for_in_loop __7 = iter->for_in_init();
    while(iter->for_in_has_next(__7))
        result = (*func)(result, iter->for_in_next(__7));
    return result;
}

template<class A, class B> A reduce(A (*func)(A, A), B *iter) {
    A result;
    typename B::for_in_loop __7 = iter->for_in_init();
    int first = 1;
    while(iter->for_in_has_next(__7)) {
        if(first) {
            result = iter->for_in_next(__7);
            first = 0;
        } else
            result = (*func)(result, iter->for_in_next(__7));
    }
    if(first) 
        throw new TypeError(new str("reduce() of empty sequence with no initial value"));
    return result;
}

/* filter */

template <class A, class B> list<typename A::for_in_unit> *filter(B (*func)(typename A::for_in_unit), A *iter) {
    list<typename A::for_in_unit> *result = new list<typename A::for_in_unit>();
    typename A::for_in_unit e;
    typename A::for_in_loop __3 = iter->for_in_init();
    while(iter->for_in_has_next(__3)) {
        e = iter->for_in_next(__3);
        if(func) {
            if(___bool((*func)(e)))
                result->append(e);
        } else if(___bool(e))
            result->append(e);
    }
    return result;
}

template <class A, class B> tuple2<A,A> *filter(B (*func)(A), tuple2<A,A> *a) {
    tuple2<A,A> *result = new tuple2<A,A>();
    int size = len(a);
    A e;
    for(int i=0; i<size; i++) {
        e = a->units[i];
        if(func) {
            if(___bool((*func)(e)))
                result->units.push_back(e);
        } else if(___bool(e))
            result->units.push_back(e);
    }
    return result;
}

template <class B> str *filter(B (*func)(str *), str *a) {
    str *result = new str();
    int size = len(a);
    char e;
    str *c;
    for(int i=0; i<size; i++) {
        e = a->unit[i];
        if(func) {
            c = __char_cache[((unsigned char)e)];
            if(___bool((*func)(c)))
                result->unit.push_back(e);
        } else 
            result->unit.push_back(e);
    }
    return result;
}

template <class A> list<A> *filter(void *func, pyiter<A> *a) { return filter(((int(*)(A))(func)), a); }
inline str *filter(void *, str *a) { return filter(((int(*)(str *))(0)), a); }
template <class A> tuple2<A,A> *filter(void *func, tuple2<A,A> *a) { return filter(((int(*)(A))(func)), a); }

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

int ord(str *c);

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
    return hex((int)i);
}
template<> inline str *oct(__ss_int i) {
    return oct((int)i);
}
template<> inline str *bin(__ss_int i) {
    return bin((int)i);
}
#endif

/* id */

template <class T> __ss_int id(T t) { 
    return (intptr_t)t;
}
template <> __ss_int id(__ss_int);
template <> __ss_int id(double);
template <> __ss_int id(__ss_bool);

/* type */

template<class T> class_ *__type(T t) { return t->__class__; }
template<> class_ *__type(int i);
template<> class_ *__type(double d);

