/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef SS_BUILTIN_HPP
#define SS_BUILTIN_HPP

#ifdef __SS_BIND
#include <Python.h>
#endif

#ifndef __SS_NOGC
#ifdef WIN32
#define GC_NO_INLINE_STD_NEW
#endif
#include <gc/gc_allocator.h>
#include <gc/gc_cpp.h>
#include <new>

/* gc_cpp.h only redirects the classic, non-aligned, throwing global
 * operator new/delete to the GC heap. C++14 added a separate sized
 * deallocation overload, and C++17 added another overload set for
 * over-aligned allocation (std::align_val_t), plus there is the
 * pre-existing nothrow overload set; none of these are covered by
 * gc_cpp.h. Any allocation that goes through one of these uncovered
 * overloads therefore bypasses GC_MALLOC and lands in the plain
 * system allocator, producing memory the collector never scans. If a
 * pointer into a GC-managed object is ever stored only in such a
 * buffer (e.g. a standard library algorithm's internal scratch space,
 * such as std::stable_sort's merge buffer, allocated via the nothrow
 * operator new below but released via the plain sized operator
 * delete(void*, size_t)), a collection that runs while it's live
 * there can reclaim the object out from under it -- or, since the
 * sized delete overload here was previously missing entirely, the
 * pointer can instead be handed to the system allocator's free()
 * even though it was never obtained from malloc, aborting immediately
 * with "free(): invalid pointer". Redirect these remaining overloads
 * to GC_MALLOC (and make the matching deletes no-ops) so *all*
 * allocation paths stay inside the traced heap. */
inline void *operator new(std::size_t sz, std::align_val_t) {
    return GC_MALLOC(sz);
}
inline void *operator new[](std::size_t sz, std::align_val_t) {
    return GC_MALLOC(sz);
}
inline void *operator new(std::size_t sz, const std::nothrow_t &) noexcept {
    return GC_MALLOC(sz);
}
inline void *operator new[](std::size_t sz, const std::nothrow_t &) noexcept {
    return GC_MALLOC(sz);
}
inline void *operator new(std::size_t sz, std::align_val_t,
                           const std::nothrow_t &) noexcept {
    return GC_MALLOC(sz);
}
inline void *operator new[](std::size_t sz, std::align_val_t,
                             const std::nothrow_t &) noexcept {
    return GC_MALLOC(sz);
}

/* GC_MALLOC'd memory is reclaimed by the collector itself, so the
 * matching deallocation overloads are deliberate no-ops (consistent
 * with how gc_cpp.h treats the classic operator delete). This sized
 * overload in particular is the one std::stable_sort's temporary
 * buffer (stl_tempbuf.h's __return_temporary_buffer) actually calls;
 * without it, freeing that buffer falls through to the system
 * allocator's free() on a GC_MALLOC'd pointer and aborts. */
inline void operator delete(void *, std::size_t) noexcept {}
inline void operator delete[](void *, std::size_t) noexcept {}
inline void operator delete(void *) noexcept {}
inline void operator delete[](void *) noexcept {}
inline void operator delete(void *, std::align_val_t) noexcept {}
inline void operator delete[](void *, std::align_val_t) noexcept {}
inline void operator delete(void *, const std::nothrow_t &) noexcept {}
inline void operator delete[](void *, const std::nothrow_t &) noexcept {}
inline void operator delete(void *, std::align_val_t,
                             const std::nothrow_t &) noexcept {}
inline void operator delete[](void *, std::align_val_t,
                               const std::nothrow_t &) noexcept {}
#endif

#ifdef __SS_BOOST
#include <boost/container/small_vector.hpp>
#include <boost/unordered/unordered_flat_map.hpp>
#include <boost/unordered/unordered_flat_set.hpp>
#endif

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
#include <numeric>
#include <cstddef>
#include <type_traits>
#include <bit>
#include <charconv>
#include <cstdio>
#include <cstdlib>

/* Floating-point std::to_chars is C++17, but shipped later than the rest of
 * <charconv>: libstdc++ has it from release 11, while libc++ and MSVC have it
 * but libc++ still does not advertise __cpp_lib_to_chars, so that macro cannot
 * be used to detect it. Anything older falls back to probing printf
 * precisions, which reaches the same answer more slowly. */
#if !defined(__GLIBCXX__) || (_GLIBCXX_RELEASE >= 11)
#define __SS_FP_TO_CHARS 1
#endif


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
#elif defined(__SS_INT128)
    typedef __int128 __ss_int;
#define __SS_LONG
#else
    typedef int64_t __ss_int;
#ifndef __SS_INT64
#define __SS_INT64
#endif
#define __SS_LONG
#endif

/* Unsigned counterpart of __ss_int. Signed overflow is undefined behaviour,
 * so anything that has to negate a possibly-most-negative value, count bits,
 * or compute a difference that may exceed the signed range does the work in
 * this type instead, where wrap-around is well defined. */
typedef std::make_unsigned<__ss_int>::type __ss_uint;

/* Magnitude of an __ss_int as __ss_uint. Written as a subtraction from zero
 * rather than as -(__ss_uint)i so that the most negative value (whose
 * negation is not representable as __ss_int) is handled correctly. */
static inline __ss_uint __ss_magnitude(__ss_int i) {
    return (i < 0) ? ((__ss_uint)0 - (__ss_uint)i) : (__ss_uint)i;
}

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
template <class K, class V> class frozendict;

template <class T> class __iter;

template<class T>
using tuple = tuple2<T, T>;

/* STL types */

#ifdef __SS_NOGC
template <class T>
using __ss_allocator = std::allocator< T >;
#else
template <class T>
using __ss_allocator = gc_allocator< T >;
#endif

#ifdef __SS_BOOST
#define __GC_VECTOR(T) boost::container::small_vector<T, 4, __ss_allocator<T> >
#else
#define __GC_VECTOR(T) std::vector< T, __ss_allocator< T > >
#endif

#define __GC_DEQUE(T) std::deque< T, __ss_allocator< T > >
#define __GC_STRING std::basic_string<char, std::char_traits<char>, __ss_allocator<char> >

extern __ss_bool True;
extern __ss_bool False;
typedef struct {} __ss_void_struct;
extern __ss_void_struct __ss_void;  // TODO own type

/* externs */

extern class_ *cl_str_, *cl_int_, *cl_bool, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict,
              *cl_set, *cl_object, *cl_xrange, *cl_rangeiter, *cl_bytes, *cl_bytearray, *cl_frozendict;

extern __GC_VECTOR(str *) __char_cache;
extern __GC_VECTOR(bytes *) __byte_cache;

extern str *nl;
extern str *sp;
extern str *byteorder_big, *byteorder_little;

/* root object class */

#ifdef __SS_NOGC
class pyobj {
#else
class pyobj : public gc {
#endif
public:
    class_ *__class__;

    virtual str *__repr__();
    virtual str *__str__();

    virtual __ss_int __hash__();
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
    virtual __ss_float __float__();
    virtual complex __ss___complex__();
    virtual __ss_bool __bool__();

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

// TODO better approach to split declarations/template definitions?
#define SS_DECL
#include "builtin/bool.hpp"
#include "builtin/list.hpp"
#undef SS_DECL

static inline __ss_bool __mbool(bool c) { __ss_bool b; b.value=c?1:0; return b; }

void __throw_index_out_of_range();
void __throw_range_step_zero();
void __throw_stop_iteration();
void __throw_zero_division(const char *msg);

#ifdef __GNUC__
#define unlikely(x)       __builtin_expect((x), 0)
#else
#define unlikely(x)    (x)
#endif

template<class T> static inline __ss_int __wrap(T a, __ss_int i) {
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

#ifdef __SS_BOOST
template <class K, class V>
using __GC_DICT = boost::unordered_flat_map<K, V, ss_hash<K>, ss_eq<K>, __ss_allocator< std::pair<const K, V> > >;

template <class T>
using __GC_SET = boost::unordered_flat_set<T, ss_hash<T>, ss_eq<T>, __ss_allocator< T > >;

#else
template <class K, class V>
using __GC_DICT = std::unordered_map<K, V, ss_hash<K>, ss_eq<K>, __ss_allocator< std::pair<K const, V> > >;

template <class T>
using __GC_SET = std::unordered_set<T, ss_hash<T>, ss_eq<T>, __ss_allocator< T > >;
#endif

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
    __seqiter();
    __seqiter(pyseq<T> *p);
    T __next__();
};

template <class T> __iter<T> *___iter(pyiter<T> *p) {
    return p->__iter__();
}

tuple<__ss_int >*__ss_tuple_int(__ss_int n, __ss_int a, __ss_int b);

/* slicing */

void slicenr(__ss_int x, __ss_int &l, __ss_int &u, __ss_int &s, __ss_int len);

#include "builtin/exception.hpp"
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
    __iter<T> *it = this->__iter__();
    it->__stop_iteration = false;
    return it;
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
    __ss_int i, cmp;
    __ss_int mnm = ___min(2, __ss_void, 0, this->__len__(), b->__len__());
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

#ifdef __SS_NOBOUNDS
    #define __SS_UNPACK_CHECK(t, expected)
#else
#define __SS_UNPACK_CHECK(t, expected) \
    if(len(t) > (__ss_int)expected) \
        throw new ValueError(new str("too many values to unpack")); \
    else if(len(t) < (__ss_int)expected) \
        throw new ValueError(new str("not enough values to unpack"));
#endif

template<class T, int SiteId> list<T> *__ss_list() {
    list<T> *l = new list<T>();
#if defined(__SS_PREDICT) || !defined(__SS_BOOST)
    __SS_LIST_RESERVE(l, 4);
#endif
    return l;
}

inline list<__ss_int> *__ss_list_range(__ss_int a, __ss_int b, __ss_int c) {
    list<__ss_int> *l = new list<__ss_int>();
    __ss_int len = range_len(a, b, c);
    l->units.resize(len);
    __ss_int pos = 0;
    if(a <= b) {
        for(__ss_int i=a; i<b; i+=c)
            l->units[pos++] = i;
    } else {
        for(__ss_int i=a; i>b; i+=c)
            l->units[pos++] = i;
    }
    return l;
}

inline list<__ss_int> *__ss_list_range(__ss_int a, __ss_int b) {
    return __ss_list_range(a, b, 1);
}

inline list<__ss_int> *__ss_list_range(__ss_int a) {
    return __ss_list_range(0, a, 1);
}

/* init/exit */

void __init();
void __start(void (*initfunc)());
void __ss_exit(int code=0);

} // namespace __shedskin__
#endif
