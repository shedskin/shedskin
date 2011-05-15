#include "array.hpp"

namespace __array__ {

str *__name__;
void * default_0;
class_ *cl_array;

char buffy[32];

template<> str *array<str *>::__repr__() {
    return __add_strs(5, new str("array('"), typecode, new str("', "), repr(tostring()), new str(")"));
}

template<> __ss_int array<__ss_int>::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    switch(typecode->unit[0]) {
        case 'b': return *((signed char *)(&units[i*itemsize]));
        case 'B': return *((unsigned char *)(&units[i*itemsize]));
        case 'h': return *((signed short *)(&units[i*itemsize]));
        case 'H': return *((unsigned short *)(&units[i*itemsize]));
        case 'i': return *((signed int *)(&units[i*itemsize]));
        case 'I': return *((unsigned int *)(&units[i*itemsize]));
        case 'l': return *((signed long *)(&units[i*itemsize]));
        case 'L': return *((unsigned long *)(&units[i*itemsize]));
    }
}
template<> str *array<str *>::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return __char_cache[(unsigned char)units[i]];
}
template<> double array<double>::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    if(typecode->unit[0] == 'f')
        return *((float *)(&units[i*itemsize]));
    else
        return *((double *)(&units[i*itemsize]));
}

template<> void *array<str *>::append(str *t) {
    if(len(t) != 1)
        throw new TypeError(new str("array item must be char"));
    units.push_back(t->unit[0]);
    return NULL;
}

template<> void *array<str *>::__setitem__(__ss_int i, str *t) {
    if(len(t) != 1)
        throw new TypeError(new str("array item must be char"));
    i = __wrap(this, i);
    units[i*itemsize] = t->unit[0];
    return NULL;
}

int get_itemsize(str *typecode) {
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
        int len = this->__len__();
        char c = t->unit[0];
        for(unsigned int i=0; i<len; i++)
            if(units[i] == c)
                return i;
    }
    throw new ValueError(new str("array.index(x): x not in list"));
}

void __init() {
    __name__ = new str("array");
    cl_array = new class_("array", 29, 29);

    default_0 = NULL;
}

} // module namespace

