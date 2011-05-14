#include "array.hpp"

namespace __array__ {

str *__name__;
void * default_0;
class_ *cl_array;

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
    for(unsigned int i=0; i<units.size(); i += 2)
        l->units.push_back((units[i] << 8) | units[i+1]);
    return l;
}
template<> list<str *> *array<str *>::tolist() {
    return NULL;
}
template<> list<double> *array<double>::tolist() {
    return NULL;
}

template<> void *array<__ss_int>::append(__ss_int t) {
    units.push_back((t >> 8) & 0xff);
    units.push_back(t & 0xff);
}
template<> void *array<str *>::append(str * t) {
    units.push_back(t->unit[0]);
}
template<> void *array<double>::append(double t) {
    char s[sizeof(double)];
    *((double *)s) = t;
    for(unsigned int i=0; i<sizeof(double); i++)
        units.push_back(s[i]);
}

template<> __ss_int array<__ss_int>::__getitem__(__ss_int i) {
    return units[i << 1] << 8 | units[(i << 1)+1];
}
template<> str *array<str *>::__getitem__(__ss_int i) {
    return 0;
}
template<> double array<double>::__getitem__(__ss_int i) {
    return 0;
}

int get_itemsize(str *typecode) {
    return 8;
}

void __init() {
    __name__ = new str("array");
    cl_array = new class_("array", 29, 29);

    default_0 = NULL;
}

} // module namespace

