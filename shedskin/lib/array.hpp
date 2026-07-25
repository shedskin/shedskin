/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __ARRAY_HPP
#define __ARRAY_HPP

#include "builtin.hpp"

using namespace __shedskin__;
namespace __array__ {

extern str *const_0;
extern str *__name__;
extern void *buffy;
extern str *typecodes;

size_t get_itemsize(char typechar);

extern class_ *cl_array;
template <class T> class array : public pyseq<T> {
public:
    __GC_VECTOR(char) units; /* XXX no pointers, so avoid GC */
    str *typecode;
    char typechar;
    size_t itemsize;

    array(str *typecode_) {
        this->__class__ = cl_array;
        typecode = typecode_;
        typechar = typecode_->unit[0];
        itemsize = get_itemsize(typechar);
    }

    template<class U> array(str *typecode_, U *iter) { /* XXX iter with type None */
        this->__class__ = cl_array;
        __init__(typecode_, iter);
    }

    template<class U> void *__init__(str *typecode_, U *iter);
    void *__init__(str *typecode_, bytes *b);

    template<class U> void *extend(U *iter);
    template<class U> void *fromlist(U *iter);
    void *fromstring(str *s);
    void *fromstring(bytes *s);
    void *frombytes(bytes *b);

    list<T> *tolist();
    bytes *tobytes();

    T __getitem__(__ss_int i);
    T __getfast__(__ss_int i);
    void *__setitem__(__ss_int i, T t);
    void *__delitem__(__ss_int i);

    void *append(T t);
    void *insert(__ss_int i, T t);

    __ss_bool __eq__(pyobj *p);

    array<T> *__mul__(__ss_int i);
    array<T> *__imul__(__ss_int i);
    array<T> *__add__(array<T> *a);
    array<T> *__iadd__(array<T> *a);

    __ss_int count(T t);
    __ss_int index(T t, __ss_int start=0);
    __ss_int index(T t, __ss_int start, __ss_int stop);

    void *remove(T t);
    T pop(__ss_int i=-1);

    void *clear();

    __ss_int __len__();
    str *__repr__();

    void *reverse();
    void *byteswap();

    void *tofile(file_binary *f);
    void *fromfile(file_binary *f, __ss_int n);

    void fillbuf(T t);

    array<T> *__copy__();
    array<T> *__deepcopy__(dict<void *, pyobj *> *memo);

    array<T> *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    void *__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, array<T> *b);
    void *__delete__(__ss_int i);
    void *__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    void *__delslice__(__ss_int a, __ss_int b);
};

template<class T> template<class U> void *array<T>::__init__(str *typecode_, U *iter) {
    typecode = typecode_;
    typechar = typecode_->unit[0];
    itemsize = get_itemsize(typechar);
    /* CPython special-cases this too: array(typecode, other_array) accepts an
     * array of a *different* typecode, treating it as a plain iterable of
     * values -- only the explicit extend()/fromlist() methods reject a
     * mismatched-typecode array with TypeError. Delegating straight to
     * extend() here would incorrectly apply that stricter check to the
     * constructor as well, so a differently-typed array is unpacked by hand
     * before falling back to extend() for the same-typecode/generic cases. */
    if(iter->__class__ == cl_array) {
        /* 'arr' is only used to read typechar below: that field sits at the
         * same offset in every array<T> specialization, so the cast is safe
         * for it. Elements themselves are read through 'iter' -- which,
         * unlike 'arr', keeps its real, compiler-inferred type U -- so that
         * __getitem__() resolves to the source array's own specialization
         * instead of reinterpreting its raw bytes under array<T>'s. */
        array<T> *arr = (array<T> *)iter;
        if(this->typechar != arr->typechar) {
            /* CPython rejects this combination too: a Python float has no
             * __index__, so assigning it into an int-typed array item raises
             * TypeError rather than truncating. An int source into a float-
             * typed target, or an int/float source into a same-kind target
             * of different width, remains a plain (possibly overflow-
             * checked) numeric conversion, same as CPython. */
            bool this_is_float = this->typechar == 'f' || this->typechar == 'd';
            bool src_is_float = arr->typechar == 'f' || arr->typechar == 'd';
            if(!this_is_float && src_is_float)
                throw new TypeError(new str("'float' object cannot be interpreted as an integer"));
            __ss_int n = iter->__len__();
            for(__ss_int i=0; i<n; i++)
                this->append(iter->__getitem__(i));
            return NULL;
        }
    }
    extend(iter);
    return NULL;
}

/* CPython special-cases the constructor: a bytes-like initializer is interpreted
 * directly as a raw buffer of machine values (like frombytes()). This does NOT
 * apply to extend()/fromlist(), which treat bytes/bytearray as an ordinary
 * iterable of small ints -- hence this is a separate, non-template overload
 * rather than something extend() itself should do. */
template<class T> void *array<T>::__init__(str *typecode_, bytes *b) {
    typecode = typecode_;
    typechar = typecode_->unit[0];
    itemsize = get_itemsize(typechar);
    frombytes(b);
    return NULL;
}

template<class T> template<class U> void *array<T>::extend(U *iter) {
    if(iter->__class__ == cl_array) {
        array<T> *arr = (array<T> *)iter;
        /* cl_array is a single shared class marker for *all* array
         * specializations, so this cast alone does not guarantee 'arr'
         * has the same typecode/itemsize as 'this' (e.g. an array('i', ...)
         * and an array('h', ...) both instantiate array<__ss_int> and reach
         * this branch). CPython rejects extending with a differently-typed
         * array; without this check the raw memcpy below silently
         * reinterprets the source bytes under the wrong itemsize and
         * corrupts the buffer. */
        if(this->typechar != arr->typechar)
            throw new TypeError(new str("can only extend with array of same kind"));
        size_t s1 = this->units.size();
        size_t s2 = arr->units.size();
        this->units.resize(s1+s2);
        if(s2) memcpy(&(this->units[s1]), &(arr->units[0]), s2);
    } else {
        typename U::for_in_unit e;
        typename U::for_in_loop __3;
        int __2;
        U *__1;
        FOR_IN(e,iter,1,2,3)
            this->append(e);
        END_FOR
    }
    return NULL;
}
template<> template<> void *array<__ss_int>::extend(list<__ss_int> *l);

template<class T> template<class U> void *array<T>::fromlist(U *iter) {
    extend(iter);
    return NULL;
}

template<class T> bytes *array<T>::tobytes() {
    bytes *s = new bytes();
    size_t s1 = this->units.size();
    s->unit.resize(s1);
    if(s1) memcpy(&(s->unit[0]), &(this->units[0]), s1);
    return s;
}

template<class T> void *array<T>::fromstring(bytes *s) {
    frombytes(s);
    return NULL;
}

template<class T> void *array<T>::frombytes(bytes *s) {
    size_t len = s->unit.size();
    if(len % itemsize != 0)
        throw new ValueError(new str("bytes length not a multiple of item size"));
    if(len == 1)
        this->units.push_back(s->unit[0]);
    else if(len) {
        size_t s1 = this->units.size();
        this->units.resize(s1+len);
        memcpy(&(this->units[s1]), &(s->unit[0]), len);
    }
    return NULL;
}

template<class T> list<T> *array<T>::tolist() {
    list<T> *l = new list<T>();
    size_t len = this->__len__();
    l->units.resize(len);
    for(size_t i=0; i<len; i++)
        l->units[i] = __getitem__((__ss_int)i);
    return l;
}

template<class T> __ss_int array<T>::__len__() {
    return (__ss_int)(units.size() / itemsize);
}

template<class T> __ss_bool array<T>::__eq__(pyobj *p) {
   if(p->__class__ != cl_array)
       return False;
   array<T> *b = (array<T> *)p;
   __ss_int len = this->__len__();
   if(b->__len__() != len)
       return False;
   if(this->typechar == b->typechar && this->typechar != 'f' && this->typechar != 'd')
       return __mbool(this->units.empty() || memcmp(&(this->units[0]), &(b->units[0]), this->units.size()) == 0);
   for(__ss_int i=0; i<len; i++)
       if(!__eq(this->__getitem__(i), b->__getitem__(i)))
           return False;
   return True;
}

template<class T> array<T> *array<T>::__mul__(__ss_int n) {
    array<T> *a = new array<T>(typecode);
    if(n<=0) return a;
    size_t len = this->units.size();
    a->units.resize(len*(size_t)n);
    if(len)
        for(size_t i=0; i<(size_t)n; i++)
            memcpy(&(a->units[i*len]), &(this->units[0]), len);
    return a;
}

template<class T> array<T> *array<T>::__imul__(__ss_int n) {
    if(n<=0) {
        this->units.clear();
        return this;
    }
    size_t len = this->units.size();
    this->units.resize(len*(size_t)n);
    if(len)
        for(size_t i=1; i<(size_t)n; i++)
            memcpy(&(this->units[i*len]), &(this->units[0]), len);
    return this;
}

template<class T> array<T> *array<T>::__add__(array<T> *b) {
    if(this->typecode != b->typecode)
        throw new TypeError(new str("bad argument type for built-in operation")); 
    array<T> *a = new array<T>(typecode);
    size_t s1 = this->units.size();
    size_t s2 = b->units.size();
    a->units.resize(s1+s2);
    if(s1) memcpy(&(a->units[0]), &(this->units[0]), s1);
    if(s2) memcpy(&(a->units[s1]), &(b->units[0]), s2);
    return a;
}

template<class T> array<T> *array<T>::__iadd__(array<T> *b) {
    if(this->typecode != b->typecode)
        throw new TypeError(new str("bad argument type for built-in operation")); 
    size_t s1 = this->units.size();
    size_t s2 = b->units.size();
    this->units.resize(s1+s2);
    if(s2) memcpy(&(this->units[s1]), &(b->units[0]), s2);
    return this;
}

template<class T> __ss_int array<T>::count(T t) {
    __ss_int result = 0;
    __ss_int len = this->__len__();
    for(__ss_int i=0; i<len; i++)
        if(__eq(t, this->__getitem__(i)))
            result += 1;
    return result;
}

template<class T> __ss_int array<T>::index(T t, __ss_int start) {
    __ss_int step = 1;
    __ss_int stop = this->__len__();
    slicenr(3, start, stop, step, this->__len__());
    for(__ss_int i=start; i<stop; i++)
        if(__eq(t, this->__getitem__(i)))
            return i;
    throw new ValueError(new str("array.index(x): x not in array"));
}

template<class T> __ss_int array<T>::index(T t, __ss_int start, __ss_int stop) {
    __ss_int step = 1;
    slicenr(3, start, stop, step, this->__len__());
    for(__ss_int i=start; i<stop; i++)
        if(__eq(t, this->__getitem__(i)))
            return i;
    throw new ValueError(new str("array.index(x): x not in array"));
}
template<class T> void *array<T>::remove(T t) {
    __ss_int len = this->__len__();
    for(__ss_int i=0; i<len; i++)
        if(__eq(t, this->__getitem__(i))) {
            this->pop(i);
            return NULL;
        }
    throw new ValueError(new str("array.remove(x): x not in array"));
}

template<class T> T array<T>::pop(__ss_int i) {
    __ss_int len = this->__len__();
    if(len==0)
        throw new IndexError(new str("pop from empty array"));
    if(i<0) i = len+i;
    if(i<0 or i>=len)
        throw new IndexError(new str("pop index out of range"));
    T t = this->__getitem__(i);
    this->units.erase(this->units.begin()+(i*itemsize), this->units.begin()+((i+1)*itemsize));
    return t;
}

template<class T> void *array<T>::clear() {
    this->units.clear();
    return NULL;
}

template<class T> void array<T>::fillbuf(T t) {
    switch(typechar) {
        case 'b':
            if(t > 127) throw new OverflowError(new str("signed char is greater than maximum"));
            if(t < -128) throw new OverflowError(new str("signed char is less than minimum"));
            *((signed char *)buffy) = (signed char)t; break;
        case 'B':
            if(t < 0) throw new OverflowError(new str("unsigned byte integer is less than minimum"));
            if(t > 255) throw new OverflowError(new str("unsigned byte integer is greater than maximum"));
            *((unsigned char *)buffy) = (unsigned char)t; break;
        case 'h':
            if(t > 32767) throw new OverflowError(new str("signed short integer is greater than maximum"));
            if(t < -32768) throw new OverflowError(new str("signed short integer is less than minimum"));
            *((signed short *)buffy) = (signed short)t; break;
        case 'H':
            if(t < 0) throw new OverflowError(new str("unsigned short is less than minimum"));
            if(t > 65535) throw new OverflowError(new str("unsigned short is greater than maximum"));
            *((unsigned short *)buffy) = (unsigned short)t; break;
        case 'i':
            if(t > 2147483647LL) throw new OverflowError(new str("signed integer is greater than maximum"));
            if(t < -2147483648LL) throw new OverflowError(new str("signed integer is less than minimum"));
            *((signed int *)buffy) = (signed int)t; break;
        case 'I':
            if(t < 0) throw new OverflowError(new str("can't convert negative value to unsigned int"));
            if(t > 4294967295LL) throw new OverflowError(new str("unsigned int is greater than maximum"));
            *((unsigned int *)buffy) = (unsigned int)t; break;
        case 'l':
            if(t > std::numeric_limits<signed long>::max()) throw new OverflowError(new str("signed long is greater than maximum"));
            if(t < std::numeric_limits<signed long>::min()) throw new OverflowError(new str("signed long is less than minimum"));
            *((signed long *)buffy) = (signed long)t; break;
        case 'L':
            if(t < 0) throw new OverflowError(new str("can't convert negative value to unsigned long"));
            if(t > std::numeric_limits<unsigned long>::max()) throw new OverflowError(new str("unsigned long is greater than maximum"));
            *((unsigned long *)buffy) = (unsigned long)t; break;
        case 'q':
            if(t > std::numeric_limits<signed long long>::max()) throw new OverflowError(new str("signed long long is greater than maximum"));
            if(t < std::numeric_limits<signed long long>::min()) throw new OverflowError(new str("signed long long is less than minimum"));
            *((signed long long *)buffy) = (signed long long)t; break;
        case 'Q':
            if(t < 0) throw new OverflowError(new str("can't convert negative int to unsigned"));
            if(t > std::numeric_limits<unsigned long long>::max()) throw new OverflowError(new str("unsigned long long is greater than maximum"));
            *((unsigned long long *)buffy) = (unsigned long long)t; break;
        case 'f': *((float *)buffy) = (float)t; break;
        case 'd': *((double *)buffy) = (double)t; break;
    }
}

template<class T> T array<T>::__getitem__(__ss_int i) {
    return __getfast__(i);
}

template<> inline __ss_int array<__ss_int>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    unsigned int j = (unsigned int)i;
    switch(typechar) {
        case 'b': return (__ss_int)(*((signed char *)(&units[j*itemsize])));
        case 'B': return (__ss_int)(*((unsigned char *)(&units[j*itemsize])));
        case 'h': return (__ss_int)(*((signed short *)(&units[j*itemsize])));
        case 'H': return (__ss_int)(*((unsigned short *)(&units[j*itemsize])));
        case 'i': return (__ss_int)(*((signed int *)(&units[j*itemsize])));
        case 'I': return (__ss_int)(*((unsigned int *)(&units[j*itemsize])));
        case 'l': return (__ss_int)(*((signed long *)(&units[j*itemsize])));
        case 'L': return (__ss_int)(*((unsigned long *)(&units[j*itemsize])));
        case 'q': return (__ss_int)(*((signed long long *)(&units[j*itemsize])));
        case 'Q': return (__ss_int)(*((unsigned long long *)(&units[j*itemsize])));
    }
    return 0;
}
template<> inline __ss_float array<__ss_float>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    if(typechar == 'f')
        return (__ss_float)(*((float *)(&units[(size_t)i*itemsize])));
    else
        return (__ss_float)(*((double *)(&units[(size_t)i*itemsize])));
}

template<class T> void *array<T>::append(T t) {
    fillbuf(t);
    for(unsigned int i=0; i<itemsize; i++)
        units.push_back(((char *)buffy)[i]);
    return NULL;
}

template<class T> void *array<T>::__setitem__(__ss_int i, T t) {
    i = __wrap(this, i);
    fillbuf(t);
    for(unsigned int j=0; j<itemsize; j++)
        this->units[i*itemsize+j] = ((char *)buffy)[j];
    return NULL;
}

template<class T> void *array<T>::insert(__ss_int i, T t) {
    __ss_int len = this->__len__();
    if(i<0) i += len;
    if(i<0) i = 0;
    if(i>len) i = len;
    /* validate/encode 't' into buffy *before* mutating 'units': fillbuf()
     * may throw OverflowError, and CPython leaves the array untouched in
     * that case. Splicing the placeholder bytes first and validating via
     * __setitem__() afterwards (as before) left a corrupt zero-element
     * behind whenever the value was out of range for the typecode. */
    fillbuf(t);
    this->units.insert(this->units.begin()+(i*itemsize), (char *)buffy, (char *)buffy+itemsize);
    return NULL;
}

template<class T> void *array<T>::__delitem__(__ss_int i) {
    i = __wrap(this, i);
    this->units.erase(units.begin()+(i*itemsize), units.begin()+((i+1)*itemsize));
    return NULL;
}

template<class T> str *array<T>::__repr__() {
    if (this->__len__())
        return __add_strs(5, new str("array('"), typecode, new str("', "), repr(tolist()), new str(")"));
    else
        return __add_strs(5, new str("array('"), typecode, new str("')"));
}

template<class T> void *array<T>::reverse() { /* use fillbuf, __setitem__ or standard C function? */
    size_t len = this->__len__();
    if(len > 1) {
        char *first = &units[0];
        char *second = &units[(len-1)*itemsize];
        for(size_t i=0; i<len/2; i++) {
            memcpy(buffy, first, itemsize);
            memcpy(first, second, itemsize);
            memcpy(second, buffy, itemsize);
            first += itemsize; 
            second -= itemsize;
        }
    }
    return NULL;
}

template<class T> void *array<T>::byteswap() { /* standard C function? */
    size_t len = this->__len__();
    for(size_t i=0; i<len; i++) {
        char *first = &units[i*itemsize];
        char *second = &units[((i+1)*itemsize)-1];
        for(unsigned int j=0; j<itemsize/2; j++) {
            char tmp = *first;
            *first = *second;
            *second = tmp;
            first++;
            second--;
        }
    }
    return NULL;
}

template<class T> void *array<T>::tofile(file_binary *f) {
    f->write(this->tobytes());
    return NULL;
}

template<class T> void *array<T>::fromfile(file_binary *f, __ss_int n) {
    bytes *s = f->read(n*(__ss_int)itemsize);
    size_t len = s->__len__();
    if(len % itemsize != 0)
        throw new ValueError(new str("bytes length not a multiple of item size"));
    for(size_t i=0; i<len; i++)
        units.push_back(s->unit[i]);
    if (len < (size_t)n*itemsize)
        throw new EOFError(new str("read() didn't return enough bytes"));
    return NULL;
}

template<class T> array<T> *array<T>::__copy__() {
    array<T> *a = new array<T>(this->typecode);
    a->units = this->units;
    return a;
}

template<class T> array<T> *array<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    return this->__copy__();
}

template<class T> array<T> *array<T>::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    array<T> *c = new array<T>(typecode);
    slicenr(x, l, u, s, this->__len__());
    if(s == 1) {
        size_t slen = (u>l) ? (size_t)(u-l)*itemsize : 0;
        c->units.resize(slen);
        if(slen) memcpy(&(c->units[0]), &(this->units[l*itemsize]), slen);
    } else if(s > 0)
        for(__ss_int i=l; i<u; i += s)
            for(size_t j=0; j<itemsize; j++)
                c->units.push_back(units[(size_t)i*itemsize+j]);
    else
        for(__ss_int i=l; i>u; i += s)
            for(size_t j=0; j<itemsize; j++)
                c->units.push_back(units[(size_t)i*itemsize+j]);
    return c;
}

/* XXX optimize XXX */

template<class T> void *array<T>::__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, array<T> *b) {
    if(this->typecode != b->typecode)
        throw new TypeError(new str("bad argument type for built-in operation"));
    if(x&4 && s != 1) { // extended slice (step 's' explicitly given): pre-check the size
        __ss_int nl = l, nu = u, ns = s; // local copies -- don't disturb l/u/s below
        slicenr(x, nl, nu, ns, this->__len__());
        __ss_int slicesize;
        if(nl == nu) slicesize = 0;
        else if(ns > 0 && nu < nl) slicesize = 0;
        else if(ns < 0 && nl < nu) slicesize = 0;
        else {
            __ss_int slicelen = __abs(nu-nl);
            __ss_int absstep = __abs(ns);
            slicesize = slicelen/absstep;
            if(slicelen%absstep) slicesize += 1;
        }
        __ss_int blen = b->__len__();
        if(slicesize != blen)
            throw new ValueError(__add_strs(0, new str("attempt to assign array of size "), __str(blen), new str(" to extended slice of size "), __str(slicesize)));
    }
    list<T> *l2 = this->tolist();
    l2->__setslice__(x, l, u, s, b->tolist());
    this->units.clear();
    this->fromlist(l2);
    return NULL;
}

template<class T> void *array<T>::__delete__(__ss_int i) {
    i = __wrap(this, i);
    this->units.erase(units.begin()+(i*itemsize), units.begin()+((i+1)*itemsize));
    return NULL;
}

/* XXX optimize XXX */

template<class T> void *array<T>::__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    list<T> *l2 = this->tolist();
    l2->__delete__(x, l, u, s);
    this->units.clear();
    this->fromlist(l2);
    return NULL;
}
template<class T> void *array<T>::__delslice__(__ss_int a, __ss_int b) {
    if(a>this->__len__()) return NULL;
    if(b>this->__len__()) b = this->__len__();
    units.erase(units.begin()+(a*itemsize),units.begin()+(b*itemsize));
    return NULL;
}

void __init();

} // module namespace
#endif
