#ifndef __ARRAY_HPP
#define __ARRAY_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __array__ {

extern str *const_0;

class array;

extern str *__name__;

extern class_ *cl_array;
class array : public pyobj {
public:
    list<__ss_int> *unit;

    array() {}
    array(str *flags, list<__ss_int> *arg=NULL) {
        this->__class__ = cl_array;
        __init__(flags, arg);
    }
    void *fromlist(list<__ss_int> *l);
    list<__ss_int> *tolist();
    void *fromstring(str *s);
    void *tofile(file *f);
    str *tostring();
    __ss_int __len__();
    array *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    void *fromfile(file *f, __ss_int n);
    void *__init__(str *flags, list<__ss_int> *arg);
    void *__delete__(__ss_int x, __ss_int a, __ss_int b, __ss_int s);
    void *__setitem__(__ss_int i, __ss_int e);
    str *__repr__();
};

extern void * default_0;

void __init();

} // module namespace
#endif
