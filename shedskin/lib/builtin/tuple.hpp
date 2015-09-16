/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* tuple2 methods */

template<class T> void tuple2<T, T>::__init2__(T a, T b) {
    units.push_back(a);
    units.push_back(b);
}

template<class T> tuple2<T, T>::tuple2() {
    this->__class__ = cl_tuple;
}

template<class T> tuple2<T, T>::tuple2(int count, ...) {
    this->__class__ = cl_tuple;
    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        T t = va_arg(ap, T);
        this->units.push_back(t);
    }
    va_end(ap);
}

template<class T> template<class U> tuple2<T, T>::tuple2(U *iter) {
    this->__class__ = cl_tuple;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        this->units.push_back(e);
    END_FOR
}

template<class T> tuple2<T, T>::tuple2(list<T> *p) {
    this->__class__ = cl_tuple;
    this->units = p->units;
}

template<class T> tuple2<T, T>::tuple2(tuple2<T, T> *p) {
    this->__class__ = cl_tuple;
    this->units = p->units;
}

template<class T> tuple2<T, T>::tuple2(str *s) {
    this->__class__ = cl_tuple;
    this->units.resize(len(s));
    int sz = s->size();
    for(int i=0; i<sz; i++)
        this->units[i] = __char_cache[((unsigned char)(s->unit[i]))];
}

template<class T> T tuple2<T, T>::__getfirst__() {
    return this->units[0];
}
template<class T> T tuple2<T, T>::__getsecond__() {
    return this->units[1];
}
template<class T> inline T tuple2<T, T>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return this->units[i];
}

template<class T> __ss_int tuple2<T, T>::__len__() {
    return units.size();
}

template<class T> T tuple2<T, T>::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return units[i];
}

template<class T> str *tuple2<T, T>::__repr__() {
    str *r = new str("(");
    for(int i = 0; i<this->__len__();i++) {
        *r += repr(this->units[i])->c_str();
        if(this->__len__() == 1 )
            *r += ",";
        if(i<this->__len__()-1)
            *r += ", ";
    }
    *r += ")";
    return r;
}

template<class T> tuple2<T,T> *tuple2<T, T>::__add__(tuple2<T,T> *b) {
    tuple2<T,T> *c = new tuple2<T,T>();
    for(int i = 0; i<this->__len__();i++)
        c->units.push_back(this->units[i]);
    for(int i = 0; i<b->__len__();i++)
        c->units.push_back(b->units[i]);
    return c;
}
template<class T> tuple2<T,T> *tuple2<T, T>::__iadd__(tuple2<T,T> *b) {
    return __add__(b);
}

template<class T> tuple2<T,T> *tuple2<T, T>::__mul__(__ss_int b) {
    tuple2<T,T> *c = new tuple2<T,T>();
    if(b<=0) return c;
    __ss_int hop = this->__len__(); /* XXX merge with list */
    if(hop==1)
        c->units.insert(c->units.begin(), b, this->units[0]);
    else
        for(__ss_int i=0; i<b; i++)
            for(__ss_int j=0; j<hop; j++)
                c->units.push_back(this->units[j]);
    return c;
}
template<class T> tuple2<T,T> *tuple2<T, T>::__imul__(__ss_int b) {
    return __mul__(b);
}

template<class T> __ss_bool tuple2<T, T>::__contains__(T a) {
    for(int i=0; i<this->__len__(); i++)
        if(__eq(this->units[i], a))
            return True;
    return False;
}

template<class T> __ss_bool tuple2<T, T>::__eq__(pyobj *p) {
    tuple2<T,T> *b;
    b = (tuple2<T,T> *)p;
    unsigned int sz = this->units.size();
    if(b->units.size() != sz)
        return False;
    for(unsigned int i=0; i<sz; i++)
        if(!__eq(this->units[i], b->units[i]))
            return False;
    return True;
}

template<class T> tuple2<T,T> *tuple2<T, T>::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    tuple2<T,T> *c = new tuple2<T,T>();
    slicenr(x, l, u, s, this->__len__());
    if(s == 1) {
        c->units.resize(u-l);
        memcpy(&(c->units[0]), &(this->units[l]), sizeof(T)*(u-l));
    } else if(s > 0)
        for(int i=l; i<u; i += s)
            c->units.push_back(units[i]);
    else
        for(int i=l; i>u; i += s)
            c->units.push_back(units[i]);
    return c;
}

template<class T> long tuple2<T, T>::__hash__() {
    long seed = 0;
    size_t sz = this->units.size();
    for(size_t i = 0; i<sz; i++)
        seed = hash_combine(seed, hasher<T>(this->units[i]));
    return seed;
}

template<class T> tuple2<T,T> *tuple2<T,T>::__copy__() {
    tuple2<T,T> *c = new tuple2<T,T>();
    c->units = this->units;
    return c;
}

template<class T> tuple2<T,T> *tuple2<T,T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    tuple2<T,T> *c = new tuple2<T,T>();
    memo->__setitem__(this, c);
    c->units.resize(this->__len__());
    for(int i=0; i<this->__len__(); i++)
        c->units[i] = __deepcopy(this->units[i], memo);
    return c;
}

template<class T> inline bool tuple2<T,T>::for_in_has_next(size_t i) {
    return i < units.size(); /* XXX opt end cond */
}

template<class T> inline T tuple2<T,T>::for_in_next(size_t &i) {
    return units[i++];
}

#ifdef __SS_BIND
template<class T> tuple2<T, T>::tuple2(PyObject *p) {
    if(!PyTuple_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (tuple expected)"));

    this->__class__ = cl_tuple;
    int size = PyTuple_Size(p);
    for(int i=0; i<size; i++)
        this->units.push_back(__to_ss<T>(PyTuple_GetItem(p, i)));
}

template<class T> PyObject *tuple2<T, T>::__to_py__() {
    int len = this->__len__();
    PyObject *p = PyTuple_New(len);
    for(int i=0; i<len; i++)
        PyTuple_SetItem(p, i, __to_py(this->__getitem__(i)));
    return p;
}
#endif

/* tuple2 methods (binary) */

template<class A, class B> void tuple2<A, B>::__init2__(A a, B b) {
    first = a;
    second = b;
}

template<class A, class B> tuple2<A, B>::tuple2() {
    this->__class__ = cl_tuple;
}

template<class A, class B> tuple2<A, B>::tuple2(int, A a, B b) {
    this->__class__ = cl_tuple;
    first = a;
    second = b;
}

template<class A, class B> A tuple2<A, B>::__getfirst__() {
    return first;
}
template<class A, class B> B tuple2<A, B>::__getsecond__() {
    return second;
}

template<class A, class B> __ss_int tuple2<A, B>::__len__() {
    return 2;
}

template<class A, class B> __ss_bool tuple2<A, B>::__eq__(pyobj *p) {
    tuple2<A,B> *b = (tuple2<A,B> *)p;
    return __mbool(__eq(first, b->__getfirst__()) & __eq(second, b->__getsecond__()));
}

template<class A, class B> __ss_int tuple2<A, B>::__cmp__(pyobj *p) {
    if (!p) return 1;
    tuple2<A,B> *b = (tuple2<A,B> *)p;
    if(int c = __cmp(first, b->first)) return c;
    return __cmp(second, b->second);
}

template<class A, class B> long tuple2<A, B>::__hash__() {
    long seed = 0;
    seed = hash_combine(seed, hasher<A>(first));
    seed = hash_combine(seed, hasher<B>(second));
    return seed;
}

template<class A, class B> str *tuple2<A, B>::__repr__() {
    __GC_STRING s = "(";
    s += repr(first)->c_str();
    s += ", ";
    s += repr(second)->c_str();
    s += ")";
    return new str(s);
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

#ifdef __SS_BIND
template<class A, class B> tuple2<A, B>::tuple2(PyObject *p) {
    if(!PyTuple_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (tuple expected)"));

    this->__class__ = cl_tuple;
    first = __to_ss<A>(PyTuple_GetItem(p, 0));
    second = __to_ss<B>(PyTuple_GetItem(p, 1));
}

template<class A, class B> PyObject *tuple2<A, B>::__to_py__() {
    PyObject *p = PyTuple_New(2);
    PyTuple_SetItem(p, 0, __to_py(first));
    PyTuple_SetItem(p, 1, __to_py(second));
    return p;
}
#endif
