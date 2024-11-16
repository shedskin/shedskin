/* Copyright 2005-2024 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_BUILTIN_HPP
#define SS_BUILTIN_HPP

#ifdef __SS_BIND
#include <Python.h>
#endif

#ifdef WIN32
#define GC_NO_INLINE_STD_NEW
#endif
#include <gc/gc_allocator.h>
#include <gc/gc_cpp.h>

#include <vector>
#include <deque>
#include <bitset>
#include <string>
#include <unordered_set>
#include <unordered_map>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdarg>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <iterator>
#include <ctype.h>
#include <stdint.h>
#include <limits>

#ifndef WIN32
#include <cxxabi.h>
#include <exception>
#ifndef __APPLE__
#ifdef __SS_BACKTRACE
#include <execinfo.h>
#endif
#endif
#endif

#if defined(_MSC_VER)
#include <ciso646>
#endif

namespace __shedskin__ {

/* integer type */

#if defined(__SS_INT32)
    typedef int32_t __ss_int;
#elif defined(__SS_INT64)
    typedef int64_t __ss_int;
#define __SS_LONG
#elif defined(__SS_INT128)
    typedef __int128 __ss_int;
#define __SS_LONG
#else
    typedef int __ss_int;
#endif

/* float type */

#if defined(__SS_FLOAT32)
    typedef float __ss_float;
#else
    typedef double __ss_float;
#endif

/* forward class declarations */

class __ss_bool;
class complex;

class pyobj;
class class_;
class str;
class bytes;

template <class T> class pyiter;
template <class T> class pyseq;

template <class T> class list;
template <class A, class B> class tuple2;
template <class T> class set;
template <class K, class V> class dict;

template <class T> class __iter;

template<class T>
using tuple = tuple2<T, T>;

/* STL types */

// TODO switch to template aliases
#define __GC_VECTOR(T) std::vector< T, gc_allocator< T > >
#define __GC_DEQUE(T) std::deque< T, gc_allocator< T > >
#define __GC_STRING std::basic_string<char,std::char_traits<char>,gc_allocator<char> >

extern __ss_bool True;
extern __ss_bool False;

/* externs */

extern class_ *cl_str_, *cl_int_, *cl_bool, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict, *cl_set, *cl_object, *cl_xrange, *cl_rangeiter, *cl_bytes;

extern __GC_VECTOR(str *) __char_cache;
extern __GC_VECTOR(bytes *) __byte_cache;

extern str *nl;
extern str *sp;

/* root object class */

class pyobj : public gc {
public:
    class_ *__class__;

    virtual str *__repr__();
    virtual str *__str__();

    virtual long __hash__();
    virtual __ss_int __cmp__(pyobj *p);

    virtual __ss_bool __eq__(pyobj *p);
    virtual __ss_bool __ne__(pyobj *p);
    virtual __ss_bool __gt__(pyobj *p);
    virtual __ss_bool __lt__(pyobj *p);
    virtual __ss_bool __ge__(pyobj *p);
    virtual __ss_bool __le__(pyobj *p);

    virtual pyobj *__copy__();
    virtual pyobj *__deepcopy__(dict<void *, pyobj *> *);

    virtual __ss_int __len__();
    virtual __ss_int __int__();

    virtual __ss_bool __nonzero__();
    virtual __ss_int __index__();

    static const bool is_pyseq = false;
};

/* abstract iterable class */

template <class T> class pyiter : public pyobj {
public:
    virtual __iter<T> *__iter__() = 0;
    virtual __ss_bool __contains__(T t);

    typedef T for_in_unit;
    typedef __iter<T> * for_in_loop;

    inline __iter<T> *for_in_init();
    inline bool for_in_has_next(__iter<T> *iter);
    inline T for_in_next(__iter<T> *iter);
};

/* abstract sequence class */

template <class T> class pyseq : public pyiter<T> {
public:
    virtual __ss_int __len__() = 0;
    virtual T __getitem__(__ss_int i) = 0;
    virtual __ss_int __cmp__(pyobj *p);

    virtual __iter<T> *__iter__();

    typedef T for_in_unit;
    typedef size_t for_in_loop;

    inline size_t for_in_init();
    inline bool for_in_has_next(size_t i);
    inline T for_in_next(size_t &i);

    static const bool is_pyseq = true;
};

template <class R, class A> class pycall1 : public pyobj {
public:
    virtual R __call__(A a) = 0;
};
template <class R, class A, class B> class pycall2 : public pyobj {
public:
    virtual R __call__(A a, B b) = 0;
};

// TODO better approach to split declarations/template definitions?
#define SS_DECL
#include "builtin/bool.hpp"
#include "builtin/list.hpp"
#undef SS_DECL

static inline __ss_bool __mbool(bool c) { __ss_bool b; b.value=c?1:0; return b; }

void __throw_index_out_of_range();
void __throw_range_step_zero();
void __throw_stop_iteration();

#ifdef __GNUC__
#define unlikely(x)       __builtin_expect((x), 0)
#else
#define unlikely(x)    (x)
#endif

template<class T> static inline int __wrap(T a, __ss_int i) {
    __ss_int l = len(a);
#ifndef __SS_NOWRAP
    if(unlikely(i<0)) i += l;
#endif
#ifndef __SS_NOBOUNDS
        if(unlikely(i<0 || i>= l))
            __throw_index_out_of_range();
#endif
    return i;
}

#undef unlikely

#include "builtin/iter.hpp"
#include "builtin/hash.hpp"
#include "builtin/str.hpp"
#include "builtin/compare.hpp"

template <class K, class V>
using __GC_DICT = std::unordered_map<K, V, ss_hash<K>, ss_eq<K>, gc_allocator< std::pair<K const, V> > >;

template <class T>
using __GC_SET = std::unordered_set<T, ss_hash<T>, ss_eq<T>, gc_allocator< T > >;

class class_: public pyobj {
public:
    str *__name__;

    class_(const char *name);
    str *__repr__();
    __ss_bool __eq__(pyobj *c);

};

class object : public pyobj {
public:
    object();

};

template<class T> class __iter : public pyiter<T> {
public:
    T __result;
    bool __stop_iteration;

    __iter<T> *__iter__();
    virtual T __next__(); /* __get_next can be overloaded to avoid (slow) exception handling */
    virtual T __get_next();

    str *__repr__();
};

template <class T> class __seqiter : public __iter<T> {
public:
    __ss_int counter, size;
    pyseq<T> *p;
    __seqiter<T>();
    __seqiter<T>(pyseq<T> *p);
    T __next__();
};

template <class T> __iter<T> *___iter(pyiter<T> *p) {
    return p->__iter__();
}

/* slicing */

void slicenr(__ss_int x, __ss_int &l, __ss_int &u, __ss_int &s, __ss_int len);

#define SS_DECL
#include "builtin/function.hpp"
#undef SS_DECL

/* assert */

#ifndef __SS_NOASSERT
#define ASSERT(x, y) if(!(x)) throw new AssertionError(y);
#else
#define ASSERT(x, y)
#endif

/* with statement */

template<class T> class __With {
public:
    __With(T expr) : _expr(expr) {
        _expr->__enter__();
    }
    ~__With() {
        _expr->__exit__();
    }
    operator T() const {
        return _expr;
    }
private:
    T _expr;
};

#define WITH(e, n) {           \
    __With<decltype(e)> __with##n(e); // TODO unique id

#define WITH_VAR(e, v, n) {    \
    __With<decltype(e)> __with##n(e);      \
    decltype(e) v = __with##n;

#define END_WITH }

/* and, or, not */

#define __OR(a, b, t) ((___bool(__ ## t = a))?(__ ## t):(b))
#define __AND(a, b, t) ((!___bool(__ ## t = a))?(__ ## t):(b))
#define __NOT(x) (__mbool(!(x)))

#include "builtin/bool.hpp"
#include "builtin/exception.hpp"
#include "builtin/extmod.hpp"
#include "builtin/tuple.hpp"
#include "builtin/function.hpp"
#include "builtin/list.hpp"
#include "builtin/bytes.hpp"
#include "builtin/math.hpp"
#include "builtin/dict.hpp"
#include "builtin/set.hpp"
#include "builtin/file.hpp"
#include "builtin/format.hpp"
#include "builtin/complex.hpp"
#include "builtin/copy.hpp"

/* pyiter methods */

template<class T> inline __iter<T> *pyiter<T>::for_in_init() {
    return this->__iter__();
}

template<class T> inline bool pyiter<T>::for_in_has_next(__iter<T> *iter) {
    iter->__result = iter->__get_next();
    return not iter->__stop_iteration;
}

template<class T> inline T pyiter<T>::for_in_next(__iter<T> *iter) {
    return iter->__result;
}

template<class T> inline __ss_bool pyiter<T>::__contains__(T t) {
    T e;
    typename pyiter<T>::for_in_loop __3;
    int __2;
    pyiter<T> *__1;
    FOR_IN(e,this,1,2,3)
        if(__eq(e,t))
            return __mbool(true);
    END_FOR
    return __mbool(false);
}

/* pyseq methods */

template<class T> __ss_int pyseq<T>::__cmp__(pyobj *p) {
    if (!p) return 1;
    pyseq<T> *b = (pyseq<T> *)p;
    int i, cmp;
    int mnm = ___min(2, 0, this->__len__(), b->__len__());
    for(i = 0; i < mnm; i++) {
        cmp = __cmp(this->__getitem__(i), b->__getitem__(i));
        if(cmp)
            return cmp;
    }
    return __cmp(this->__len__(), b->__len__());
}

template<class T> __iter<T> *pyseq<T>::__iter__() {
    return new __seqiter<T>(this);
}

template<class T> inline size_t pyseq<T>::for_in_init() {
    return 0;
}

template<class T> inline bool pyseq<T>::for_in_has_next(size_t i) {
    return (__ss_int)i < __len__(); /* XXX opt end cond */
}

template<class T> inline T pyseq<T>::for_in_next(size_t &i) {
    __ss_int pos = (__ss_int)i;
    i++;
    return __getitem__(pos);
}

/* __iter methods */

template<class T> __iter<T> *__iter<T>::__iter__() {
    __stop_iteration = false;
    return this;
}

template<class T> T __iter<T>::__next__() { /* __get_next can be overloaded instead to avoid (slow) exception handling */
    __result = this->__get_next();
    if(__stop_iteration)
        throw new StopIteration();
    return __result;
}

template<class T> T __iter<T>::__get_next() {
    try {
        __result = this->__next__();
    } catch (StopIteration *) {
        __stop_iteration = true;
    }
    return __result;
}

/* iterators */

template<class T> str *__iter<T>::__repr__() {
    return new str("iterator instance");
}

template<class T> __seqiter<T>::__seqiter() {}
template<class T> __seqiter<T>::__seqiter(pyseq<T> *seq) {
    this->p = seq;
    size = seq->__len__();
    counter = 0;
}

template<class T> T __seqiter<T>::__next__() {
    if(counter==size)
        __throw_stop_iteration();
    return p->__getitem__(counter++);
}

/* tuple unpacking */

template<class T> void __unpack_check(T t, int expected) {
    if(len(t) > (__ss_int)expected)
	 throw new ValueError(new str("too many values to unpack"));
    else if(len(t) < (__ss_int)expected)
	 throw new ValueError(new str("not enough values to unpack"));
}

/* init/exit */

void __init();
void __start(void (*initfunc)());
void __ss_exit(int code=0);

} // namespace __shedskin__
#endif
