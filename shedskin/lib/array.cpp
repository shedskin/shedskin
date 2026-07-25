/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#include "array.hpp"

namespace __array__ {

str *__name__;
class_ *cl_array;
str *typecodes;

void *buffy;

void __throw_no_char() {
    throw new TypeError(new str("array item must be char"));
}

size_t get_itemsize(char typechar) {
    switch(typechar) {
        case 'b': return sizeof(signed char);
        case 'B': return sizeof(unsigned char);
        case 'h': return sizeof(signed short);
        case 'H': return sizeof(unsigned short);
        case 'i': return sizeof(signed int);
        case 'I': return sizeof(unsigned int);
        case 'l': return sizeof(signed long);
        case 'L': return sizeof(unsigned long);
        case 'q': return sizeof(signed long long);
        case 'Q': return sizeof(unsigned long long);
        case 'f': return sizeof(float);
        case 'd': return sizeof(double);
    }
    throw new TypeError(new str("must be char, not str"));
}

template<> template<> void *array<__ss_int>::extend(list<__ss_int> *l) {
    size_t len = l->units.size();
    size_t pos = this->units.size();
    this->units.resize(pos+len*itemsize);
    switch(typechar) {
        /* NOTE: bounds must match fillbuf() in array.hpp exactly, or append()
         * and extend()/fromlist()/the list-constructor will silently disagree
         * about which values are valid for a given typecode. */
        case 'b': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t > 127) throw new OverflowError(new str("signed char is greater than maximum")); if(t < -128) throw new OverflowError(new str("signed char is less than minimum")); *((signed char *)(&this->units[pos+i*itemsize])) = (signed char)t; } break;
        case 'B': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t < 0) throw new OverflowError(new str("unsigned byte integer is less than minimum")); if(t > 255) throw new OverflowError(new str("unsigned byte integer is greater than maximum")); *((unsigned char *)(&this->units[pos+i*itemsize])) = (unsigned char)t; } break;
        case 'h': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t > 32767) throw new OverflowError(new str("signed short integer is greater than maximum")); if(t < -32768) throw new OverflowError(new str("signed short integer is less than minimum")); *((signed short *)(&this->units[pos+i*itemsize])) = (signed short)t; } break;
        case 'H': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t < 0) throw new OverflowError(new str("unsigned short is less than minimum")); if(t > 65535) throw new OverflowError(new str("unsigned short is greater than maximum")); *((unsigned short *)(&this->units[pos+i*itemsize])) = (unsigned short)t; } break;
        case 'i': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t > 2147483647LL) throw new OverflowError(new str("signed integer is greater than maximum")); if(t < -2147483648LL) throw new OverflowError(new str("signed integer is less than minimum")); *((signed int *)(&this->units[pos+i*itemsize])) = (signed int)t; } break;
        case 'I': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t < 0) throw new OverflowError(new str("can't convert negative value to unsigned int")); if(t > 4294967295LL) throw new OverflowError(new str("unsigned int is greater than maximum")); *((unsigned int *)(&this->units[pos+i*itemsize])) = (unsigned int)t; } break;
        case 'l': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t > std::numeric_limits<signed long>::max()) throw new OverflowError(new str("signed long is greater than maximum")); if(t < std::numeric_limits<signed long>::min()) throw new OverflowError(new str("signed long is less than minimum")); *((signed long *)(&this->units[pos+i*itemsize])) = (signed long)t; } break;
        case 'L': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t < 0) throw new OverflowError(new str("can't convert negative value to unsigned long")); if((unsigned long long)t > std::numeric_limits<unsigned long>::max()) throw new OverflowError(new str("unsigned long is greater than maximum")); *((unsigned long *)(&this->units[pos+i*itemsize])) = (unsigned long)t; } break;
        case 'q': for(size_t i=0; i<len; i++) *((signed long long *)(&this->units[pos+i*itemsize])) = (signed long long)l->units[i]; break;
        case 'Q': for(size_t i=0; i<len; i++) { __ss_int t = l->units[i]; if(t < 0) throw new OverflowError(new str("can't convert negative int to unsigned")); *((unsigned long long *)(&this->units[pos+i*itemsize])) = (unsigned long long)t; } break;
        case 'f': for(size_t i=0; i<len; i++) *((float *)(&this->units[pos+i*itemsize])) = (float)l->units[i]; break;
        case 'd': for(size_t i=0; i<len; i++) *((double *)(&this->units[pos+i*itemsize])) = (double)l->units[i]; break;
    }
    return NULL;
}

void __init() {
    __name__ = new str("array");
    cl_array = new class_("array");

    buffy = malloc(8);
    typecodes = new str("bBuwhHiIlLqQfd");
}

} // module namespace

