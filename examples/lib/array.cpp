#include "array.hpp"

namespace __array__ {

str *const_0;

str *__name__;

void * default_0;

/**
class array
*/

class_ *cl_array;

void *array::fromlist(list<int> *l) {
    
    return NULL;
}

list<int> *array::tolist() {
    
    return (new list<int>(1, 1));
}

void *array::fromstring(str *s) {
    
    return NULL;
}

void *array::tofile(file *f) {
    
    return NULL;
}

str *array::tostring() {
    
    return const_0;
}

int array::__len__() {
    
    return 1;
}

array *array::__slice__(int x, int l, int u, int s) {
    
    return this;
}

void *array::fromfile(file *f, int n) {
    
    return NULL;
}

void *array::__init__(str *flags, list<int> *arg) {
    
    return NULL;
}

void *array::__delete__(int x, int a, int b, int s) {
    
    return NULL;
}

void __init() {
    const_0 = new str("");

    __name__ = new str("array");

    cl_array = new class_("array", 29, 29);

    default_0 = NULL;
}

} // module namespace

