#ifndef __ARRAY_HPP
#define __ARRAY_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __array__ {

extern str *const_0;
extern str *__name__;
extern char buffy[];

int get_itemsize(str *typecode);

extern class_ *cl_array;
template <class T> class array : public pyseq<T> {
public:
    __GC_VECTOR(char) units; /* XXX no pointers, so avoid GC */
    str *typecode;
    __ss_int itemsize;

    array(str *typecode) {
        this->__class__ = cl_array;
        this->typecode = typecode;
        this->itemsize = get_itemsize(typecode);
    }

    template<class U> array(str *typecode, U *iter) { /* XXX iter with type None */
        this->__class__ = cl_array;
        __init__(typecode, iter);
    }

    template<class U> void *__init__(str *typecode, U *iter);

    template<class U> void *extend(U *iter);
    template<class U> void *fromlist(U *iter);

    list<T> *tolist();
    str *tostring();
    void *append(T t);
    void *fromstring(str *s);

    __ss_int __len__();
    T __getitem__(__ss_int i);
    __ss_bool __eq__(pyobj *p);

    array<T> *__mul__(__ss_int i);
    array<T> *__imul__(__ss_int i);
    array<T> *__add__(array<T> *a);
    array<T> *__iadd__(array<T> *a);

    __ss_int count(T t);
    __ss_int index(T t);

    str *__repr__();

    void fillbuf(T t);
};

template<class T> template<class U> void *array<T>::__init__(str *typecode, U *iter) {
    this->typecode = typecode;
    this->itemsize = get_itemsize(typecode);
    this->extend(iter);
    return NULL;
}

template<class T> template<class U> void *array<T>::extend(U *iter) { /* array? memcpy */
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        this->append(e);
    END_FOR
    return NULL;
}

template<class T> template<class U> void *array<T>::fromlist(U *iter) {
    extend(iter);
    return NULL;
}

template<class T> str *array<T>::tostring() { /* memcpy */
    str *s = new str();
    for(unsigned int i=0;i<units.size(); i++)
        s->unit += units[i];
    return s;
}

template<class T> void *array<T>::fromstring(str *s) { /* memcpy */
    int len = s->unit.size();
    for(unsigned int i=0;i<len; i++)
        units.push_back(s->unit[i]);
    return NULL;
}

template<class T> list<T> *array<T>::tolist() {
    list<T> *l = new list<T>();
    int len = __len__();
    for(unsigned int i=0;i<len; i++)
        l->units.push_back(__getitem__(i));
    return l;
}

template<class T> __ss_int array<T>::__len__() {
    return units.size() / itemsize;
}

template<class T> __ss_bool array<T>::__eq__(pyobj *p) { /* strncmp */
   if(p->__class__ != cl_array)
       return False;
   array<T> *b = (array<T> *)p;
   unsigned int len = this->__len__();
   if(b->__len__() != len)
       return False;
   for(unsigned int i = 0; i < len; i++)
       if(!__eq(this->__getitem__(i), b->__getitem__(i)))
           return False;
   return True;
}

template<class T> array<T> *array<T>::__mul__(__ss_int n) { /* memcpy */
    array<T> *a = new array<T>(typecode);
    int len = this->units.size();
    for(unsigned int i=0; i<n; i++)
        for(unsigned int j=0;j<len; j++)
            a->units.push_back(this->units[j]);
    return a;
}

template<class T> array<T> *array<T>::__imul__(__ss_int n) { /* memcpy */
    int len = this->units.size();
    for(unsigned int i=0; i<n-1; i++)
        for(unsigned int j=0;j<len; j++)
            this->units.push_back(this->units[j]);
    return this;
}

template<class T> array<T> *array<T>::__add__(array<T> *b) { /* memcpy */
    array<T> *a = new array<T>(typecode);
    int len = this->units.size();
    for(unsigned int j=0;j<len; j++)
        a->units.push_back(this->units[j]);
    len = b->units.size();
    for(unsigned int j=0;j<len; j++)
        a->units.push_back(b->units[j]);
    return a;
}

template<class T> array<T> *array<T>::__iadd__(array<T> *b) { /* memcpy */
    int len = b->units.size();
    for(unsigned int j=0;j<len; j++)
        this->units.push_back(b->units[j]);
    return this;
}

template<class T> __ss_int array<T>::count(T t) {
    __ss_int result = 0;
    int len = this->__len__();
    for(unsigned int i=0;i<len; i++)
        if(__eq(t, this->__getitem__(i)))
            result += 1;
    return result;
}

template<class T> __ss_int array<T>::index(T t) {
    int len = this->__len__();
    for(unsigned int i=0;i<len; i++)
        if(__eq(t, this->__getitem__(i)))
            return i;
    throw new ValueError(new str("array.index(x): x not in list"));
}

template<class T> void array<T>::fillbuf(T t) {
    switch(typecode->unit[0]) {
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

template<> __ss_int array<__ss_int>::__getitem__(__ss_int i);
template<> str *array<str *>::__getitem__(__ss_int i);
template<> double array<double>::__getitem__(__ss_int i);

template<> void *array<__ss_int>::append(__ss_int t);
template<> void *array<str *>::append(str * t);
template<> void *array<double>::append(double t);

template<> str *array<__ss_int>::__repr__();
template<> str *array<str *>::__repr__();
template<> str *array<double>::__repr__();

extern void * default_0;

void __init();

} // module namespace
#endif
