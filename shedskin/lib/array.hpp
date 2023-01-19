/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __ARRAY_HPP
#define __ARRAY_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __array__ {

extern str *const_0;
extern str *__name__;
extern void *buffy;

unsigned int get_itemsize(char typechar);

extern class_ *cl_array;
template <class T> class array : public pyseq<T> {
public:
    __GC_VECTOR(char) units; /* XXX no pointers, so avoid GC */
    str *typecode;
    char typechar;
    unsigned int itemsize;

    array(str *typecode) {
        this->__class__ = cl_array;
        this->typecode = typecode;
        this->typechar = typecode->unit[0];
        this->itemsize = get_itemsize(typechar);
    }

    template<class U> array(str *typecode, U *iter) { /* XXX iter with type None */
        this->__class__ = cl_array;
        __init__(typecode, iter);
    }

    template<class U> void *__init__(str *typecode, U *iter);

    template<class U> void *extend(U *iter);
    template<class U> void *fromlist(U *iter);
    void *fromstring(str *s);
    void *fromstring(bytes *s);
    void *frombytes(bytes *b);

    list<T> *tolist();
    bytes *tostring();
    bytes *tobytes();

    T __getitem__(__ss_int i);
    T __getfast__(__ss_int i);
    void *__setitem__(__ss_int i, T t);
    void *__delitem__(__ss_int i);

    void *append(T t);
    void *insert(__ss_int i, T t);

    __ss_bool __eq__(pyobj *p);

    array<T> *__mul__(__ss_int i);
    array<T> *__imul__(__ss_int i);
    array<T> *__add__(array<T> *a);
    array<T> *__iadd__(array<T> *a);

    __ss_int count(T t);
    __ss_int index(T t);

    void *remove(T t);
    T pop(__ss_int i=-1);

    __ss_int __len__();
    str *__repr__();

    void *reverse();
    void *byteswap();

    void *tofile(file_binary *f);
    void *fromfile(file_binary *f, __ss_int n);

    void fillbuf(T t);

    array<T> *__copy__();
    array<T> *__deepcopy__(dict<void *, pyobj *> *memo);

    array<T> *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    void *__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, array<T> *b);
    void *__delete__(__ss_int i);
    void *__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    void *__delslice__(__ss_int a, __ss_int b);
};

template<class T> template<class U> void *array<T>::__init__(str *typecode, U *iter) {
    this->typecode = typecode;
    this->typechar = typecode->unit[0];
    this->itemsize = get_itemsize(typechar);
    this->extend(iter);
    return NULL;
}

template<class T> template<class U> void *array<T>::extend(U *iter) {
    if(iter->__class__ == cl_array) {
        array<T> *arr = (array<T> *)iter;
        size_t s1 = this->units.size();
        size_t s2 = arr->units.size();
        this->units.resize(s1+s2);
        memcpy(&(this->units[s1]), &(arr->units[0]), s2);
    } else {
        typename U::for_in_unit e;
        typename U::for_in_loop __3;
        int __2;
        U *__1;
        FOR_IN(e,iter,1,2,3)
            this->append(e);
        END_FOR
    }
    return NULL;
}
template<> template<> void *array<int>::extend(list<__ss_int> *l);
template<> template<> void *array<str *>::extend(bytes *s);

template<class T> template<class U> void *array<T>::fromlist(U *iter) {
    extend(iter);
    return NULL;
}

template<class T> bytes *array<T>::tostring() {
    return tobytes();
}

template<class T> bytes *array<T>::tobytes() {
    bytes *s = new bytes();
    size_t s1 = this->units.size();
    s->unit.resize(s1);
    memcpy(&(s->unit[0]), &(this->units[0]), s1);
    return s;
}

template<class T> void *array<T>::fromstring(bytes *s) {
    frombytes(s);
    return NULL;
}

template<class T> void *array<T>::frombytes(bytes *s) {
    size_t len = s->size();
    if(len == 1)
        this->units.push_back(s->unit[0]);
    else {
        size_t s1 = this->units.size();
        this->units.resize(s1+len);
        memcpy(&(this->units[0]), &(s->unit[0]), len);
    }
    return NULL;
}

template<class T> list<T> *array<T>::tolist() {
    list<T> *l = new list<T>();
    size_t len = this->__len__();
    l->resize(len);
    for(size_t i=0; i<len; i++)
        l->units[i] = __getitem__(i);
    return l;
}

template<class T> __ss_int array<T>::__len__() {
    return units.size() / itemsize;
}

template<class T> __ss_bool array<T>::__eq__(pyobj *p) {
   if(p->__class__ != cl_array)
       return False;
   array<T> *b = (array<T> *)p;
   __ss_int len = this->__len__();
   if(b->__len__() != len)
       return False;
   if(this->typechar == b->typechar)
       return __mbool(memcmp(&(this->units[0]), &(b->units[0]), this->units.size()) == 0);
   for(__ss_int i=0; i<len; i++)
       if(!__eq(this->__getitem__(i), b->__getitem__(i)))
           return False;
   return True;
}

template<class T> array<T> *array<T>::__mul__(__ss_int n) {
    array<T> *a = new array<T>(typecode);
    size_t len = this->units.size();
    a->units.resize(len*n);
    for(size_t i=0; i<n; i++)
        memcpy(&(a->units[i*len]), &(this->units[0]), len);
    return a;
}

template<class T> array<T> *array<T>::__imul__(__ss_int n) {
    size_t len = this->units.size();
    this->units.resize(len*n);
    for(size_t i=1; i<n; i++)
        memcpy(&(this->units[i*len]), &(this->units[0]), len);
    return this;
}

template<class T> array<T> *array<T>::__add__(array<T> *b) {
    if(this->typecode != b->typecode)
        throw new TypeError(new str("bad argument type for built-in operation")); 
    array<T> *a = new array<T>(typecode);
    size_t s1 = this->units.size();
    size_t s2 = b->units.size();
    a->units.resize(s1+s2);
    memcpy(&(a->units[0]), &(this->units[0]), s1);
    memcpy(&(a->units[s1]), &(b->units[0]), s2);
    return a;
}

template<class T> array<T> *array<T>::__iadd__(array<T> *b) {
    if(this->typecode != b->typecode)
        throw new TypeError(new str("bad argument type for built-in operation")); 
    size_t s1 = this->units.size();
    size_t s2 = b->units.size();
    this->units.resize(s1+s2);
    memcpy(&(this->units[s1]), &(b->units[0]), s2);
    return this;
}

template<class T> __ss_int array<T>::count(T t) {
    __ss_int result = 0;
    size_t len = this->__len__();
    for(size_t i=0; i<len; i++)
        if(__eq(t, this->__getitem__(i)))
            result += 1;
    return result;
}
template<> __ss_int array<str *>::count(str *t);

template<class T> __ss_int array<T>::index(T t) {
    size_t len = this->__len__();
    for(size_t i=0; i<len; i++)
        if(__eq(t, this->__getitem__(i)))
            return i;
    throw new ValueError(new str("array.index(x): x not in list"));
}
template<> __ss_int array<str *>::index(str *t);

template<class T> void *array<T>::remove(T t) {
    this->pop(this->index(t));
    return NULL;
}

template<class T> T array<T>::pop(__ss_int i) {
    size_t len = this->__len__();
    if(len==0)
        throw new IndexError(new str("pop from empty list"));
    if(i<0) i = len+i;
    if(i<0 or i>=len)
        throw new IndexError(new str("pop index out of range"));
    T t = this->__getitem__(i);
    this->units.erase(this->units.begin()+(i*itemsize), this->units.begin()+((i+1)*itemsize));
    return t;
}

template<class T> void array<T>::fillbuf(T t) {
    switch(typechar) {
        case 'b': *((signed char *)buffy) = t; break;
        case 'B': *((unsigned char *)buffy) = t; break;
        case 'h': *((signed short *)buffy) = t; break;
        case 'H': *((unsigned short *)buffy) = t; break;
        case 'i': *((signed int *)buffy) = t; break;
        case 'I': *((unsigned int *)buffy) = t; break;
        case 'l': *((signed long *)buffy) = t; break;
        case 'L': *((unsigned long *)buffy) = t; break;
        case 'f': *((float *)buffy) = t; break;
        case 'd': *((double *)buffy) = t; break;
    }
}

template<class T> T array<T>::__getitem__(__ss_int i) {
    return __getfast__(i);
}

template<> inline __ss_int array<__ss_int>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    switch(typechar) {
        case 'b': return *((signed char *)(&units[i*itemsize]));
        case 'B': return *((unsigned char *)(&units[i*itemsize]));
        case 'h': return *((signed short *)(&units[i*itemsize]));
        case 'H': return *((unsigned short *)(&units[i*itemsize]));
        case 'i': return *((signed int *)(&units[i*itemsize]));
        case 'I': return *((unsigned int *)(&units[i*itemsize]));
        case 'l': return *((signed long *)(&units[i*itemsize]));
        case 'L': return *((unsigned long *)(&units[i*itemsize]));
    }
    return 0;
}
template<> inline str *array<str *>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return __char_cache[(unsigned char)units[i]];
}
template<> inline double array<double>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    if(typechar == 'f')
        return *((float *)(&units[i*itemsize]));
    else
        return *((double *)(&units[i*itemsize]));
}

template<class T> void *array<T>::append(T t) {
    fillbuf(t);
    for(unsigned int i=0; i<itemsize; i++)
        units.push_back(((char *)buffy)[i]);
    return NULL;
}
template<> void *array<str *>::append(str *t);

template<class T> void *array<T>::__setitem__(__ss_int i, T t) {
    i = __wrap(this, i);
    fillbuf(t);
    for(unsigned int j=0; j<itemsize; j++)
        this->units[i*itemsize+j] = ((char *)buffy)[j];
    return NULL;
}
template<> void *array<str *>::__setitem__(__ss_int i, str *t);

template<class T> void *array<T>::insert(__ss_int i, T t) {
    i = __wrap(this, i);
    this->units.insert(this->units.begin()+(i*itemsize), itemsize, '\0');
    this->__setitem__(i, t);
    return NULL;
}

template<class T> void *array<T>::__delitem__(__ss_int i) {
    i = __wrap(this, i);
    this->units.erase(units.begin()+(i*itemsize), units.begin()+((i+1)*itemsize));
    return NULL;
}

template<class T> str *array<T>::__repr__() {
    return __add_strs(5, new str("array('"), typecode, new str("', "), repr(tolist()), new str(")"));
}
template<> str *array<str *>::__repr__();

template<class T> void *array<T>::reverse() { /* use fillbuf, __setitem__ or standard C function? */
    size_t len = this->__len__();
    if(len > 1) {
        char *first = &units[0];
        char *second = &units[(len-1)*itemsize];
        for(size_t i=0; i<len/2; i++) {
            memcpy(buffy, first, itemsize);
            memcpy(first, second, itemsize);
            memcpy(second, buffy, itemsize);
            first += itemsize; 
            second -= itemsize;
        }
    }
    return NULL;
}

template<class T> void *array<T>::byteswap() { /* standard C function? */
    size_t len = this->__len__();
    for(size_t i=0; i<len; i++) {
        char *first = &units[i*itemsize];
        char *second = &units[((i+1)*itemsize)-1];
        for(unsigned int j=0; j<itemsize/2; j++) {
            char tmp = *first;
            *first = *second;
            *second = tmp;
            first++;
            second--;
        }
    }
    return NULL;
}

template<class T> void *array<T>::tofile(file_binary *f) {
    f->write(this->tostring());
    return NULL;
}

template<class T> void *array<T>::fromfile(file_binary *f, __ss_int n) {
    bytes *s = f->read(n*itemsize);
    size_t len = s->__len__();
    size_t bytes = (len/itemsize)*itemsize;
    for(size_t i=0; i<bytes; i++)
        units.push_back(s->unit[i]);
    if (len < n*itemsize)
        throw new EOFError(new str("read() didn't return enough bytes"));
    return NULL;
}

template<class T> array<T> *array<T>::__copy__() {
    array<T> *a = new array<T>(this->typecode);
    a->units = this->units;
    return a;
}

template<class T> array<T> *array<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    return this->__copy__();
}

template<class T> array<T> *array<T>::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    array<T> *c = new array<T>(typecode);
    slicenr(x, l, u, s, this->__len__());
    if(s == 1) {
        c->units.resize((u-l)*itemsize);
        memcpy(&(c->units[0]), &(this->units[l*itemsize]), (u-l)*itemsize);
    } else if(s > 0)
        for(int i=l; i<u; i += s)
            for(int j=0; j<itemsize; j++)
                c->units.push_back(units[i*itemsize+j]);
    else
        for(int i=l; i>u; i += s)
            for(int j=0; j<itemsize; j++)
                c->units.push_back(units[i*itemsize+j]);
    return c;
}

/* XXX optimize XXX */

template<class T> void *array<T>::__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, array<T> *b) {
    list<T> *l2 = this->tolist();
    l2->__setslice__(x, l, u, s, b->tolist());
    this->units.clear();
    this->fromlist(l2);
    return NULL;
}

template<class T> void *array<T>::__delete__(__ss_int i) {
    i = __wrap(this, i);
    this->units.erase(units.begin()+(i*itemsize), units.begin()+((i+1)*itemsize));
    return NULL;
}

/* XXX optimize XXX */

template<class T> void *array<T>::__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    list<T> *l2 = this->tolist();
    l2->__delete__(x, l, u, s);
    this->units.clear();
    this->fromlist(l2);
    return NULL;
}
template<class T> void *array<T>::__delslice__(__ss_int a, __ss_int b) {
    if(a>this->__len__()) return NULL;
    if(b>this->__len__()) b = this->__len__();
    units.erase(units.begin()+(a*itemsize),units.begin()+(b*itemsize));
    return NULL;
}

extern void * default_0;

void __init();

} // module namespace
#endif
