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
    list<int> *unit;

    array() {}
    array(str *flags, list<int> *arg=NULL) {
        this->__class__ = cl_array;
        __init__(flags, arg);
    }
    void *fromlist(list<int> *l);
    list<int> *tolist();
    void *fromstring(str *s);
    void *tofile(file *f);
    str *tostring();
    int __len__();
    array *__slice__(int x, int l, int u, int s);
    void *fromfile(file *f, int n);
    void *__init__(str *flags, list<int> *arg);
    void *__delete__(int x, int a, int b, int s);
    void *__setitem__(int i, int e);
    str *__repr__();
};

extern void * default_0;

void __init();

} // module namespace
#endif
