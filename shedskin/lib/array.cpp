#include "array.hpp"

namespace __array__ {

str *__name__;
void * default_0;
class_ *cl_array;

char buffy[32];

template<> str *array<__ss_int>::__repr__() {
    return __add_strs(3, new str("array('i', "), repr(tolist()), new str(")"));
}
template<> str *array<str *>::__repr__() {
    return __add_strs(3, new str("array('c', "), repr(tostring()), new str(")"));
}
template<> str *array<double>::__repr__() {
    return NULL;
}

template<> list<__ss_int> *array<__ss_int>::tolist() {
    list<__ss_int> *l = new list<__ss_int>();
    for(unsigned int i=0; i<units.size(); i += itemsize)
        l->units.push_back(*((signed int *)(&units[i])));
    return l;
}
template<> list<str *> *array<str *>::tolist() {
    return NULL;
}
template<> list<double> *array<double>::tolist() {
    return NULL;
}

template<> void *array<__ss_int>::append(__ss_int t) {
    fillbuf(t);
    for(unsigned int i=0; i<itemsize; i++)
        units.push_back(buffy[i]);
    /* printf("na append\n");
    for(unsigned int i=0; i<units.size(); i++)
        printf("%d\n", units[i]); */
}

template<> void *array<str *>::append(str * t) {
    units.push_back(t->unit[0]);
}
template<> void *array<double>::append(double t) {
    fillbuf(t);
    for(unsigned int i=0; i<itemsize; i++)
        units.push_back(buffy[i]);
}

template<> __ss_int array<__ss_int>::__getitem__(__ss_int i) {
    return *((signed int *)(&units[i*itemsize]));
}
template<> str *array<str *>::__getitem__(__ss_int i) {
    return 0;
}
template<> double array<double>::__getitem__(__ss_int i) {
    return 0;
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
    return 0;
}

void __init() {
    __name__ = new str("array");
    cl_array = new class_("array", 29, 29);

    default_0 = NULL;
}

} // module namespace

