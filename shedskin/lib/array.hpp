#ifndef __ARRAY_HPP
#define __ARRAY_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __array__ {

extern str *const_0;
extern str *__name__;

extern class_ *cl_array;
template <class T> class array : public pyseq<T> {
public:
    __GC_VECTOR(T) units; /* XXX no pointers, so avoid GC */
    str *typecode;

    array(str *typecode) {
        this->__class__ = cl_array;
        this->typecode = typecode;
    }

    template<class U> array(str *typecode, U *iter) {
        this->__class__ = cl_array;
        __init__(typecode, iter);
    }

    template<class U> void *__init__(str *typecode, U *iter);
    template<class U> void *extend(U *iter);

    list<T> *tolist();
    str *tostring();
    void *append(T t);
    void *fromlist(list<T> *l);
    void *fromstring(str *s);
    __ss_int __len__();
    T __getitem__(__ss_int i);
    str *__repr__();
};

template<class T> template<class U> void *array<T>::__init__(str *typecode, U *iter) {
    this->typecode = typecode;
    if(iter)
        this->extend(iter);
    return NULL;
}

template<class T> template<class U> void *array<T>::extend(U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        this->append(e);
    END_FOR
    return NULL;
}

template<class T> list<T> *array<T>::tolist() {
    return new list<T>();
}

template<class T> str *array<T>::tostring() {
    return new str("beh");
}


template<class T> void *array<T>::append(T t) {
    return NULL;
}

template<class T> void *array<T>::fromlist(list<T> *l) {
    return NULL;
}

template<class T> void *array<T>::fromstring(str *s) {
    return NULL;
}

template<class T> __ss_int array<T>::__len__() {
    return 0;
}

template<class T> T array<T>::__getitem__(__ss_int i) {
    return NULL;
}

template<class T> str *array<T>::__repr__() {
    return new str("array");
}

extern void * default_0;

void __init();

} // module namespace
#endif
