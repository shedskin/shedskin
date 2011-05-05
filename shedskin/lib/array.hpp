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
    __GC_VECTOR(char) units; /* XXX no pointers, so avoid GC */
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

template<class T> str *array<T>::tostring() {
    str *s = new str();
    for(unsigned int i=0;i<units.size(); i++)
        s->unit += units[i];
    return s;
}

template<class T> void *array<T>::fromlist(list<T> *l) {
    return NULL;
}

template<class T> void *array<T>::fromstring(str *s) {
    return NULL;
}

template<class T> __ss_int array<T>::__len__() {
    if(typecode->unit[0] == 'i')
        return units.size() >> 1;
    return 0;
}

template<> __ss_int array<__ss_int>::__getitem__(__ss_int i);
template<> str *array<str *>::__getitem__(__ss_int i);
template<> double array<double>::__getitem__(__ss_int i);

template<> void *array<__ss_int>::append(__ss_int t);
template<> void *array<str *>::append(str * t);
template<> void *array<double>::append(double t);

template<> list<__ss_int> *array<__ss_int>::tolist();
template<> list<str *> *array<str *>::tolist();
template<> list<double> *array<double>::tolist();

template<> str *array<__ss_int>::__repr__();
template<> str *array<str *>::__repr__();
template<> str *array<double>::__repr__();

extern void * default_0;

void __init();

} // module namespace
#endif
