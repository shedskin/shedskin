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

    array(str *typecode, pyiter<T> *it=NULL) {
        this->__class__ = cl_array;
        __init__(typecode, it);
    }
    void *__init__(str *typecode, pyiter<T> *arg);
    list<T> *tolist();
    str *tostring();
    void *extend(pyiter<T> *arg);
    void *fromlist(list<T> *l);
    void *fromstring(str *s);

    __ss_int __len__();
    T __getitem__(__ss_int i);
    str *__repr__();
};

extern void * default_0;

void __init();

} // module namespace
#endif
