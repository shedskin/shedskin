/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "array.hpp"

namespace __array__ {

str *__name__;
void * default_0;
class_ *cl_array;
str *typecodes;

void *buffy;

void __throw_no_char() {
    throw new TypeError(new str("array item must be char"));
}

unsigned int get_itemsize(char typechar) {
    switch(typechar) {
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

template<> template<> void *array<int>::extend(list<__ss_int> *l) {
    size_t len = l->units.size();
    size_t pos = this->units.size();
    this->units.resize(pos+len*itemsize);
    switch(typechar) {
        case 'b': for(size_t i=0; i<len; i++) *((signed char *)(&this->units[pos+i*itemsize])) = (signed char)l->units[i]; break;
        case 'B': for(size_t i=0; i<len; i++) *((unsigned char *)(&this->units[pos+i*itemsize])) = (unsigned char)l->units[i]; break;
        case 'h': for(size_t i=0; i<len; i++) *((signed short *)(&this->units[pos+i*itemsize])) = (signed short)l->units[i]; break;
        case 'H': for(size_t i=0; i<len; i++) *((unsigned short *)(&this->units[pos+i*itemsize])) = (unsigned short)l->units[i]; break;
        case 'i': for(size_t i=0; i<len; i++) *((signed int *)(&this->units[pos+i*itemsize])) = (signed int)l->units[i]; break;
        case 'I': for(size_t i=0; i<len; i++) *((unsigned int *)(&this->units[pos+i*itemsize])) = (unsigned int)l->units[i]; break;
        case 'l': for(size_t i=0; i<len; i++) *((signed long *)(&this->units[pos+i*itemsize])) = (signed long)l->units[i]; break;
        case 'L': for(size_t i=0; i<len; i++) *((unsigned long *)(&this->units[pos+i*itemsize])) = (unsigned long)l->units[i]; break;
        case 'f': for(size_t i=0; i<len; i++) *((float *)(&this->units[pos+i*itemsize])) = (float)l->units[i]; break;
        case 'd': for(size_t i=0; i<len; i++) *((double *)(&this->units[pos+i*itemsize])) = (double)l->units[i]; break;
    }
    return NULL;
}

void __init() {
    __name__ = new str("array");
    cl_array = new class_("array");

    buffy = malloc(8);
    default_0 = NULL;
    typecodes = new str("bBuhHiIlLqQfd");
}

} // module namespace

