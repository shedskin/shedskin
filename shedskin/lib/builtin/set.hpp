/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

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
    this->__class__ = cl_dict;
    this->frozen = 0;
    this->hash = -1;

    (this->add(args), ...);
}

template<class T> __ss_bool set<T>::__eq__(pyobj *p) { /* XXX check hash */
    set<T> *b = (set<T> *)p;

    // TODO why can't we just use unordered_map operator==
    typename __GC_SET<T>::iterator it;

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
        throw new KeyError(repr(key));
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

template<class T> __ss_bool set<T>::__ge__(set<T> *s) {
    return issuperset(s);
}

template<class T> __ss_bool set<T>::__le__(set<T> *s) {
    return issubset(s);
}

template<class T> __ss_bool set<T>::__lt__(set<T> *s) {
    return issubset(s);
}

template<class T> __ss_bool set<T>::__gt__(set<T> *s) {
    return issuperset(s);
}

template<class T> long set<T>::__hash__() {
    if(!frozen)
        throw new TypeError(new str("unhashable type: 'set'"));

    if (hash != -1)
        return hash;

    // element order does not matter!

    long hash_ = 1927868237L;

    hash_ *= __len__() + 1;

    for (const auto& key : gcs) {
        long h = hasher<T>(key);
        hash_ ^= (h ^ (h << 16) ^ 89869747L)  * 3644798167u;
    }
    hash_ = hash_ * 69069L + 907133923L;
    if (hash_ == -1)
        hash_ = 590923713L;

    hash = hash_;
    return hash_;
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
           r->unit += ", ";
        --rest;
    }

    if(this->frozen)
        r->unit += "})";
    else
        r->unit += "}";
    return r;
}

template<class T> __ss_int set<T>::__len__() {
    return (__ss_int)gcs.size();
}

template <class T> __ss_bool set<T>::__contains__(T key) {
    return __mbool(gcs.find(key) != gcs.end());
}

template <class T> void *set<T>::clear()
{
    gcs.clear();
    return NULL;
}

template<class T> void *set<T>::update(int, set<T> *s) {
   for (const auto& key : s->gcs)
       gcs.insert(key);
    return NULL;
}

template<class T> template<class U> void *set<T>::update(int, U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        add(e);
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
    *c = *this;
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
    *c = *this;
    c->update(1, other, other2);
    return c;
}

template<class T> template<class U, class V, class W> set<T> *set<T>::__ss_union(int, U *other, V *other2, W *other3) {
    set<T> *c = new set<T>(this->frozen);
    *c = *this;
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

template<class T> template <class U> set<T> *set<T>::intersection(int, U *iter) {
    set<T>* result = new set<T>;

    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        if (__contains__(e)) {
            result->add(e);
        }
    END_FOR

    return result;
}

template<class T> set<T> *set<T>::intersection(int, set<T> *s) {
    set<T> *a, *b;
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
    set<T>* result = new set<T>();
    for (const auto& key : gcs)
        if (!other->__contains__(key))
            result->gcs.insert(key);
    return result;
}

template<class T> set<T> *set<T>::__and__(set<T> *s) {
    return intersection(1, s);
}
template<class T> set<T> *set<T>::__or__(set<T> *s) {
    return __ss_union(1, s);
}
template<class T> set<T> *set<T>::__xor__(set<T> *s) {
    return symmetric_difference(s);
}
template<class T> set<T> *set<T>::__sub__(set<T> *s) {
    return difference(1, s);
}
template<class T> set<T> *set<T>::__iand__(set<T> *s) {
    this->gcs = intersection(1, s)->gcs;
    return this;
}
template<class T> set<T> *set<T>::__ior__(set<T> *s) {
    this->gcs = __ss_union(1, s)->gcs;
    return this;
}
template<class T> set<T> *set<T>::__ixor__(set<T> *s) {
    this->gcs = symmetric_difference(s)->gcs;
    return this;
}
template<class T> set<T> *set<T>::__isub__(set<T> *s) {
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
    set<T> *c = new set<T>();
    c->gcs = gcs;
    return c;
}

template<class T> set<T> *set<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    set<T> *c = new set<T>();
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
    it = s->gcs.begin();
}

template<class T> T __setiter<T>::__next__() {
    if(it == p->gcs.end())
        __throw_stop_iteration();
    return *it++;
}
