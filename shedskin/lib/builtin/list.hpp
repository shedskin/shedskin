/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

/* list methods */

template<class T> list<T>::list() {
    this->__class__ = cl_list;
}

template<class T> list<T>::list(int count, ...) {
    this->__class__ = cl_list;
    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        T t = va_arg(ap, T);
        this->units.push_back(t);
    }
    va_end(ap);
}

template<class T> template<class U> list<T>::list(U *iter) {
    this->__class__ = cl_list;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        this->units.push_back(e);
    END_FOR
}

template<class T> list<T>::list(list<T> *p) {
    this->__class__ = cl_list;
    this->units = p->units;
}

template<class T> list<T>::list(tuple2<T, T> *p) {
    this->__class__ = cl_list;
    this->units = p->units;
}

template<class T> list<T>::list(str *s) {
    this->__class__ = cl_list;
    this->units.resize(len(s));
    size_t sz = s->size();
    for(size_t i=0; i<sz; i++)
        this->units[i] = __char_cache[((unsigned char)(s->unit[i]))];
}

#ifdef __SS_BIND
template<class T> list<T>::list(PyObject *p) {
    if(!PyList_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (list expected)"));

    this->__class__ = cl_list;
    size_t size = PyList_Size(p);
    for(size_t i=0; i<size; i++)
        append(__to_ss<T>(PyList_GetItem(p, i)));
}

template<class T> PyObject *list<T>::__to_py__() {
    int len = this->__len__();
    PyObject *p = PyList_New(len);
    for(int i=0; i<len; i++)
        PyList_SetItem(p, i, __to_py(this->__getitem__(i)));
    return p;
}
#endif

template<class T> void list<T>::clear() {
    units.resize(0);
}

template<class T> void list<T>::resize(__ss_int i) {
    units.resize(i);
}

template<class T> __ss_int list<T>::__len__() {
    return units.size();
}

template<class T> T list<T>::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return units[i];
}

template<class T> __ss_bool list<T>::__eq__(pyobj *p) {
   list<T> *b = (list<T> *)p;
   unsigned int len = this->units.size();
   if(b->units.size() != len) return False;
   for(unsigned int i = 0; i < len; i++)
       if(!__eq(this->units[i], b->units[i]))
           return False;
   return True;
}

template<class T> void *list<T>::append(T a) {
    this->units.push_back(a);
    return NULL;
}

template<class T> template<class U> void *list<T>::extend(U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN(e,iter,1,2,3)
        this->units.push_back(e);
    END_FOR
    return NULL;
}

template<class T> void *list<T>::extend(list<T> *p) {
    int l1, l2;
    l1 = this->__len__(); l2 = p->__len__();
    this->units.resize(l1+l2);
    memcpy(&(this->units[l1]), &(p->units[0]), sizeof(T)*l2);
    return NULL;
}
template<class T> void *list<T>::extend(tuple2<T,T> *p) {
    int l1, l2;
    l1 = this->__len__(); l2 = p->__len__();
    this->units.resize(l1+l2);
    memcpy(&(this->units[l1]), &(p->units[0]), sizeof(T)*l2);
    return NULL;
}

template<class T> void *list<T>::extend(str *s) {
    size_t sz = s->size();
    for(size_t i=0; i<sz; i++)
        this->units.push_back(__char_cache[((unsigned char)(s->unit[i]))]);
    return NULL;
}

template<class T> inline T list<T>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return this->units[i];
}

template<class T> void *list<T>::__setitem__(__ss_int i, T e) {
    i = __wrap(this, i);
    units[i] = e;
    return NULL;
}

template<class T> void *list<T>::__delitem__(__ss_int i) {
    i = __wrap(this, i);
    units.erase(units.begin()+i,units.begin()+i+1);
    return NULL;
}

template<class T> int list<T>::empty() {
    return units.empty();
}

template<class T> list<T> *list<T>::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    list<T> *c = new list<T>();
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

template<class T> void *list<T>::__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, pyiter<T> *b) {
    list<T> *la = new list<T>(); /* XXX avoid intermediate list */
    typename pyiter<T>::for_in_unit e;
    typename pyiter<T>::for_in_loop __3;
    int __2;
    pyiter<T> *__1;
    FOR_IN(e,b,1,2,3)
        la->units.push_back(e);
    END_FOR
    this->__setslice__(x, l, u, s, la);
    return NULL;
}

template<class T> void *list<T>::__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, list<T> *la) {
    slicenr(x, l, u, s, this->__len__());

    if(x&4 && s != 1) { // x&4: extended slice (step 's' is given), check if sizes match
        int slicesize;
        if(l == u) slicesize = 0; // XXX ugly
        else if(s > 0 && u < l) slicesize=0;
        else if(s < 0 && l < u) slicesize=0;
        else {
            int slicelen = std::abs(u-l);
            int absstep = std::abs(s);
            slicesize = slicelen/absstep;
            if(slicelen%absstep) slicesize += 1;
        }

        if(slicesize != len(la))
            throw new ValueError(__modtuple(new str("attempt to assign sequence of size %d to extended slice of size %d"), new tuple2<__ss_int,__ss_int>(2, len(la), (__ss_int)slicesize)));
    }

    if(s == 1) {
        if(l <= u) {
            this->units.erase(this->units.begin()+l, this->units.begin()+u);
            this->units.insert(this->units.begin()+l, la->units.begin(), la->units.end());
        } else
            this->units.insert(this->units.begin()+l, la->units.begin(), la->units.end());
    }
    else {
        int i, j;
        if(s > 0)
            for(i = 0, j = l; j < u; i++, j += s)
                this->units[j] = la->units[i];
        else
            for(i = 0, j = l; j > u; i++, j += s)
                this->units[j] = la->units[i];
    }

    return NULL;
}

template<class T> void *list<T>::__delete__(__ss_int i) {
    i = __wrap(this, i);
    units.erase(units.begin()+i,units.begin()+i+1);
    return NULL;
}

template<class T> void *list<T>::__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    slicenr(x, l, u, s, this->__len__());

    if(s == 1)
        __delslice__(l, u);
    else {
        __GC_VECTOR(T) v;
        for(__ss_int i=0; i<this->__len__();i++)
            if(i < l or i >= u or (i-l)%s)
                v.push_back(this->units[i]);
        units = v;
    }
    return NULL;
}

template<class T> void *list<T>::__delslice__(__ss_int a, __ss_int b) {
    if(a>this->__len__()) return NULL;
    if(b>this->__len__()) b = this->__len__();
    units.erase(units.begin()+a,units.begin()+b);
    return NULL;
}

template<class T> __ss_bool list<T>::__contains__(T a) {
    size_t size = this->units.size();
    for(size_t i=0; i<size; i++)
        if(__eq(this->units[i], a))
            return True;
    return False;
}

template<class T> list<T> *list<T>::__add__(list<T> *b) {
    int l1 = this->__len__();
    int l2 = b->__len__();

    list<T> *c = new list<T>();
    c->units.resize(l1+l2);

    if(l1==1) c->units[0] = this->units[0];
    else memcpy(&(c->units[0]), &(this->units[0]), sizeof(T)*l1);
    if(l2==1) c->units[l1] = b->units[0];
    else memcpy(&(c->units[l1]), &(b->units[0]), sizeof(T)*l2);

    return c;
}

template<class T> list<T> *list<T>::__mul__(__ss_int b) {
    list<T> *c = new list<T>();
    if(b<=0) return c;
    __ss_int len = this->units.size();
    if(len==1)
        c->units.assign(b, this->units[0]);
    else {
        c->units.resize(b*len);
        for(__ss_int i=0; i<b; i++)
            memcpy(&(c->units[i*len]), &(this->units[0]), sizeof(T)*len);
    }
    return c;
}

template<class T> list<T> *list<T>::__copy__() {
    list<T> *c = new list<T>();
    c->units = this->units;
    return c;
}

template<class T> list<T> *list<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    list<T> *c = new list<T>();
    memo->__setitem__(this, c);
    c->units.resize(this->__len__());
    for(__ss_int i=0; i<this->__len__(); i++)
        c->units[i] = __deepcopy(this->units[i], memo);
    return c;
}

template<class T> template<class U> list<T> *list<T>::__iadd__(U *iter) {
    extend(iter);
    return this;
}

template<class T> list<T> *list<T>::__imul__(__ss_int n) {
    __ss_int l1 = this->__len__();
    this->units.resize(l1*n);
    for(__ss_int i = 1; i <= n-1; i++)
        memcpy(&(this->units[l1*i]), &(this->units[0]), sizeof(T)*l1);
    return this;
}

template<class T> __ss_int list<T>::index(T a) { return index(a, 0, this->__len__()); }
template<class T> __ss_int list<T>::index(T a, __ss_int s) { return index(a, s, this->__len__()); }
template<class T> __ss_int list<T>::index(T a, __ss_int s, __ss_int e) {
    __ss_int one = 1;
    slicenr(7, s, e, one, this->__len__());
    for(__ss_int i = s; i<e;i++)
        if(__eq(a,units[i]))
            return i;
    throw new ValueError(new str("list.index(x): x not in list"));
}

template<class T> __ss_int list<T>::count(T a) {
    __ss_int c = 0;
    __ss_int len = this->__len__();
    for(__ss_int i = 0; i<len;i++)
        if(__eq(a,units[i]))
            c++;
    return c;
}

template<class T> str *list<T>::__repr__() {
    str *r = new str("[");
    int len = this->__len__();
    for(__ss_int i = 0; i<len;i++) {
        *r += repr(units[i])->c_str();
        if (i<len-1)
            *r += ", ";
    }
    *r += "]";
    return r;
}

template<class T> T list<T>::pop(int i) { /* XXX optimize */
    int len = this->__len__();
    if(len==0)
        throw new IndexError(new str("pop from empty list"));
    if(i<0) 
        i = len+i;
    if(i<0 or i>=len)
        throw new IndexError(new str("pop index out of range"));
    T e = units[i];
    units.erase(units.begin()+i);
    return e;
}

template<class T> T list<T>::pop() {
    if(this->units.size()==0)
        throw new IndexError(new str("pop from empty list"));
    T e = units.back();
    units.pop_back();
    return e;
}

template<class T> void *list<T>::reverse() {
    std::reverse(this->units.begin(), this->units.end());
    return NULL;
}

template<class T> template <class U> void *list<T>::sort(__ss_int (*cmp)(T, T), U (*key)(T), __ss_int reverse) {
    if(key) {
        if(reverse)
            std::sort(units.begin(), units.end(), cpp_cmp_key_rev<T, U>(key));
        else
            std::sort(units.begin(), units.end(), cpp_cmp_key<T, U>(key));
    }
    else if(cmp) {
        if(reverse)
            std::sort(units.begin(), units.end(), cpp_cmp_custom_rev<T>(cmp));
        else
            std::sort(units.begin(), units.end(), cpp_cmp_custom<T>(cmp));
    } else {
        if(reverse)
            std::sort(units.begin(), units.end(), cpp_cmp_rev<T>);
        else
            std::sort(units.begin(), units.end(), cpp_cmp<T>);
    }

    return NULL;
}

template<class T> template <class U> void *list<T>::sort(__ss_int cmp, U (*key)(T), __ss_int reverse) {
    return sort((__ss_int(*)(T,T))0, key, reverse);
}
template<class T> void *list<T>::sort(__ss_int (*cmp)(T, T), __ss_int, __ss_int reverse) {
    return sort(cmp, (__ss_int(*)(T))0, reverse);
}
template<class T> void *list<T>::sort(__ss_int, __ss_int, __ss_int reverse) {
    return sort((__ss_int(*)(T,T))0, (__ss_int(*)(T))0, reverse);
}

template<class T> void *list<T>::insert(int m, T e) {
    int len = this->__len__();
    if (m<0) m = len+m;
    if (m<0) m = 0;
    if (m>=len) m = len;
    units.insert(units.begin()+m, e);
    return NULL;
}

template<class T> void *list<T>::remove(T e) {
    for(int i = 0; i < this->__len__(); i++)
        if(__eq(units[i], e)) {
            units.erase(units.begin()+i);
            return NULL;
        }
    throw new ValueError(new str("list.remove(x): x not in list"));
}
template<class T> template <class U> void *list<T>::remove(U e) {
    throw new ValueError(new str("list.remove(x): x not in list"));
}

template<class T> inline bool list<T>::for_in_has_next(size_t i) {
    return i < units.size(); /* XXX opt end cond */
}

template<class T> inline T list<T>::for_in_next(size_t &i) {
    return units[i++];
}
