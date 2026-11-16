/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_SET_HPP
#define SS_SET_HPP

template<class T> struct set_looper {
    typename __GC_SET<T>::iterator it;
};

template <class T> class __setiter final : public __iter<T> {
public:
    set<T> *p;
    typename __GC_SET<T>::iterator it;

    __setiter(set<T> *p);
    T __next__();
};

/* final: users cannot subclass builtins (see graph.py), so the C++ compiler may devirtualize */
template<class T> class set final : public pyiter<T> {
public:
    int frozen;
    __ss_int hash;

    __GC_SET<T> gcs;

    template<class U> set(U *other, int frozen);
    template<class U> set(U *other);
    set(int frozen=0);
    template<class ... Args> set(int count, Args ... args);

    void *add(T key);
    void *discard(T key);
    void *remove(T key);
    T pop();

    str* __repr__();

    __ss_bool __contains__(T key) final;
    template <class U> requires (!std::is_convertible_v<U, T> && !std::is_arithmetic_v<U>) __ss_bool __contains__(U key);
    __ss_int __len__() final;

    void *clear();
    set<T> *copy();

    void *update(int);
    void *update(int, set<T> *s);
    void *update(int, list<T> *l);
    template <class U> void *update(int, U *other);
    template <class U, class V> void *update(int, U *other, V *other2);
    template <class U, class V, class W> void *update(int, U *other, V *other2, W *other3);

    set<T> *intersection(int);
    set<T> *intersection(int, set<T> *s);
    template <class U> set<T> *intersection(int, U *other);
    template <class U, class V> set<T> *intersection(int, U *iter, V *iter2);
    template <class U, class V, class W> set<T> *intersection(int, U *iter, V *iter2, W *iter3);

    void *intersection_update(int);
    void *intersection_update(int, set<T> *s);
    template <class U> void *intersection_update(int, U *other);
    template <class U, class V> void *intersection_update(int, U *other, V *other2);
    template <class U, class V, class W> void *intersection_update(int, U *other, V *other2, W *other3);

    set<T> *difference(int);
    set<T> *difference(int, set<T> *s);
    template <class U> set<T> *difference(int, U *other);
    template <class U, class V> set<T> *difference(int, U *other, V *other2);
    template <class U, class V, class W> set<T> *difference(int, U *other, V *other2, W *other3);

    void *difference_update(int);
    void *difference_update(int, set<T> *s);
    template <class U> void *difference_update(int, U *other);
    template <class U, class V> void *difference_update(int, U *other, V *other2);
    template <class U, class V, class W> void *difference_update(int, U *other, V *other2, W *other3);

    set<T> *__ss_union(int);
    set<T> *__ss_union(int, set<T> *s);
    template <class U> set<T> *__ss_union(int, U *other);
    template <class U, class V> set<T> *__ss_union(int, U *other, V *other2);
    template <class U, class V, class W> set<T> *__ss_union(int, U *other, V *other2, W *other3);

    set<T> *symmetric_difference(set<T> *s);
    template <class U> set<T> *symmetric_difference(U *other);
    void *symmetric_difference_update(set<T> *s);
    template <class U> void *symmetric_difference_update(U *other);

    template <class U> set<T> *__and__(U *s);
    template <class U> set<__ss_wider_t<T, std::remove_cvref_t<typename U::for_in_unit>>> *__or__(U *s);
    template <class U> set<__ss_wider_t<T, std::remove_cvref_t<typename U::for_in_unit>>> *__xor__(U *s);
    template <class U> set<T> *__sub__(U *s);

    set<T> *__iand__(set<T> *s);
    template <class U> set<T> *__ior__(U *s);
    set<T> *__ixor__(set<T> *s);
    set<T> *__isub__(set<T> *s);

    __ss_bool issubset(pyiter<T> *s);
    __ss_bool issubset(set<T> *s);
    __ss_bool issuperset(set<T> *s);
    __ss_bool issuperset(pyiter<T> *s);

    __ss_bool isdisjoint(set<T> *s);
    __ss_bool isdisjoint(pyiter<T> *s);

    __ss_bool __gt__(pyobj *);
    __ss_bool __lt__(pyobj *);
    __ss_bool __ge__(pyobj *);
    __ss_bool __le__(pyobj *);

    __ss_bool __gt__(set<T> *s);
    __ss_bool __lt__(set<T> *s);
    __ss_bool __ge__(set<T> *s);
    __ss_bool __le__(set<T> *s);

    __ss_bool __eq__(pyobj *p);

    __setiter<T> *__iter__() {
        return new __setiter<T>(this);
    }

    set<T> *__copy__();
    set<T> *__deepcopy__(dict<void *, pyobj *> *memo);

    /* iteration */

    typedef T for_in_unit;
    typedef set_looper<T> for_in_loop;

    inline set_looper<T> for_in_init() {
        set_looper<T> l;
        l.it = gcs.begin();
        return l;
    }

    inline bool for_in_has_next(set_looper<T> &l) {
        return l.it != gcs.end();
    }

    inline T for_in_next(set_looper<T> &l) {
        return *(l.it++);
    }

#ifdef __SS_BIND
    set(PyObject *);
    PyObject *__to_py__();
#endif

    __ss_int __hash__();
};


template <class T> set<T>::set(int frozen_) : frozen(frozen_) {
    this->__class__ = cl_set;
    this->hash = -1;
}

#ifdef __SS_BIND

template<class T> set<T>::set(PyObject *p) {
    this->__class__ = cl_set;
    this->hash = -1;
    if(PyFrozenSet_CheckExact(p))
        frozen = 1;
    else if(PyAnySet_CheckExact(p))
        frozen = 0;
    else
        throw new TypeError(new str("error in conversion to Shed Skin (set expected)"));

    PyObject *iter = PyObject_GetIter(p), *item;
    while ((item = PyIter_Next(iter))) {
        add(__to_ss<T>(item));
        Py_DECREF(item);
    }
    Py_DECREF(iter);
}

template<class T> PyObject *set<T>::__to_py__() {
    list<T> *l = new list<T>(this); /* XXX optimize */
    PyObject *s;
    PyObject *p = __to_py(l);
    if(frozen)
        s = PyFrozenSet_New(p);
    else
        s = PySet_New(p);
    Py_DECREF(p);
    return s;
}

#endif

template<class T> template<class U> set<T>::set(U *other, int frozen_) {
    this->__class__ = cl_set;
    this->frozen = frozen_;
    this->hash = -1;

    update(1, other);
}

template<class T> template<class U> set<T>::set(U *other) {
    this->__class__ = cl_set;
    this->frozen = 0;
    this->hash = -1;

    update(1, other);
}

template<class T> template<class ... Args> set<T>::set(int, Args ... args)  {
    this->__class__ = cl_set;
    this->frozen = 0;
    this->hash = -1;

    (this->add(args), ...);
}

template<class T> __ss_bool set<T>::__eq__(pyobj *p) { /* XXX check hash */
    set<T> *b = (set<T> *)p;

    if(b->__len__() != this->__len__())
        return False;

    // TODO why can't we just use unordered_map operator==
    for (const auto& key : gcs)
        if (b->gcs.find(key) == b->gcs.end())
            return False;

    return True;
}

template <class T> void *set<T>::discard(T key) {
    typename __GC_SET<T>::iterator it = gcs.find(key);
    if(it != gcs.end())
        gcs.erase(it);
    return NULL;
}

template <class T> void *set<T>::remove(T key) {
    typename __GC_SET<T>::iterator it = gcs.find(key);
    if(it == gcs.end())
        throw __key_error(key);
    else
        gcs.erase(it);
    return NULL;
}

template<class T> T set<T>::pop() {
    typename __GC_SET<T>::iterator it = gcs.begin();
    if(it == gcs.end())
        throw new KeyError(new str("pop from an empty set"));
    T t = *it;
    gcs.erase(it);
    return t;
}

/* suppress -Wvirtual-overloaded warnings TODO better to always use pyobj *? */
template<class T> __ss_bool set<T>::__lt__(pyobj *) { return False; }
template<class T> __ss_bool set<T>::__gt__(pyobj *) { return False; }
template<class T> __ss_bool set<T>::__ge__(pyobj *) { return False; }
template<class T> __ss_bool set<T>::__le__(pyobj *) { return False; }

template<class T> __ss_bool set<T>::__ge__(set<T> *s) {
    return issuperset(s);
}

template<class T> __ss_bool set<T>::__le__(set<T> *s) {
    return issubset(s);
}

template<class T> __ss_bool set<T>::__lt__(set<T> *s) {
    return __mbool(__len__() < s->__len__() && issubset(s).value);
}

template<class T> __ss_bool set<T>::__gt__(set<T> *s) {
    return __mbool(__len__() > s->__len__() && issuperset(s).value);
}

/* comparing sets of different element types (e.g. ints and floats): in the wider one */
template<class W, class E> inline set<W> *__ss_set_as(set<E> *s) {
    if constexpr (std::is_same_v<W, E>)
        return s;
    else {
        if(!s)
            return NULL;
        set<W> *c = new set<W>(s->frozen);
        c->update(1, s);
        return c;
    }
}

#define __SS_SET_CMP(op) \
template<class A, class B> requires (!std::is_same_v<A, B>) inline __ss_bool op(set<A> *a, set<B> *b) { \
    static_assert(__ss_widens_v<A, B> || __ss_widens_v<B, A>, \
        "set comparison: element types cannot be converted to each other"); \
    using W = std::conditional_t<__ss_widens_v<A, B>, B, A>; \
    return op(__ss_set_as<W>(a), __ss_set_as<W>(b)); \
}
__SS_SET_CMP(__eq)
__SS_SET_CMP(__ne)
__SS_SET_CMP(__lt)
__SS_SET_CMP(__le)
__SS_SET_CMP(__gt)
__SS_SET_CMP(__ge)
#undef __SS_SET_CMP

template<class T> __ss_int set<T>::__hash__() {
    if(!frozen)
        throw new TypeError(new str("unhashable type: 'set'"));

    if (hash != -1)
        return hash;

    /* unsigned: no (undefined) signed overflow */
    __ss_uint_hash_t hash_ = 1927868237UL;

    hash_ *= (__ss_uint_hash_t)__len__() + 1;

    for (const auto& key : gcs)
        hash_ ^= (__ss_uint_hash_t)hash_shuffle_bits(hasher<T>(key));

    hash_ ^= (hash_ >> 11) ^ (hash_ >> 25); /* as in CPython: disperse clustered (e.g. small int) hashes */
    hash_ = hash_ * 69069UL + 907133923UL;
    if ((__ss_int)hash_ == -1)
        hash_ = 590923713UL;

    hash = (__ss_int)hash_;
    return hash;
}

template <class T> void *set<T>::add(T key)
{
    gcs.insert(key);
    return NULL;
}

template<class T> str *set<T>::__repr__() {
    str *r;

    if(this->frozen) {
        if(gcs.size() == 0)
            return new str("frozenset()");
        r = new str("frozenset({");
    }
    else {
        if(gcs.size() == 0)
            return new str("set()");
        r = new str("{");
    }

    size_t rest = gcs.size()-1;

    typename __GC_SET<T>::iterator it;
    for(it = gcs.begin(); it != gcs.end(); it++) {
        r->unit += repr(*it)->unit;
        if(rest)
           r->unit += __gcs(", ");
        --rest;
    }

    if(this->frozen)
        r->unit += __gcs("})");
    else
        r->unit += __gcs("}");
    return r;
}

template<class T> __ss_int set<T>::__len__() {
    return (__ss_int)gcs.size();
}

template <class T> inline __ss_bool set<T>::__contains__(T key) {
    return __mbool(gcs.find(key) != gcs.end());
}

/* a key of another type: see list<T>::__contains__ */
template <class T> template <class U> requires (!std::is_convertible_v<U, T> && !std::is_arithmetic_v<U>) __ss_bool set<T>::__contains__(U key) {
    return __contains__(__ss_key<T>(key));
}

template <class T> void *set<T>::clear()
{
    gcs.clear();
    return NULL;
}

template<class T> void *set<T>::update(int, set<T> *s) {
    gcs.reserve(4);
    gcs.insert(s->gcs.begin(),s->gcs.end());
    return NULL;
}

template<class T> void *set<T>::update(int, list<T> *l) {
    gcs.reserve(4);
    gcs.insert(l->units.begin(),l->units.end());
    return NULL;
}

template<class T> template<class U> void *set<T>::update(int, U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        add(__ss_elem<T>(e));
    END_FOR
    return NULL;
}

template<class T> template<class U, class V> void *set<T>::update(int, U *iter, V *iter2) {
    update(1, iter);
    update(1, iter2);
    return NULL;
}

template<class T> template<class U, class V, class W> void *set<T>::update(int, U *iter, V *iter2, W *iter3) {
    update(1, iter);
    update(1, iter2);
    update(1, iter3);
    return NULL;
}


template<class T> template<class U> set<T> *set<T>::__ss_union(int, U *other) {
    set<T> *c = new set<T>(this->frozen);
    c->gcs = gcs;
    c->update(1, other);
    return c;
}

template<class T> set<T> *set<T>::__ss_union(int, set<T> *s) {
    set<T> *a, *b;
    set<T> *c = new set<T>(this->frozen);

    if(len(s) < len(this)) { a = s; b = this; }
    else { a = this; b = s; }

    c->gcs = b->gcs;
    c->update(1, a);

    return c;
}


template<class T> template<class U, class V> set<T> *set<T>::__ss_union(int, U *other, V *other2) {
    set<T> *c = new set<T>(this->frozen);
    c->gcs = gcs;
    c->update(1, other, other2);
    return c;
}

template<class T> template<class U, class V, class W> set<T> *set<T>::__ss_union(int, U *other, V *other2, W *other3) {
    set<T> *c = new set<T>(this->frozen);
    c->gcs = gcs;
    c->update(1, other, other2, other3);
    return c;
}

template<class T> set<T> *set<T>::symmetric_difference(set<T> *s) {
    set<T> *c = new set<T>(this->frozen);

    // TODO optimize based on size difference?

    for (const auto& key : gcs) {
        if (!s->__contains__(key))
            c->add(key);
    }
    for (const auto& key : s->gcs) {
        if (!__contains__(key))
            c->add(key);
    }

    return c;
}

template<class T> template <class U> set<T> *set<T>::symmetric_difference(U *iter) {
    set<T> *c = new set<T>(this->frozen);
    c->gcs = gcs;

    /* membership is checked against 'this', so duplicates in 'iter' are harmless */
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        T x = __ss_elem<T>(e);
        if (__contains__(x))
            c->gcs.erase(x);
        else
            c->gcs.insert(x);
    END_FOR

    return c;
}

template<class T> template <class U> set<T> *set<T>::intersection(int, U *iter) {
    set<T>* result = new set<T>(this->frozen);

    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        T x = __ss_elem<T>(e);
        if (__contains__(x)) {
            result->add(x);
        }
    END_FOR

    return result;
}

template<class T> set<T> *set<T>::intersection(int, set<T> *s) {
    set<T> *c = new set<T>(this->frozen);

    // TODO optimize based on size difference?

    for (const auto& key : gcs)
        if (s->__contains__(key))
            c->add(key);

    return c;
}

template<class T> template<class U, class V> set<T> *set<T>::intersection(int, U *iter, V *iter2) {
    return intersection(1, iter)->intersection(1, iter2);
}

template<class T> template<class U, class V, class W> set<T> *set<T>::intersection(int, U *iter, V *iter2, W *iter3) {
    return intersection(1, iter)->intersection(1, iter2)->intersection(1, iter3);
}


template<class T> template<class U> set<T>* set<T>::difference(int, U *other) {
    return difference(1, new set<T>(other));
}

template<class T> template<class U, class V> set<T>* set<T>::difference(int, U *other, V *other2) {
    set<T> *result = difference(1, new set<T>(other));
    return result->difference(1, new set<T>(other2));
}

template<class T> template<class U, class V, class W> set<T>* set<T>::difference(int, U *other, V *other2, W *other3) {
    set<T> *result = difference(1, new set<T>(other));
    result = result->difference(1, new set<T>(other2));
    return result->difference(1, new set<T>(other3));
}

template <class T> set<T>* set<T>::difference(int, set<T> *other)
{
    set<T>* result = new set<T>(this->frozen);
    for (const auto& key : gcs)
        if (!other->__contains__(key))
            result->gcs.insert(key);
    return result;
}

/* other element types: converted on the way (e.g. ints into a set of floats) */
#define __SS_SET_ELEMS_WIDEN(U, T, what) \
    static_assert(__ss_widens_v<std::remove_cvref_t<typename U::for_in_unit>, T>, \
        "set." what ": elements of the other set do not fit (e.g. floats into a set of ints)")

/* a set of a wider element type on the right (e.g. ints & floats): computed in the wider
   type. the result of & and - holds elements of the left set, so it is converted back
   (without loss), while that of | and ^ has the wider element type */
#define __SS_SET_ELEMS_COMPAT(U, T, what) \
    using E = std::remove_cvref_t<typename U::for_in_unit>; \
    static_assert(__ss_compatible_v<E, T>, \
        "set." what ": element types cannot be converted to each other")

template<class T> template<class U> set<T> *set<T>::__and__(U *s) {
    __SS_SET_ELEMS_COMPAT(U, T, "__and__");
    if constexpr (__ss_widens_v<E, T>)
        return intersection(1, s);
    else if constexpr (std::is_same_v<T, void *>) /* empty */
        return new set<T>(this->frozen);
    else
        return __ss_set_as<T>(__ss_set_as<E>(this)->intersection(1, s));
}
template<class T> template<class U> set<__ss_wider_t<T, std::remove_cvref_t<typename U::for_in_unit>>> *set<T>::__or__(U *s) {
    __SS_SET_ELEMS_COMPAT(U, T, "__or__");
    if constexpr (__ss_widens_v<E, T>)
        return __ss_union(1, s);
    else
        return __ss_set_as<E>(this)->__ss_union(1, s);
}
template<class T> template<class U> set<__ss_wider_t<T, std::remove_cvref_t<typename U::for_in_unit>>> *set<T>::__xor__(U *s) {
    __SS_SET_ELEMS_COMPAT(U, T, "__xor__");
    if constexpr (__ss_widens_v<E, T>)
        return symmetric_difference(s);
    else
        return __ss_set_as<E>(this)->symmetric_difference(s);
}
template<class T> template<class U> set<T> *set<T>::__sub__(U *s) {
    __SS_SET_ELEMS_COMPAT(U, T, "__sub__");
    if constexpr (__ss_widens_v<E, T>)
        return difference(1, s);
    else if constexpr (std::is_same_v<T, void *>) /* empty */
        return new set<T>(this->frozen);
    else
        return __ss_set_as<T>(__ss_set_as<E>(this)->difference(1, s));
}
#undef __SS_SET_ELEMS_COMPAT
template<class T> set<T> *set<T>::__iand__(set<T> *s) {
    if(this->frozen) /* frozenset: rebind to a new object */
        return intersection(1, s);
    this->gcs = intersection(1, s)->gcs;
    return this;
}
/* any element type: converted on the way (e.g. ints into a set of floats) */
template<class T> template<class U> set<T> *set<T>::__ior__(U *s) {
    __SS_SET_ELEMS_WIDEN(U, T, "__ior__");
    if(this->frozen) /* frozenset: rebind to a new object */
        return __ss_union(1, s);
    this->gcs = __ss_union(1, s)->gcs;
    return this;
}
template<class T> set<T> *set<T>::__ixor__(set<T> *s) {
    if(this->frozen) /* frozenset: rebind to a new object */
        return symmetric_difference(s);
    this->gcs = symmetric_difference(s)->gcs;
    return this;
}
template<class T> set<T> *set<T>::__isub__(set<T> *s) {
    if(this->frozen) /* frozenset: rebind to a new object */
        return difference(1, s);
    this->gcs = difference(1, s)->gcs;
    return this;
}

template<class T> void *set<T>::difference_update(int, set<T> *s) {
    set<T> *c = difference(1, s);
    this->gcs = c->gcs;
    return NULL;
}


template<class T> template <class U> void *set<T>::difference_update(int, U *iter) {
    difference_update(1, new set<T>(iter));
    return NULL;
}

template<class T> template<class U, class V> void *set<T>::difference_update(int, U *iter, V *iter2) {
    difference_update(1, iter);
    difference_update(1, iter2);
    return NULL;
}

template<class T> template<class U, class V, class W> void *set<T>::difference_update(int, U *iter, V *iter2, W *iter3) {
    difference_update(1, iter);
    difference_update(1, iter2);
    difference_update(1, iter3);
    return NULL;
}

template<class T> void *set<T>::symmetric_difference_update(set<T> *s) {
    set<T> *c = symmetric_difference(s);
    this->gcs = c->gcs;
    return NULL;
}

template<class T> template<class U> void *set<T>::symmetric_difference_update(U *other) {
    this->gcs = symmetric_difference(other)->gcs;
    return NULL;
}

template<class T> void *set<T>::intersection_update(int, set<T> *s) {
    set<T> *c = intersection(1, s);
    this->gcs = c->gcs;
    return NULL;
}

template<class T> template<class U> void *set<T>::intersection_update(int, U *iter) {
    intersection_update(1, new set<T>(iter));
    return NULL;
}

template<class T> template<class U, class V> void *set<T>::intersection_update(int, U *iter, V *iter2) {
    intersection_update(1, new set<T>(iter));
    intersection_update(1, new set<T>(iter2));
    return NULL;
}

template<class T> template<class U, class V, class W> void *set<T>::intersection_update(int, U *iter, V *iter2, W *iter3) {
    intersection_update(1, new set<T>(iter));
    intersection_update(1, new set<T>(iter2));
    intersection_update(1, new set<T>(iter3));
    return NULL;
}

/* zero-argument forms: union(), intersection() and difference() return a copy; the _update forms do nothing */

template<class T> set<T> *set<T>::__ss_union(int) { return copy(); }
template<class T> set<T> *set<T>::intersection(int) { return copy(); }
template<class T> set<T> *set<T>::difference(int) { return copy(); }
template<class T> void *set<T>::update(int) { return NULL; }
template<class T> void *set<T>::intersection_update(int) { return NULL; }
template<class T> void *set<T>::difference_update(int) { return NULL; }

template<class T> set<T> *set<T>::copy() {
    set<T> *c = new set<T>(this->frozen);
    c->gcs = gcs;
    return c;
}

template<class T> __ss_bool set<T>::issubset(set<T> *s) {
    if(__len__() > s->__len__()) { return False; }
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN(e,this,1,2,3)
        if(!s->__contains__(e))
            return False;
    END_FOR
    return True;
}

template<class T> __ss_bool set<T>::issuperset(set<T> *s) {
    if(__len__() < s->__len__()) return False;
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN(e,s,1,2,3)
        if(!__contains__(e))
            return False;
    END_FOR
    return True;
}

template<class T> __ss_bool set<T>::isdisjoint(set<T> *other) {
    typename __GC_SET<T>::iterator it = gcs.begin();
    while (it != gcs.end())
        if (other->__contains__(*it++))
            return False;
    return True;
}


template<class T> __ss_bool set<T>::issubset(pyiter<T> *s) {
    return issubset(new set<T>(s));
}

template<class T> __ss_bool set<T>::issuperset(pyiter<T> *s) {
    return issuperset(new set<T>(s));
}

template<class T> __ss_bool set<T>::isdisjoint(pyiter<T> *s) {
    return isdisjoint(new set<T>(s));
}

template<class T> set<T> *set<T>::__copy__() {
    set<T> *c = new set<T>(this->frozen);
    c->gcs = gcs;
    return c;
}

template<class T> set<T> *set<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    set<T> *c = new set<T>(this->frozen);
    memo->__setitem__(this, c);
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN(e,this,1,2,3)
        c->add(__deepcopy(e, memo));
    END_FOR
    return c;
}

template<class T> __setiter<T>::__setiter(set<T> *s) {
    this->p = s;
    it = s->gcs.begin();
}

template<class T> T __setiter<T>::__next__() {
    if(it == p->gcs.end())
        __throw_stop_iteration();
    return *it++;
}

#endif
