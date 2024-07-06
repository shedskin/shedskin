/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_COPY_HPP
#define SS_COPY_HPP

template<class T> T __copy(T t) {
    if(!t)
        return (T)NULL;
    return (T)(t->__copy__());
}

#ifdef __SS_LONG
template<> inline __ss_int __copy(__ss_int i) { return i; }
#endif
template<> inline int __copy(int i) { return i; }
template<> inline __ss_bool __copy(__ss_bool b) { return b; }
template<> inline __ss_float __copy(__ss_float d) { return d; }
template<> inline void *__copy(void *p) { return p; }

template<class T> T __deepcopy(T t, dict<void *, pyobj *> *memo=0) {
    if(!t)
        return (T)NULL;

    if(!memo)
        memo = new dict<void *, pyobj *>();
    T u = (T)(memo->get(t, 0));
    if(u)
       return u;

    return (T)(t->__deepcopy__(memo));
}

#ifdef __SS_LONG
template<> inline __ss_int __deepcopy(__ss_int i, dict<void *, pyobj *> *) { return i; }
#endif
template<> inline int __deepcopy(int i, dict<void *, pyobj *> *) { return i; }
template<> inline __ss_bool __deepcopy(__ss_bool b, dict<void *, pyobj *> *) { return b; }
template<> inline __ss_float __deepcopy(__ss_float d, dict<void *, pyobj *> *) { return d; }
template<> inline void *__deepcopy(void *p, dict<void *, pyobj *> *) { return p; }

/* builtin copy methods */

template<class T> tuple2<T,T> *tuple2<T,T>::__copy__() {
    tuple2<T,T> *c = new tuple2<T,T>();
    c->units = this->units;
    return c;
}

template<class T> tuple2<T,T> *tuple2<T,T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    tuple2<T,T> *c = new tuple2<T,T>();
    memo->__setitem__(this, c);
    c->units.resize(this->units.size());
    for(size_t i=0; i<this->units.size(); i++)
        c->units[i] = __deepcopy(this->units[i], memo);
    return c;
}

template<class A, class B> tuple2<A,B> *tuple2<A,B>::__copy__() {
    return new tuple2<A,B>(2, first, second);
}

template<class A, class B> tuple2<A,B> *tuple2<A,B>::__deepcopy__(dict<void *, pyobj *> *memo) {
    tuple2<A,B> *n = new tuple2<A,B>();
    memo->__setitem__(this, n);
    n->first = __deepcopy(first, memo);
    n->second = __deepcopy(second, memo);
    return n;
}

template<class T> list<T> *list<T>::__copy__() {
    list<T> *c = new list<T>();
    c->units = this->units;
    return c;
}

template<class T> list<T> *list<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    list<T> *c = new list<T>();
    memo->__setitem__(this, c);
    c->units.resize(this->units.size());
    for(size_t i=0; i<this->units.size(); i++)
        c->units[i] = __deepcopy(this->units[i], memo);
    return c;
}

template<class K, class V> dict<K,V> *dict<K,V>::__copy__() {
    dict<K,V> *c = new dict<K,V>;
    c->gcd = gcd;
    return c;
}

template<class K, class V> dict<K,V> *dict<K,V>::__deepcopy__(dict<void *, pyobj *> *memo) {
    dict<K,V> *c = new dict<K,V>();
    memo->__setitem__(this, c);
    K e;
    typename dict<K,V>::for_in_loop __3;
    int __2;
    dict<K,V> *__1;
    FOR_IN(e,this,1,2,3)
        c->__setitem__(__deepcopy(e, memo), __deepcopy(this->__getitem__(e), memo));
    END_FOR
    return c;
}

/* copy, deepcopy */

template<> inline complex __copy(complex a) { return a; }
template<> inline complex __deepcopy(complex a, dict<void *, pyobj *> *) { return a; }

#endif
