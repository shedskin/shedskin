/* Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef BUILTIN_HPP
#define BUILTIN_HPP

#ifdef __SS_BIND
#include <Python.h>
#endif

#include <gc/gc_allocator.h>
#include <gc/gc_cpp.h>

#include <vector>
#include <deque>
#include <string>
#include <set>
#include <iostream>
#include <functional>
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
#include "builtin/msvc.hpp"
#endif

namespace __shedskin__ {

/* integer type */

#ifdef __SS_LONG
    typedef long long __ss_int;
#else
    typedef int __ss_int;
#endif

#ifdef __SS_FLOAT
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
class file;
class file_binary;

class int_;
class bool_;
class float_;
class complex_;

template <class T> class pyiter;
template <class T> class pyseq;

template <class T> class list;
template <class A, class B> class tuple2;
template <class T> class set;
template <class K, class V> class dict;

template <class T> class __iter;
template <class T> class __seqiter;
template <class T> class __setiter;
template <class T, class U> class __dictiterkeys;
template <class T, class U> class __dictitervalues;
template <class T, class U> class __dictiteritems;
class __fileiter;
class __filebiniter;
class __xrange;
class __rangeiter;

class BaseException;
class Exception;
class AssertionError;
class KeyError;
class ValueError;
class IndexError;
class NotImplementedError;
class FileNotFoundError;
class OSError;
class SyntaxError;
class StopIteration;
class TypeError;
class RuntimeError;
class OverflowError;

template<class T>
using tuple = tuple2<T, T>;

/* STL types */

#define __GC_VECTOR(T) std::vector< T, gc_allocator< T > >
#define __GC_DEQUE(T) std::deque< T, gc_allocator< T > >
#define __GC_STRING std::basic_string<char,std::char_traits<char>,gc_allocator<char> >

extern __ss_bool True;
extern __ss_bool False;

/* class declarations */

#ifdef __SS_GC_CLEANUP
class pyobj : public gc_cleanup {
#else
class pyobj : public gc {
#endif
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

template <class T> class list : public pyseq<T> {
public:
    __GC_VECTOR(T) units;

    list();
    list(int count, ...);
    template <class U> list(U *iter);
    list(list<T> *p);
    list(tuple2<T, T> *p);
    list(str *s);

    void clear();
    void *__setitem__(__ss_int i, T e);
    void *__delitem__(__ss_int i);
    int empty();
    list<T> *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    void *__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, pyiter<T> *b);
    void *__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, list<T> *b);
    void *__delete__(__ss_int i);
    void *__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);
    void *__delslice__(__ss_int a, __ss_int b);
    __ss_bool __contains__(T a);

    list<T> *__add__(list<T> *b);
    list<T> *__mul__(__ss_int b);

    template <class U> void *extend(U *iter);
    void *extend(list<T> *p);
    void *extend(tuple2<T,T> *p);
    void *extend(str *s);

    template <class U> list<T> *__iadd__(U *iter);
    list<T> *__imul__(__ss_int n);

    __ss_int index(T a);
    __ss_int index(T a, __ss_int s);
    __ss_int index(T a, __ss_int s, __ss_int e);

    __ss_int count(T a);
    str *__repr__();
    __ss_bool __eq__(pyobj *l);

    void resize(__ss_int i); /* XXX remove */

    inline T __getfast__(__ss_int i);
    inline T __getitem__(__ss_int i);
    inline __ss_int __len__();

    T pop();
    T pop(int m);
    void *remove(T e);
    template <class U> void *remove(U e);
    void *insert(int m, T e);

    void *append(T a);

    void *reverse();
    template<class U> void *sort(__ss_int (*cmp)(T, T), U (*key)(T), __ss_int reverse);
    template<class U> void *sort(__ss_int cmp, U (*key)(T), __ss_int reverse);
    void *sort(__ss_int (*cmp)(T, T), __ss_int key, __ss_int reverse);
    void *sort(__ss_int cmp, __ss_int key, __ss_int reverse);

    list<T> *__copy__();
    list<T> *__deepcopy__(dict<void *, pyobj *> *memo);

    /* iteration */

    inline bool for_in_has_next(size_t i);
    inline T for_in_next(size_t &i);
#ifdef __SS_BIND
    list(PyObject *);
    PyObject *__to_py__();
#endif
};

template<class A, class B> class tuple2 : public pyobj {
public:
    A first;
    B second;

    tuple2();
    tuple2(int n, A a, B b);
    void __init2__(A a, B b);

    A __getfirst__();
    B __getsecond__();

    str *__repr__();
    __ss_int __len__();

    __ss_bool __eq__(pyobj *p);
    __ss_int __cmp__(pyobj *p);
    long __hash__();

    tuple2<A,B> *__copy__();
    tuple2<A,B> *__deepcopy__(dict<void *, pyobj *> *memo);

#ifdef __SS_BIND
    tuple2(PyObject *p);
    PyObject *__to_py__();
#endif
};

template<class T> class tuple2<T,T> : public pyseq<T> {
public:
    __GC_VECTOR(T) units;

    tuple2();
    tuple2(int count, ...);
    template <class U> tuple2(U *iter);
    tuple2(list<T> *p);
    tuple2(tuple2<T, T> *p);
    tuple2(str *s);

    void __init2__(T a, T b);

    T __getfirst__();
    T __getsecond__();

    inline T __getfast__(__ss_int i);
    inline T __getitem__(__ss_int i);

    inline __ss_int __len__();

    str *__repr__();

    tuple2<T,T> *__add__(tuple2<T,T> *b);
    tuple2<T,T> *__mul__(__ss_int b);

    tuple2<T,T> *__iadd__(tuple2<T,T> *b);
    tuple2<T,T> *__imul__(__ss_int n);

    __ss_bool __contains__(T a);
    __ss_bool __eq__(pyobj *p);

    tuple2<T,T> *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);

    long __hash__();

    tuple2<T,T> *__deepcopy__(dict<void *, pyobj *> *memo);
    tuple2<T,T> *__copy__();

    /* iteration */

    inline bool for_in_has_next(size_t i);
    inline T for_in_next(size_t &i);

#ifdef __SS_BIND
    tuple2(PyObject *p);
    PyObject *__to_py__();
#endif
};

class bytes : public pyseq<__ss_int> {
protected:
public:
    __GC_STRING unit;
    long hash;
    int frozen;

    bytes(int frozen=1);
    bytes(const char *s);
    bytes(bytes *b, int frozen=1);
    bytes(__GC_STRING s, int frozen=1);
    bytes(const char *s, int size, int frozen=1); /* '\0' delimiter in C */

    inline __ss_int __getitem__(__ss_int i);
    inline __ss_int __getfast__(__ss_int i);

    template<class U> bytes *join(U *);

    inline __ss_int __len__();
    bytes *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);

    bytes *rstrip(bytes *chars=0);
    bytes *strip(bytes *chars=0);
    bytes *lstrip(bytes *chars=0);

    list<bytes *> *split(bytes *sep=0, __ss_int maxsplit=-1);
    list<bytes *> *rsplit(bytes *sep = 0, __ss_int maxsplit = -1);
    tuple2<bytes *, bytes *> *rpartition(bytes *sep);
    tuple2<bytes *, bytes *> *partition(bytes *sep);
    list<bytes *> *splitlines(__ss_int keepends = 0);

    /* functions pointing to the underlying C++ implementation */
    const char *c_str() const;
    const size_t size() const;
    const __ss_int find(const char c, __ss_int a=0) const;
    const __ss_int find(const char *c, __ss_int a=0) const;

    __ss_int __fixstart(__ss_int a, __ss_int b);
    __ss_int __checkneg(__ss_int i);

    __ss_int find(bytes *s, __ss_int a=0);
    __ss_int find(bytes *s, __ss_int a, __ss_int b);
    __ss_int rfind(bytes *s, __ss_int a=0);
    __ss_int rfind(bytes *s, __ss_int a, __ss_int b);

    bytes *upper();
    bytes *lower();
    bytes *title();
    bytes *capitalize();

    __ss_bool istitle();
    __ss_bool isspace();
    __ss_bool isalpha();
    __ss_bool isdigit();
    __ss_bool islower();
    __ss_bool isupper();
    __ss_bool isalnum();
    __ss_bool __ss_isascii();

    __ss_bool startswith(bytes *s, __ss_int start=0);
    __ss_bool startswith(bytes *s, __ss_int start, __ss_int end);
    __ss_bool endswith(bytes *s, __ss_int start=0);
    __ss_bool endswith(bytes *s, __ss_int start, __ss_int end);

    __ss_int count(bytes *b, __ss_int start=0);
    __ss_int count(__ss_int b, __ss_int start=0);
    __ss_int count(bytes *b, __ss_int start, __ss_int end);
    __ss_int count(__ss_int b, __ss_int start, __ss_int end);

    __ss_int index(bytes *s, __ss_int a=0);
    __ss_int index(bytes *s, __ss_int a, __ss_int b);
    __ss_int rindex(bytes *s, __ss_int a=0);
    __ss_int rindex(bytes *s, __ss_int a, __ss_int b);

    bytes *expandtabs(__ss_int tabsize=8);

    bytes *swapcase();

    bytes *replace(bytes *a, bytes *b, __ss_int c=-1);

    bytes *center(__ss_int width, bytes *fillchar=0);

    bytes *zfill(__ss_int width);
    bytes *ljust(__ss_int width, bytes *fillchar=0);
    bytes *rjust(__ss_int width, bytes *fillchar=0);

    str *hex(str *sep=0);

    str *__str__();
    str *__repr__();

    __ss_bool __contains__(bytes *);

    __ss_bool __eq__(pyobj *s);
    long __hash__();

    __ss_bool __ctype_function(int (*cfunc)(int));

    bytes *__add__(bytes *b);
    bytes *__mul__(__ss_int n);

    /* iteration */

    inline bool for_in_has_next(size_t i);
    inline __ss_int for_in_next(size_t &i);

    /* bytearray */

    void *clear();
    void *append(__ss_int i);
    __ss_int pop(__ss_int i=-1);
    bytes *copy();
    void *extend(pyiter<__ss_int> *p);
    void *reverse();
    void *insert(__ss_int index, __ss_int item);

    void *__setitem__(__ss_int i, __ss_int e);
    void *__delitem__(__ss_int i);

    void *remove(__ss_int i);

    bytes *__iadd__(bytes *b);
    bytes *__imul__(__ss_int n);

    void *__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, pyiter<__ss_int> *b);
    void *__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);

#ifdef __SS_BIND
    bytes(PyObject *p);
    PyObject *__to_py__();
#endif
};

class str : public pyseq<str *> {
protected:
public:
    __GC_STRING unit;
    long hash;
    bool charcache;

    str();
    str(const char *s);
    str(__GC_STRING s);
    str(const char *s, int size); /* '\0' delimiter in C */

    __ss_bool __contains__(str *s);
    str *strip(str *chars=0);
    str *lstrip(str *chars=0);
    str *rstrip(str *chars=0);
    __ss_bool __eq__(pyobj *s);
    str *__add__(str *b);

    template<class U> str *join(U *);

    /* operators */
    //inline void operator+= (const char *c);
    str *operator+ (const char *c);
    str *operator+ (const char &c);
    void operator+= (const char *c);
    void operator+= (const char &c);
    //str *operator+ (const char c);
    //str *operator+ (str *c);
    //str *operator+ (basic_string c);

    /* functions pointing to the underlying C++ implementation */
    const char *c_str() const;
    const size_t size() const;
    const __ss_int find(const char c, __ss_int a=0) const;
    const __ss_int find(const char *c, __ss_int a=0) const;

    str *__str__();
    str *__repr__();
    str *__mul__(__ss_int n);
    inline str *__getitem__(__ss_int n);
    inline str *__getfast__(__ss_int i);
    inline __ss_int __len__();
    str *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);

    list<str *> *split(str *sep=0, __ss_int maxsplit=-1);
    list<str *> *rsplit(str *sep = 0, __ss_int maxsplit = -1);
    tuple2<str *, str *> *rpartition(str *sep);
    tuple2<str *, str *> *partition(str *sep);
    list<str *> *splitlines(__ss_int keepends = 0);

    __ss_int __fixstart(__ss_int a, __ss_int b);
    __ss_int __checkneg(__ss_int i);

    __ss_int find(str *s, __ss_int a=0);
    __ss_int find(str *s, __ss_int a, __ss_int b);
    __ss_int rfind(str *s, __ss_int a=0);
    __ss_int rfind(str *s, __ss_int a, __ss_int b);

    __ss_int index(str *s, __ss_int a=0);
    __ss_int index(str *s, __ss_int a, __ss_int b);
    __ss_int rindex(str *s, __ss_int a=0);
    __ss_int rindex(str *s, __ss_int a, __ss_int b);

    __ss_int count(str *s, __ss_int start=0);
    __ss_int count(str *s, __ss_int start, __ss_int end);

    str *upper();
    str *lower();
    str *title();
    str *capitalize();
    str *casefold();

    str *replace(str *a, str *b, __ss_int c=-1);
    str *translate(str *table, str *delchars=0);
    str *swapcase();
    str *center(__ss_int width, str *fillchar=0);

    __ss_bool __ctype_function(int (*cfunc)(int));

    __ss_bool istitle();
    __ss_bool isspace();
    __ss_bool isalpha();
    __ss_bool isdigit();
    __ss_bool islower();
    __ss_bool isupper();
    __ss_bool isalnum();
    __ss_bool isprintable();
    __ss_bool isnumeric();
    __ss_bool __ss_isascii();
    __ss_bool isdecimal();
    __ss_bool isidentifier();

    __ss_bool startswith(str *s, __ss_int start=0);
    __ss_bool startswith(str *s, __ss_int start, __ss_int end);
    __ss_bool endswith(str *s, __ss_int start=0);
    __ss_bool endswith(str *s, __ss_int start, __ss_int end);

    str *zfill(__ss_int width);
    str *expandtabs(__ss_int tabsize=8);

    str *ljust(__ss_int width, str *fillchar=0);
    str *rjust(__ss_int width, str *fillchar=0);

    __ss_int __cmp__(pyobj *p);
    long __hash__();

    __ss_int __int__(); /* XXX compilation warning for int(pyseq<str *> *) */

    str *__iadd__(str *b);
    str *__imul__(__ss_int n);

    /* iteration */

    inline bool for_in_has_next(size_t i);
    inline str *for_in_next(size_t &i);

#ifdef __SS_BIND
    str(PyObject *p);
    PyObject *__to_py__();
#endif
};

void __throw_index_out_of_range();
void __throw_range_step_zero();
void __throw_set_changed();
void __throw_dict_changed();
void __throw_slice_step_zero();
void __throw_stop_iteration();

template<class K, class V> class dictentry;

const int MINSIZE = 8;

template<class K, class V> struct dict_looper {
    __ss_int pos;
    int si_used;
    dictentry<K,V> *entry;
};

template <class K, class V> class dict : public pyiter<K> {
public:
	int fill;
    int used;
    int mask;
    dictentry<K,V> *table;
    dictentry<K,V> smalltable[MINSIZE];

    dict();
    dict(int count, ...);
    template<class U> dict(U *other);
    dict(dict<K, V> *p);

    dict<K,V>& operator=(const dict<K,V>& other);

    void *__setitem__(K k, V v);
    V __getitem__(K k);
    void *__delitem__(K k);
    int do_discard(K key);
    __ss_int __len__();
    str *__repr__();
    __ss_bool has_key(K k);
    __ss_bool __contains__(K key);
    __ss_bool __contains__(dictentry<K,V>* entry);
    void *clear();
    dict<K,V> *copy();
    V get(K k);
    V get(K k, V v);
    V pop(K k);
    tuple2<K, V> *popitem();
    template <class U> void *update(U *other);
    void *update(dict<K, V> *e);

    __ss_bool __gt__(dict<K,V> *s);
    __ss_bool __lt__(dict<K,V> *s);
    __ss_bool __ge__(dict<K,V> *s);
    __ss_bool __le__(dict<K,V> *s);
    __ss_bool __eq__(pyobj *p);

    __ss_int __cmp__(pyobj *p);
    V setdefault(K k, V v=0);

    __dictiterkeys<K, V> *__iter__() { return new __dictiterkeys<K,V>(this);}
    __dictiterkeys<K, V> *keys() { return new __dictiterkeys<K,V>(this);}
    __dictitervalues<K, V> *values() { return new __dictitervalues<K,V>(this);}
    __dictiteritems<K, V> *items() { return new __dictiteritems<K,V>(this);}

    dict<K, V> *__deepcopy__(dict<void *, pyobj *> *memo);
    dict<K, V> *__copy__();

    void *__addtoitem__(K k, V v);

    /* iteration */

    typedef K for_in_unit;
    typedef dict_looper<K,V> for_in_loop;

    inline dict_looper<K,V> for_in_init() { dict_looper<K,V> l; l.pos = 0; l.si_used = used; return l; }
    inline bool for_in_has_next(dict_looper<K,V> &l) {
        if (l.si_used != used) {
            l.si_used = -1;
            __throw_dict_changed();
        }
        int ret = next(&l.pos, &l.entry);
        if (!ret) return false;
        return true;
    }
    inline K for_in_next(dict_looper<K,V> &l) { return l.entry->key; }

#ifdef __SS_BIND
    dict(PyObject *);
    PyObject *__to_py__();
#endif

    // used internally
    dictentry<K,V>* lookup(K key, long hash) const;
    void insert_key(K key, V value, long hash);
    void insert_clean(K key, V value, long hash);
    int next(__ss_int *pos_ptr, dictentry<K,V> **entry_ptr);
    void resize(int minused);
};

template<class T> struct setentry;

template<class T> struct set_looper {
    int pos;
    int si_used;
    setentry<T> *entry;
};

template<class T> class set : public pyiter<T> {
public:
    int frozen;
    int fill;
    int used;
    int mask;
    setentry<T> *table;
    setentry<T> smalltable[MINSIZE];
    long hash;

    template<class U> set(U *other, int frozen);
    template<class U> set(U *other);
    set(int frozen=0);

    set<T>& operator=(const set<T>& other);

    void *add(T key);
    void *add(setentry<T>* entry);
    void *discard(T key);
    int do_discard(T key);
    void *remove(T key);
    T pop();

    str* __repr__();

    __ss_bool __contains__(T key);
    __ss_bool __contains__(setentry<T>* entry);
    __ss_int __len__();

    void *clear();
    set<T> *copy();

    template <class U> void *update(int, U *other);
    void *update(int, set<T> *s);
    template <class U, class V> void *update(int, U *other, V *other2);
    template <class U, class V, class W> void *update(int, U *other, V *other2, W *other3);

    template <class U> set<T> *intersection(int, U *other);
    set<T> *intersection(int, set<T> *s);
    template <class U, class V> set<T> *intersection(int, U *iter, V *iter2);
    template <class U, class V, class W> set<T> *intersection(int, U *iter, V *iter2, W *iter3);

    template <class U> void *intersection_update(int, U *other);
    void *intersection_update(int, set<T> *s);
    template <class U, class V> void *intersection_update(int, U *other, V *other2);
    template <class U, class V, class W> void *intersection_update(int, U *other, V *other2, W *other3);

    template <class U> set<T> *difference(int, U *other);
    set<T> *difference(int, set<T> *s);
    template <class U, class V> set<T> *difference(int, U *other, V *other2);
    template <class U, class V, class W> set<T> *difference(int, U *other, V *other2, W *other3);

    template <class U> void *difference_update(int, U *other);
    void *difference_update(int, set<T> *s);
    template <class U, class V> void *difference_update(int, U *other, V *other2);
    template <class U, class V, class W> void *difference_update(int, U *other, V *other2, W *other3);

    set<T> *symmetric_difference(set<T> *s);
    void *symmetric_difference_update(set<T> *s);

    template <class U> set<T> *__ss_union(int, U *other);
    set<T> *__ss_union(int, set<T> *s);
    template <class U, class V> set<T> *__ss_union(int, U *other, V *other2);
    template <class U, class V, class W> set<T> *__ss_union(int, U *other, V *other2, W *other3);

    set<T> *__and__(set<T> *s);
    set<T> *__or__(set<T> *s);
    set<T> *__xor__(set<T> *s);
    set<T> *__sub__(set<T> *s);

    set<T> *__iand__(set<T> *s);
    set<T> *__ior__(set<T> *s);
    set<T> *__ixor__(set<T> *s);
    set<T> *__isub__(set<T> *s);

    __ss_bool issubset(pyiter<T> *s);
    __ss_bool issubset(set<T> *s);
    __ss_bool issuperset(set<T> *s);
    __ss_bool issuperset(pyiter<T> *s);

    __ss_bool isdisjoint(set<T> *s);
    __ss_bool isdisjoint(pyiter<T> *s);

    __ss_bool __gt__(set<T> *s);
    __ss_bool __lt__(set<T> *s);
    __ss_bool __ge__(set<T> *s);
    __ss_bool __le__(set<T> *s);
    __ss_bool __eq__(pyobj *p);

    __ss_int __cmp__(pyobj *p);

    __setiter<T> *__iter__() {
        return new __setiter<T>(this);
    }

    set<T> *__copy__();
    set<T> *__deepcopy__(dict<void *, pyobj *> *memo);

    /* iteration */

    typedef T for_in_unit;
    typedef set_looper<T> for_in_loop;

    inline set_looper<T> for_in_init() { set_looper<T> l; l.pos = 0; l.si_used = used; return l; }
    inline bool for_in_has_next(set_looper<T> &l) {
        if (l.si_used != used) {
            l.si_used = -1;
            __throw_set_changed();
        }
        int ret = next(&l.pos, &l.entry);
        if (!ret) return false;
        return true;
    }
    inline T for_in_next(set_looper<T> &l) { return l.entry->key; }

#ifdef __SS_BIND
    set(PyObject *);
    PyObject *__to_py__();
#endif

    long __hash__();

    // used internally
    setentry<T>* lookup(T key, long hash) const;
    void insert_key(T key, long hash);
    void insert_clean(T key, long hash);
    int next(int *pos_ptr, setentry<T> **entry_ptr);
    void resize(int minused);
};

class __ss_bool {
public:
    uint8_t value;
    inline __ss_int operator+(__ss_bool b);
    inline __ss_bool operator==(__ss_bool b);
    inline __ss_bool operator&(__ss_bool b);
    inline __ss_bool operator|(__ss_bool b);
    inline __ss_bool operator^(__ss_bool b);
    inline bool operator!();
    inline operator bool();
    inline __ss_bool& operator=(int a);
};

class complex {
public:
    __ss_float real, imag;

    inline complex operator+(complex b);
    inline complex operator+(__ss_float b);
    inline complex operator-(complex b);
    inline complex operator-(__ss_float b);
    inline complex operator*(complex b);
    inline complex operator*(__ss_float b);
    inline complex operator/(complex b);
    inline complex operator/(__ss_float b);
    inline complex operator%(complex b);
    inline complex operator%(__ss_float b);
    inline complex operator+();
    inline complex operator-();
    inline __ss_bool operator==(complex b);
    inline __ss_bool operator==(__ss_float b);
    inline __ss_bool operator!=(complex b);
    inline __ss_bool operator!=(__ss_float b);
    inline complex& operator=(__ss_float a);

    inline complex conjugate();
    complex parsevalue(str *s);

    inline long __hash__();
    str *__repr__();
};

complex mcomplex(__ss_float real=0.0, __ss_float imag=0.0);
template<class T> complex mcomplex(T t);
complex mcomplex(str *s);

inline complex operator+(__ss_float a, complex b) { return mcomplex(a)+b; }
inline complex operator-(__ss_float a, complex b) { return mcomplex(a)-b; }
inline complex operator*(__ss_float a, complex b) { return mcomplex(a)*b; }
inline complex operator/(__ss_float a, complex b) { return mcomplex(a)/b; }
inline complex operator%(__ss_float a, complex b) { return mcomplex(a)%b; }

inline __ss_bool operator==(__ss_float a, complex b) { return mcomplex(a)==b; }
inline __ss_bool operator!=(__ss_float a, complex b) { return mcomplex(a)!=b; }

class class_: public pyobj {
public:
    str *__name__;

    class_(const char *name);
    str *__repr__();
    __ss_bool __eq__(pyobj *c);

};

class int_ : public pyobj {
public:
    __ss_int unit;
    int_(__ss_int i);
    str *__repr__();
    __ss_bool __nonzero__();
};

class float_ : public pyobj {
public:
    __ss_float unit;
    float_(__ss_float f);
    str *__repr__();
    __ss_bool __nonzero__();
};

class bool_ : public pyobj {
public:
    __ss_bool unit;
    bool_(__ss_bool i);
    str *__repr__();
    __ss_bool __nonzero__();
    __ss_int __index__();
};

class complex_ : public pyobj {
public:
    complex unit;
    complex_(complex i);
    str *__repr__();
    __ss_bool __nonzero__();
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

template <class T> class __setiter : public __iter<T> {
public:
    set<T> *p;
    int pos;
    int si_used;
    int len;
    setentry<T>* entry;

    __setiter<T>(set<T> *p);
    T __next__();
};

class __xrange : public pyiter<__ss_int> {
public:
    __ss_int a, b, s;

    __xrange(__ss_int a, __ss_int b, __ss_int s);
    __iter<__ss_int> *__iter__();
    __ss_int __len__();
    __ss_int __getitem__(__ss_int i);
    str *__repr__();
};

template <class T> class __seqiter : public __iter<T> {
public:
    size_t counter, size;
    pyseq<T> *p;
    __seqiter<T>();
    __seqiter<T>(pyseq<T> *p);
    T __next__();
};

template <class K, class V> class __dictiterkeys : public __iter<K> {
public:
    dict<K,V> *p;
    __ss_int pos;
    int si_used;
    int len;
    dictentry<K,V>* entry;

    __dictiterkeys<K, V>(dict<K, V> *p);
    K __next__();

    inline str *__str__() { return new str("dict_keys"); }
};

template <class K, class V> class __dictitervalues : public __iter<V> {
public:
    dict<K,V> *p;
    __ss_int pos;
    int si_used;
    int len;
    dictentry<K,V>* entry;

    __dictitervalues<K, V>(dict<K, V> *p);
    V __next__();

    inline str *__str__() { return new str("dict_values"); }
};

template <class K, class V> class __dictiteritems : public __iter<tuple2<K, V> *> {
public:
    dict<K,V> *p;
    __ss_int pos;
    int si_used;
    int len;
    dictentry<K,V>* entry;

    __dictiteritems<K, V>(dict<K, V> *p);
    tuple2<K, V> *__next__();

    inline str *__str__() { return new str("dict_items"); }
};

static inline __ss_bool __mbool(bool c) { __ss_bool b; b.value=(int)c; return b; }

/* builtin function declarations */

template <class T> __iter<T> *___iter(pyiter<T> *p) {
    return p->__iter__();
}

file *open(str *name, str *flags = 0);
file *open(bytes *name, str *flags = 0);
file_binary *open_binary(str *name, str *flags = 0);
file_binary *open_binary(bytes *name, str *flags = 0); /* ugly duplication.. use str/byte template? */
str *input(str *msg = 0);

void print(int n, file *f, str *end, str *sep, ...);
void print2(file *f, int comma, int n, ...);

__xrange *range(__ss_int b);
__xrange *range(__ss_int a, __ss_int b, __ss_int s=1);

static inline __ss_float __portableround(__ss_float x) {
    if(x<0) return ceil(x-0.5);
    return floor(x+0.5);
}
inline __ss_float ___round(__ss_float a) {
    return __portableround(a);
}
inline __ss_float ___round(__ss_float a, int n) {
    return __portableround(pow((__ss_float)10,n)*a)/pow((__ss_float)10,n);
}

template<class T> inline T __abs(T t) { return t->__abs__(); }
#ifdef __SS_LONG
template<> inline __ss_int __abs(__ss_int a) { return a<0?-a:a; }
#endif
template<> inline int __abs(int a) { return a<0?-a:a; }
template<> inline __ss_float __abs(__ss_float a) { return a<0?-a:a; }
inline int __abs(__ss_bool b) { return b.value; }

template<class T> str *hex(T t) {
    return t->__hex__();
}
#ifdef __SS_LONG
template<> str *hex(__ss_int a);
#endif
template<> str *hex(int a);
template<> str *hex(__ss_bool b);

template<class T> str *oct(T t) {
    return t->__oct__();
}
#ifdef __SS_LONG
template<> str *oct(__ss_int a);
#endif
template<> str *oct(int a);
template<> str *oct(__ss_bool b);

template<class T> str *bin(T t) {
    return bin(t->__index__());
}
#ifdef __SS_LONG
template<> str *bin(__ss_int a);
#endif
template<> str *bin(int a);
template<> str *bin(__ss_bool b);

str *__mod4(str *fmt, list<pyobj *> *vals, bool bytes=false);
str *__modct(str *fmt, int n, ...);
bytes *__modct(bytes *fmt, int n, ...);
str *__modcd(str *fmt, list<str *> *l, ...);

template<class T> str *__modtuple(str *fmt, tuple2<T,T> *t);
template<class A, class B> str *__modtuple(str *fmt, tuple2<A,B> *t);

__ss_bool isinstance(pyobj *p, class_ *cl);

/* internal use */

#define __SS_MIN(a,b) ((a) < (b) ? (a) : (b))
#define __SS_MIN3(a,b,c) (__SS_MIN((a), __SS_MIN((b), (c))))
#define __SS_MAX(a,b) ((a) > (b) ? (a) : (b))
#define __SS_MAX3(a,b,c) (__SS_MAX((a), __SS_MAX((b), (c))))

void __init();
void __start(void (*initfunc)());
void __ss_exit(int code=0);

/* slicing */

static void inline slicenr(__ss_int x, __ss_int &l, __ss_int &u, __ss_int &s, __ss_int len);

#include "builtin/hash.hpp"
#include "builtin/compare.hpp"


template<class T> inline int __is_none(T *t) { return !t; }
template<class T> inline int __is_none(T) { return 0; }

/* externs */

extern class_ *cl_str_, *cl_int_, *cl_bool, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict, *cl_set, *cl_object, *cl_xrange, *cl_rangeiter, *cl_bytes;

extern __GC_VECTOR(str *) __char_cache;

extern list<str *> *__join_cache;
extern list<bytes *> *__join_cache_bin;

extern file *__ss_stdin, *__ss_stdout, *__ss_stderr;

/* set */

const int PERTURB_SHIFT = 5;

const int DISCARD_NOTFOUND = 0;
const int DISCARD_FOUND = 1;

const int unused = 0;
const int dummy = 1;
const int active = 2;

template<class T> struct setentry {
    long hash; // avoid rehashings...
    T key;
    int use;
};

template<class K, class V> struct dictentry {
    long hash;
    K key;
    V value;
    int use;
};

/* int */

inline __ss_int __int() { return 0; }
__ss_int __int(str *s, __ss_int base=10);
__ss_int __int(bytes *s, __ss_int base=10);

template<class T> inline __ss_int __int(T t) { return t->__int__(); }
#ifdef __SS_LONG
template<> inline __ss_int __int(__ss_int i) { return i; }
#endif
template<> inline __ss_int __int(int i) { return i; }
template<> inline __ss_int __int(str *s) { return __int(s, 10); }
template<> inline __ss_int __int(__ss_bool b) { return b.value; }
template<> inline __ss_int __int(__ss_float d) { return (__ss_int)d; }

/* float */

inline __ss_float __float() { return 0; }
template<class T> inline __ss_float __float(T t) { return t->__float__(); }
#ifdef __SS_LONG
template<> inline __ss_float __float(__ss_int p) { return p; }
#endif
template<> inline __ss_float __float(int p) { return p; }
template<> inline __ss_float __float(__ss_bool b) { return b.value; }
template<> inline __ss_float __float(__ss_float d) { return d; }
template<> __ss_float __float(str *s);

/* str */

template<class T> str *__str(T t) { if (!t) return new str("None"); return t->__str__(); }
template<> str *__str(__ss_float t);
#ifdef __SS_LONG
str *__str(__ss_int t, __ss_int base=10);
#endif
str *__str(int t, int base=10);
str *__str(__ss_bool b);
str *__str(void *);
str *__str();

str *__add_strs(int n, str *a, str *b, str *c);
str *__add_strs(int n, str *a, str *b, str *c, str *d);
str *__add_strs(int n, str *a, str *b, str *c, str *d, str *e);
str *__add_strs(int n, ...);

#include "builtin/iter.hpp"

/* bytes */

template<class T> bytes *__bytes(T *t) {
    if constexpr (std::is_base_of_v<pyiter<__ss_int>, T>) {
        bytes *b = new bytes();
        __ss_int e;
        typename T::for_in_loop __3;
        __ss_int __2;
        T *__1;
        FOR_IN(e,t,1,2,3)
            b->unit += (unsigned char)e;
        END_FOR
        return b;
    } else {
        if (!t)
            return new bytes("None");
        else
            return t->__bytes__();
    }
}

bytes *__bytes(bytes *b);
 bytes *__bytes(__ss_int t);
bytes *__bytes();

template<class T> bytes *__bytearray(T *t) {
    if constexpr (std::is_base_of_v<pyiter<__ss_int>, T>) {
        bytes *b = new bytes();
        b->frozen = 0;
        __ss_int e;
        typename pyiter<__ss_int>::for_in_loop __3;
        int __2;
        pyiter<__ss_int> *__1;
        FOR_IN(e,t,1,2,3)
            b->unit += (unsigned char)e;
        END_FOR
        return b;
    } else {
        if (!t)
            return new bytes("None");
        else
            return t->__bytes__();
    }
}

bytes *__bytearray(bytes *b);
bytes *__bytearray(__ss_int t);
bytes *__bytearray();

/* repr */

template<class T> str *repr(T t) { if (!t) return new str("None"); return t->__repr__(); }
template<> str *repr(__ss_float t);
#ifdef __SS_LONG
template<> str *repr(__ss_int t);
#endif
template<> str *repr(int t);
template<> str *repr(__ss_bool b);
template<> str *repr(void *t);

#ifndef __SS_NOASSERT
#define ASSERT(x, y) if(!(x)) throw new AssertionError(y);
#else
#define ASSERT(x, y)
#endif


/* len */

template<class T> inline __ss_int len(T x) { return x->__len__(); }
template<class T> inline __ss_int len(list<T> *x) { return x->units.size(); } /* XXX more general solution? */

#include "builtin/bool.hpp"
#include "builtin/exception.hpp"
#include "builtin/extmod.hpp"


/* file objects */

struct __file_options {
    char lastchar;
    int space;
    bool universal_mode;
    bool cr;
    __file_options() : lastchar('\n'), space(0), universal_mode(false), cr(false) {}
};

class file : public __iter<str *> {
public:
    str *name;
    str *mode;

    FILE *f;
    file_binary *buffer;

    __ss_int closed;
    __file_options options;
    __GC_VECTOR(char) __read_cache;

    file(FILE *g=0) : f(g) {}
    file(str *name, str *mode=0);

    virtual void * close();
    virtual void * flush();
    virtual int  __ss_fileno();
    virtual __ss_bool isatty();
    virtual str *  read(int n=-1);
    virtual str *  readline(int n=-1);
    list<str *> *  readlines(__ss_int size_hint=-1);
    virtual void * seek(__ss_int i, __ss_int w=0);
    virtual __ss_int tell();
    virtual void * truncate(int size);
    virtual void * write(str *s);
    virtual void * writelines(pyiter<str *> *iter);
    __iter<str *> *xreadlines();
    virtual void __enter__();
    virtual void __exit__();

    virtual __iter<str *> *__iter__();
    virtual str *  __next__();

    virtual str *__repr__();

    virtual bool __eof();
    virtual bool __error();

    inline void __check_closed() {
        if(closed)
            throw new ValueError(new str("I/O operation on closed file"));
    }
};

/* TODO file<bytes *> template? */

class file_binary : public __iter<bytes *> {
public:
    str *name;
    str *mode;

    FILE *f;
    __ss_int closed;
    __file_options options;
    __GC_VECTOR(char) __read_cache;

    file_binary(FILE *g=0) : f(g) {}
    file_binary(str *name, str *mode=0);

    virtual void * close();
    virtual void * flush();
    virtual int  __ss_fileno();
    virtual __ss_bool isatty();
    virtual bytes *  read(int n=-1);
    virtual bytes *  readline(int n=-1);
    list<bytes *> *  readlines(__ss_int size_hint=-1);
    virtual void * seek(__ss_int i, __ss_int w=0);
    virtual __ss_int tell();
    virtual void * truncate(int size);
    virtual void * write(bytes *b);
    virtual void *writelines(pyiter<bytes *> *iter);
    __iter<bytes *> *xreadlines();
    virtual void __enter__();
    virtual void __exit__();
    virtual str *__repr__();

    virtual __iter<bytes *> *__iter__();
    virtual bytes *  __next__();

    virtual bool __eof();
    virtual bool __error();

    inline void __check_closed() {
        if(closed)
            throw new ValueError(new str("I/O operation on closed file"));
    }
};

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

template<class T> static inline int __wrap(T a, __ss_int i) {
    __ss_int l = len(a);
#ifndef __SS_NOWRAP
    if(i<0) i += l;
#endif
#ifndef __SS_NOBOUNDS
        if(i<0 || i>= l)
            __throw_index_out_of_range();
#endif
    return i;
}


/* copy */

template<class T> T __copy(T t) {
    if(!t)
        return (T)NULL;
    return (T)(t->__copy__());
}

#ifdef __SS_LONG
template<> inline __ss_int __copy(__ss_int i) { return i; }
#endif
template<> inline int __copy(int i) { return i; }
template<> inline __ss_bool __copy(__ss_bool b) { return b; }
template<> inline __ss_float __copy(__ss_float d) { return d; }
template<> inline void *__copy(void *p) { return p; }

template<class T> T __deepcopy(T t, dict<void *, pyobj *> *memo=0) {
    if(!t)
        return (T)NULL;

    if(!memo)
        memo = new dict<void *, pyobj *>();
    T u = (T)(memo->get(t, 0));
    if(u)
       return u;

    return (T)(t->__deepcopy__(memo));
}

#ifdef __SS_LONG
template<> inline __ss_int __deepcopy(__ss_int i, dict<void *, pyobj *> *) { return i; }
#endif
template<> inline int __deepcopy(int i, dict<void *, pyobj *> *) { return i; }
template<> inline __ss_bool __deepcopy(__ss_bool b, dict<void *, pyobj *> *) { return b; }
template<> inline __ss_float __deepcopy(__ss_float d, dict<void *, pyobj *> *) { return d; }
template<> inline void *__deepcopy(void *p, dict<void *, pyobj *> *) { return p; }

/* and, or, not */

#define __OR(a, b, t) ((___bool(__ ## t = a))?(__ ## t):(b))
#define __AND(a, b, t) ((!___bool(__ ## t = a))?(__ ## t):(b))
#define __NOT(x) (__mbool(!(x)))

/* 'zero' value for type */

template<class T> T __zero() { return 0; }
template<> inline __ss_bool __zero<__ss_bool>() { return False; }
template<> inline complex __zero<complex>() { return mcomplex(0,0); }

#include "builtin/list.hpp"
#include "builtin/tuple.hpp"
#include "builtin/str.hpp"
#include "builtin/bytes.hpp"
#include "builtin/math.hpp"
#include "builtin/dict.hpp"
#include "builtin/set.hpp"
#include "builtin/file.hpp"
#include "builtin/format.hpp"
#include "builtin/function.hpp"
#include "builtin/complex.hpp"

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
    return __getitem__(i++);
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
template<class T> __seqiter<T>::__seqiter(pyseq<T> *p) {
    this->p = p;
    size = p->__len__();
    counter = 0;
}

template<class T> T __seqiter<T>::__next__() {
    if(counter==size)
        __throw_stop_iteration();
    return p->__getitem__(counter++);
}


/* slicing */

static void inline slicenr(__ss_int x, __ss_int &l, __ss_int &u, __ss_int &s, __ss_int len) {
    if(x&4) {
        if (s == 0)
            __throw_slice_step_zero();
    } else
        s = 1;

    if (l>=len)
        l = len;
    else if (l<0) {
        l = len+l;
        if(l<0)
            l = 0;
    }
    if (u>=len)
        u = len;
    else if (u<0) {
        u = len+u;
        if(u<0)
            u = 0;
    }

    if(s<0) {
        if (!(x&1))
            l = len-1;
        if (!(x&2))
            u = -1;
    }
    else {
        if (!(x&1))
            l = 0;
        if (!(x&2))
            u = len;
    }
}

template<class T> void __unpack_check(T t, int expected) {
    if(len(t) > (__ss_int)expected)
	 throw new ValueError(new str("too many values to unpack"));
    else if(len(t) < (__ss_int)expected)
	 throw new ValueError(new str("not enough values to unpack"));
}

} // namespace __shedskin__
#endif
