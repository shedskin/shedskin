/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "array.hpp"

namespace __array__ {

str *__name__;
void * default_0;
class_ *cl_array;

void *buffy;

template<> str *array<str *>::__repr__() {
    return __add_strs(5, new str("array('"), typecode, new str("', "), repr(tostring()), new str(")"));
}

void __throw_no_char() {
    throw new TypeError(new str("array item must be char"));
}

template<> void *array<str *>::append(str *t) {
    if(t->unit.size() != 1)
        __throw_no_char();
    units.push_back(t->unit[0]);
    return NULL;
}

template<> void *array<str *>::__setitem__(__ss_int i, str *t) {
    if(t->unit.size() != 1)
        __throw_no_char();
    i = __wrap(this, i);
    units[i*itemsize] = t->unit[0];
    return NULL;
}

unsigned int get_itemsize(str *typecode) {
    char c = typecode->unit[0];
    switch(c) {
        case 'c': return sizeof(char);
        case 'b': return sizeof(signed char);
        case 'B': return sizeof(unsigned char);
        case 'h': return sizeof(signed short);
        case 'H': return sizeof(unsigned short);
        case 'i': return sizeof(signed int);
        case 'I': return sizeof(unsigned int);
        case 'l': return sizeof(signed long);
        case 'L': return sizeof(unsigned long);
        case 'f': return sizeof(float);
        case 'd': return sizeof(double);
    }
    throw new TypeError(new str("must be char, not str"));
}

template<> __ss_int array<str *>::count(str *t) { 
    if(len(t) != 1)
        return 0;
    return std::count(this->units.begin(), this->units.end(), t->unit[0]);
}

template<> __ss_int array<str *>::index(str *t) {
    if(len(t) == 1) {
        size_t len = this->__len__();
        char c = t->unit[0];
        for(size_t i=0; i<len; i++)
            if(units[i] == c)
                return i;
    }
    throw new ValueError(new str("array.index(x): x not in list"));
}

template<> template<> void *array<int>::extend(list<int> *l) { /* XXX generalize */
    size_t len = l->__len__();
    if(typecode->unit[0] != 'I') {
        for(size_t i=0; i<len; i++)
            append(l->units[i]);
    } else {
        this->units.resize(len*itemsize);
        for(size_t i=0; i<len; i++)
            *((unsigned int *)(&this->units[i*itemsize])) = l->units[i];
    }
    return NULL;
}
template<> template<> void *array<str *>::extend(str *s) {
    fromstring(s);
}

void __init() {
    __name__ = new str("array");
    cl_array = new class_("array");

    buffy = malloc(8);
    default_0 = NULL;
}

} // module namespace

