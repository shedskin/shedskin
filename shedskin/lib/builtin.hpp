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
#include <fstream>
#include <sstream>
#include <cstdarg>
#include <cstring>
#include <cmath>
#include <algorithm>
#include <iterator>
#include <ctype.h>

#if defined( _MSC_VER )
    #pragma warning( disable : 4996 ) // CRT security warning
    #pragma warning( disable : 4800 ) // forcing bool
    #pragma warning( disable : 4101 ) // unreferences var
    #pragma warning( disable : 4396 ) // can't use inline
    #pragma warning( disable : 4099 ) // mixing struct and class defs
    #pragma warning( disable : 4715 ) // not all paths return a value
    #include <unordered_map>
    #include <limits>
#else
    #include <ext/hash_map>
#endif

namespace __shedskin__ {

/* integer type */

#ifdef __SS_LONG
    typedef long long __ss_int;
#else
    typedef int __ss_int;
#endif

/* forward class declarations */

class pyobj;
class class_;
class str;
class int_;
class __ss_bool;
class float_;
class file;
class bool_;
class complex;

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
class __xrange;
class __rangeiter;

class BaseException;
class Exception;
class StandardError;
class AssertionError;
class KeyError;
class ValueError;
class IndexError;
class NotImplementedError;
class IOError;
class OSError;
class SyntaxError;
class StopIteration;
class TypeError;
class RuntimeError;
class OverflowError;

/* STL types */

template<class T> class hashfunc;
template<class T> class hasheq;

#define __GC_VECTOR(T) std::vector< T, gc_allocator< T > >
#define __GC_DEQUE(T) std::deque< T, gc_allocator< T > >
#define __GC_STRING std::basic_string<char,std::char_traits<char>,gc_allocator<char> >

/* builtin class declarations */

class pyobj : public gc {
public:
    class_ *__class__;

    virtual str *__repr__();
    virtual str *__str__();

    virtual int __hash__();
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
    typedef int for_in_loop;

    inline int for_in_init();
    inline bool for_in_has_next(int i);
    inline T for_in_next(int &i);

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

    inline bool for_in_has_next(int i);
    inline T for_in_next(int &i);
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

    __ss_bool __eq__(tuple2<A,B> *b);
    __ss_int __cmp__(pyobj *p);
    int __hash__();

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

    int __hash__();

    tuple2<T,T> *__deepcopy__(dict<void *, pyobj *> *memo);
    tuple2<T,T> *__copy__();

    /* iteration */

    inline bool for_in_has_next(int i);
    inline T for_in_next(int &i);

#ifdef __SS_BIND
    tuple2(PyObject *p);
    PyObject *__to_py__();
#endif
};

class str : public pyseq<str *> {
public:
    __GC_STRING unit;
    bool charcache;
    long hash;

    str();
    str(const char *s);
    str(__GC_STRING s);
    str(const char *s, int size); /* '\0' delimiter in C */

    __ss_bool __contains__(str *s);
    str *strip(str *chars=0);
    str *lstrip(str *chars=0);
    str *rstrip(str *chars=0);
    list<str *> *split(str *sep=0, int maxsplit=-1);
    __ss_bool __eq__(pyobj *s);
    str *__add__(str *b);

    str *__join(pyseq<str *> *l, bool only_ones, int total);
    template<class U> str *join(U *);
    str *join(list<str *> *); /* XXX why can't we use pyseq<str *> *? */
    str *join(tuple2<str *, str *> *);

    str *__str__();
    str *__repr__();
    str *__mul__(__ss_int n);
    inline str *__getitem__(__ss_int n);
    inline str *__getfast__(__ss_int i);
    inline __ss_int __len__();
    str *__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s);

    list<str *> *rsplit(str *sep = 0, int maxsplit = -1);
    tuple2<str *, str *> *rpartition(str *sep);
    tuple2<str *, str *> *partition(str *sep);
    list<str *> *splitlines(int keepends = 0);

    int __fixstart(int a, int b);
    int __checkneg(int i);

    int find(str *s, int a=0);
    int find(str *s, int a, int b);
    int rfind(str *s, int a=0);
    int rfind(str *s, int a, int b);
    int index(str *s, int a=0);
    int index(str *s, int a, int b);
    int rindex(str *s, int a=0);
    int rindex(str *s, int a, int b);

    __ss_int count(str *s, __ss_int start=0);
    __ss_int count(str *s, __ss_int start, __ss_int end);

    str *upper();
    str *lower();
    str *title();
    str *capitalize();
    str *replace(str *a, str *b, int c=-1);
    str *translate(str *table, str *delchars=0);
    str *swapcase();
    str *center(int w, str *fill=0);

    __ss_bool __ctype_function(int (*cfunc)(int));

    __ss_bool istitle();
    __ss_bool isspace();
    __ss_bool isalpha();
    __ss_bool isdigit();
    __ss_bool islower();
    __ss_bool isupper();
    __ss_bool isalnum();

    __ss_bool startswith(str *s, __ss_int start=0);
    __ss_bool startswith(str *s, __ss_int start, __ss_int end);
    __ss_bool endswith(str *s, __ss_int start=0);
    __ss_bool endswith(str *s, __ss_int start, __ss_int end);

    str *zfill(int width);
    str *expandtabs(int width=8);

    str *ljust(int width, str *fchar=0);
    str *rjust(int width, str *fchar=0);

    __ss_int __cmp__(pyobj *p);
    int __hash__();

    __ss_int __int__(); /* XXX compilation warning for int(pyseq<str *> *) */

    str *__iadd__(str *b);
    str *__imul__(__ss_int n);

    /* iteration */

    inline bool for_in_has_next(int i);
    inline str *for_in_next(int &i);

#ifdef __SS_BIND
    str(PyObject *p);
    PyObject *__to_py__();
#endif
};

template<class K, class V> class dictentry;

const int MINSIZE = 8;

template<class K, class V> struct dict_looper {
    int pos;
    int si_used;
    dictentry<K,V> *entry;
};

static void __throw_dict_changed();

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
    list<K> *keys();
    list<V> *values();
    list<tuple2<K, V> *> *items();
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
    __dictiterkeys<K, V> *iterkeys() { return new __dictiterkeys<K,V>(this);}
    __dictitervalues<K, V> *itervalues() { return new __dictitervalues<K,V>(this);}
    __dictiteritems<K, V> *iteritems() { return new __dictiteritems<K,V>(this);}

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
    int next(int *pos_ptr, dictentry<K,V> **entry_ptr);
    void resize(int minused);
};

template<class T> struct setentry;

template<class T> struct set_looper {
    int pos;
    int si_used;
    setentry<T> *entry;
};

static void __throw_set_changed();

template<class T> class set : public pyiter<T> {
public:
    int frozen;
    int fill;
    int used;
    int mask;
    setentry<T> *table;
    setentry<T> smalltable[MINSIZE];
    int hash;

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

    template <class U> void *update(U *other);
    void *update(set<T> *other);

    void *difference_update(set<T> *s);
    void *intersection_update(set<T> *s);
    void *symmetric_difference_update(set<T> *s);

    set<T> *intersection(set<T> *s);
    set<T> *__ss_union(pyiter<T> *s);
    set<T> *__ss_union(set<T> *s);
    set<T> *symmetric_difference(set<T> *s);
    set<T> *difference(set<T> *other);

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

    int __hash__();

    // used internally
    setentry<T>* lookup(T key, long hash) const;
    void insert_key(T key, long hash);
    void insert_clean(T key, long hash);
    int next(int *pos_ptr, setentry<T> **entry_ptr);
    void resize(int minused);
};

struct print_options {
    int endoffile;
    char lastchar;
    int space;
    print_options() {
        lastchar = '\n';
        space = 0;
    }
};

class file : public pyiter<str *> {
public:
    FILE *f;
    print_options print_opt;

    str *name;
    str *mode;
    __ss_int closed;

    bool universal_mode;
    bool cr;

    file(str *name, str *mode=0);
    file(FILE *g);
    file();

    str *read(int n=-1);
    str *readline(int n=-1);
    list<str *> *readlines();
    void *write(str *s);
    template<class U> void *writelines(U *iter);
    void *flush();
    int __ss_fileno();

    void __check_closed();

    virtual int getchar();
    virtual void *putchar(int c);
    virtual void *seek(__ss_int i, __ss_int w=0);
    virtual void *close();

    __ss_int tell();

    void __enter__();
    void __exit__();

    str *__repr__();

    __iter<str *> *__iter__();
    str *next();
};

class __ss_bool {
public:
    int value;
    inline __ss_int operator+(__ss_bool b);
    inline __ss_bool operator==(__ss_bool b);
    inline __ss_bool operator&(__ss_bool b);
    inline __ss_bool operator|(__ss_bool b);
    inline __ss_bool operator^(__ss_bool b);
    inline bool operator!();
    inline operator bool();
};

class complex : public pyobj {
public:
    double real, imag;

    complex(double real=0.0, double imag=0.0);
    template<class T> complex(T t);
    complex(str *s);

    complex *__add__(complex *b);
    complex *__add__(double b);
    complex *__iadd__(complex *b);
    complex *__iadd__(double b);

    complex *__sub__(complex *b);
    complex *__sub__(double b);
    complex *__rsub__(double b);
    complex *__isub__(complex *b);
    complex *__isub__(double b);

    complex *__mul__(complex *b);
    complex *__mul__(double b);
    complex *__imul__(complex *b);
    complex *__imul__(double b);

    complex *__div__(complex *b);
    complex *__div__(double b);
    complex *__rdiv__(double b);
    complex *__idiv__(complex *b);
    complex *__idiv__(double b);

    complex *__floordiv__(complex *b);
    complex *__floordiv__(double b);
    complex *__mod__(complex *b);
    complex *__mod__(double b);
    tuple2<complex *, complex *> *__divmod__(complex *b);
    tuple2<complex *, complex *> *__divmod__(double b);

    complex *conjugate();
    complex *__pos__();
    complex *__neg__();
    double __abs__();

    str *__repr__();

    complex *parsevalue(str *s);

    __ss_bool __eq__(pyobj *p);
    int __hash__();
    __ss_bool __nonzero__();

#ifdef __SS_BIND
    complex(PyObject *);
    PyObject *__to_py__();
#endif
};

class class_: public pyobj {
public:
    int low, high;
    str *__name__;

    class_(const char *name, int low, int high);
    str *__repr__();
    __ss_bool __eq__(pyobj *c);

};

class int_ : public pyobj {
public:
    __ss_int unit;
    int_(__ss_int i);
    str *__repr__();
};

class float_ : public pyobj {
public:
    double unit;
    float_(double f);
    str *__repr__();
};

class bool_ : public pyobj {
public:
    __ss_bool unit;
    bool_(__ss_bool i);
    str *__repr__();
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
    virtual T next(); /* __get_next can be overloaded to avoid (slow) exception handling */
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
    T next();
};

class __fileiter : public __iter<str *> {
public:
    file *p;
    __fileiter(file *p);
    str *next();
};

class __xrange : public pyiter<__ss_int> {
public:
    __ss_int a, b, s;

    __xrange(__ss_int a, __ss_int b, __ss_int s);
    __iter<__ss_int> *__iter__();
    __ss_int __len__();
    str *__repr__();
};

template <class T> class __seqiter : public __iter<T> {
public:
    unsigned int counter;
    int size;
    pyseq<T> *p;
    __seqiter<T>();
    __seqiter<T>(pyseq<T> *p);
    T next();
};

template <class K, class V> class __dictiterkeys : public __iter<K> {
public:
    dict<K,V> *p;
    int pos;
    int si_used;
    int len;
    dictentry<K,V>* entry;

    __dictiterkeys<K, V>(dict<K, V> *p);
    K next();
};

template <class K, class V> class __dictitervalues : public __iter<V> {
public:
    dict<K,V> *p;
    int pos;
    int si_used;
    int len;
    dictentry<K,V>* entry;

    __dictitervalues<K, V>(dict<K, V> *p);
    V next();
};

template <class K, class V> class __dictiteritems : public __iter<tuple2<K, V> *> {
public:
    dict<K,V> *p;
    int pos;
    int si_used;
    int len;
    dictentry<K,V>* entry;

    __dictiteritems<K, V>(dict<K, V> *p);
    tuple2<K, V> *next();
};

static inline __ss_bool __mbool(bool c) { __ss_bool b; b.value=(int)c; return b; }

/* builtin function declarations */

template <class T> __iter<T> *___iter(pyiter<T> *p) {
    return p->__iter__();
}

file *open(str *name, str *flags = 0);
str *raw_input(str *msg = 0);

void print(int n, file *f, str *end, str *sep, ...);
void print2(file *f, int comma, int n, ...);

__ss_bool isinstance(pyobj *, class_ *);
__ss_bool isinstance(pyobj *, tuple2<class_ *, class_ *> *);

list<__ss_int> *range(__ss_int b);
list<__ss_int> *range(__ss_int a, __ss_int b, __ss_int s=1);

__xrange *xrange(__ss_int b);
__xrange *xrange(__ss_int a, __ss_int b, __ss_int s=1);

static inline double __portableround(double x) {
    if(x<0) return ceil(x-0.5);
    return floor(x+0.5);
}
inline double ___round(double a) {
    return __portableround(a);
}
inline double ___round(double a, int n) {
    return __portableround(pow((double)10,n)*a)/pow((double)10,n);
}

template<class T> inline T __abs(T t) { return t->__abs__(); }
#ifdef __SS_LONG
template<> inline __ss_int __abs(__ss_int a) { return a<0?-a:a; }
#endif
template<> inline int __abs(int a) { return a<0?-a:a; }
template<> inline double __abs(double a) { return a<0?-a:a; }
inline int __abs(__ss_bool b) { return __abs(b.value); }
double __abs(complex *c);

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

str *__mod4(str *fmt, list<pyobj *> *vals);
str *__modct(str *fmt, int n, ...);
str *__modcd(str *fmt, list<str *> *l, ...);

template<class T> str *__modtuple(str *fmt, tuple2<T,T> *t);
template<class A, class B> str *__modtuple(str *fmt, tuple2<A,B> *t);

/* internal use */

#ifdef __sun
#define INFINITY __builtin_inff()
#endif
#if defined( _MSC_VER )
#define INFINITY std::numeric_limits<double>::infinity()
#endif

#define __SS_MIN(a,b) ((a) < (b) ? (a) : (b))
#define __SS_MIN3(a,b,c) (__SS_MIN((a), __SS_MIN((b), (c))))
#define __SS_MAX(a,b) ((a) > (b) ? (a) : (b))
#define __SS_MAX3(a,b,c) (__SS_MAX((a), __SS_MAX((b), (c))))

void __init();
void __start(void (*initfunc)());
void __ss_exit(int code=0);

/* slicing */

static void inline slicenr(__ss_int x, __ss_int &l, __ss_int &u, __ss_int &s, __ss_int len);

/* hashing */

static inline int hash_combine(int seed, int other) {
    return seed ^ (other + 0x9e3779b9 + (seed << 6) + (seed >> 2));
}

template<class T> inline int hasher(T t) {
    if(t == NULL) return 0;
    return t->__hash__();
}
#ifdef __SS_LONG
template<> inline int hasher(__ss_int a) { return (a==-1)?-2:a; }
#endif
template<> inline int hasher(int a) { return (a==-1)?-2:a; }
template<> inline int hasher(__ss_bool a) { return a.value; }
template<> inline int hasher(void *a) { return (intptr_t)a; }
template<> inline int hasher(double v) {
    long hipart, x; /* modified from CPython */
    int expo;
    v = frexp(v, &expo);
    v *= 2147483648.0; /* 2**31 */
    hipart = (long)v;   /* take the top 32 bits */
    v = (v - (double)hipart) * 2147483648.0; /* get the next 32 bits */
    x = hipart + (long)v + (expo << 15);
    if (x== -1)
        x = -2;
    return x;
}

template<class T> class hashfunc
{
public:
    int operator()(T t) const { return hasher<T>(t); }
};

template<class T> class hasheq {
public:
    int operator()(T t, T v) const { return __eq(t, v); }
};

/* comparison */

template<class T> inline __ss_int __cmp(T a, T b) {
    if (!a) return -1;
    return a->__cmp__(b);
}

#ifdef __SS_LONG
template<> inline __ss_int __cmp(__ss_int a, __ss_int b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}
#endif

template<> inline __ss_int __cmp(int a, int b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}

template<> inline __ss_int __cmp(__ss_bool a, __ss_bool b) {
    return __cmp(a.value, b.value); /* XXX */
}

template<> inline __ss_int __cmp(double a, double b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}
template<> inline __ss_int __cmp(void *a, void *b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}

template<class T> __ss_int cpp_cmp(T a, T b) {
    return __cmp(a, b) == -1;
}
template<class T> __ss_int cpp_cmp_rev(T a, T b) {
    return __cmp(a, b) == 1;
}
template<class T> class cpp_cmp_custom {
    typedef __ss_int (*hork)(T, T);
    hork cmp;
public:
    cpp_cmp_custom(hork a) { cmp = a; }
    __ss_int operator()(T a, T b) const { return cmp(a,b) == -1; }
};
template<class T> class cpp_cmp_custom_rev {
    typedef __ss_int (*hork)(T, T);
    hork cmp;
public:
    cpp_cmp_custom_rev(hork a) { cmp = a; }
    __ss_int operator()(T a, T b) const { return cmp(a,b) == 1; }
};
template<class T, class V> class cpp_cmp_key {
    typedef V (*hork)(T);
    hork key;
public:
    cpp_cmp_key(hork a) { key = a; }
    __ss_int operator()(T a, T b) const { return __cmp(key(a), key(b)) == -1; }
};
template<class T, class V> class cpp_cmp_key_rev {
    typedef V (*hork)(T);
    hork key;
public:
    cpp_cmp_key_rev(hork a) { key = a; }
    __ss_int operator()(T a, T b) const { return __cmp(key(a), key(b)) == 1; }
};

template<class T> struct dereference {};
template<class T> struct dereference <T*> {
    typedef T type;
};

template<class T> inline int __is_none(T *t) { return !t; }
template<class T> inline int __is_none(T t) { return 0; }

/* binding */

#ifdef __SS_BIND
template<class T> T __to_ss(PyObject *p) {
    if(p==Py_None) return (T)NULL;
    return new (typename dereference<T>::type)(p); /* isn't C++ pretty :-) */
}

#ifdef __SS_LONG
template<> __ss_int __to_ss(PyObject *p);
#endif
template<> int __to_ss(PyObject *p);
template<> __ss_bool __to_ss(PyObject *p);
template<> double __to_ss(PyObject *p);
template<> void *__to_ss(PyObject *p);

template<class T> PyObject *__to_py(T t) {
    if(!t) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return t->__to_py__();
}

#ifdef __SS_LONG
template<> PyObject *__to_py(__ss_int i);
#endif
template<> PyObject *__to_py(int i);
template<> PyObject *__to_py(__ss_bool i);
template<> PyObject *__to_py(double i);
template<> PyObject *__to_py(void *);

extern dict<void *, void *> *__ss_proxy;
#endif

/* externs */

extern class_ *cl_str_, *cl_int_, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict, *cl_set, *cl_object, *cl_xrange, *cl_rangeiter;

extern __GC_VECTOR(str *) __char_cache;

extern __ss_bool True;
extern __ss_bool False;

extern list<str *> *__join_cache;

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
__ss_int __int(str *s, __ss_int base);

template<class T> inline __ss_int __int(T t) { return t->__int__(); }
#ifdef __SS_LONG
template<> inline __ss_int __int(__ss_int i) { return i; }
#endif
template<> inline __ss_int __int(int i) { return i; }
template<> inline __ss_int __int(str *s) { return __int(s, 10); }
template<> inline __ss_int __int(__ss_bool b) { return b.value; }
template<> inline __ss_int __int(double d) { return (__ss_int)d; }

/* float */

inline double __float() { return 0; }
template<class T> inline double __float(T t) { return t->__float__(); }
#ifdef __SS_LONG
template<> inline double __float(__ss_int p) { return p; }
#endif
template<> inline double __float(int p) { return p; }
template<> inline double __float(__ss_bool b) { return __float(b.value); }
template<> inline double __float(double d) { return d; }
template<> double __float(str *s);

/* str */

str *__str();
template<class T> str *__str(T t);
template<> str *__str(double t);
#ifdef __SS_LONG
str *__str(__ss_int t, __ss_int base=10);
#endif
str *__str(int t, int base=10);
str *__str(__ss_bool b);

template<class T> str *repr(T t);
template<> str *repr(double t);
#ifdef __SS_LONG
template<> str *repr(__ss_int t);
#endif
template<> str *repr(int t);
template<> str *repr(__ss_bool b);
template<> str *repr(void *t);

/* exceptions */

class BaseException : public pyobj {
public:
    str *msg;
    BaseException(str *msg=0) { __init__(msg); }

    void __init__(str *msg) { this->msg = msg; }
    void __init__(void *) { this->msg = 0; } /* XXX */
    void __init__(int) { this->msg = 0; } /* XXX */
    str *__repr__() { return msg ? msg : new str("0"); }
};

class Exception: public BaseException {
public:
    Exception(str *msg=0) : BaseException(msg) {}

#ifdef __SS_BIND
   virtual PyObject *__to_py__() { return PyExc_Exception; }
#endif
};

class StopIteration : public Exception {
public:
    StopIteration(str *msg=0) : Exception(msg) {}
};
class StandardError : public Exception {
public:
    StandardError(str *msg=0) : Exception(msg) {}
};

class AssertionError : public StandardError {
public:
    AssertionError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_AssertionError; }
#endif
};

class EOFError : public StandardError {
public:
    EOFError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_EOFError; }
#endif
};

class FloatingPointError : public StandardError {
public:
    FloatingPointError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_FloatingPointError; }
#endif
};

class KeyError : public StandardError {
public:
    KeyError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_KeyError; }
#endif
};

class IndexError : public StandardError {
public:
    IndexError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_IndexError; }
#endif
};

class TypeError : public StandardError {
public:
    TypeError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_TypeError; }
#endif
};

class IOError : public StandardError {
public:
    int __ss_errno;
    str *filename;
    str *message;
    str *strerror;

    IOError(str *msg=0);
    str *__str__();
    str *__repr__();

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_IOError; }
#endif
};

class KeyboardInterrupt : public BaseException {
public:
    KeyboardInterrupt(str *msg=0) : BaseException(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_KeyboardInterrupt; }
#endif
};

class MemoryError : public StandardError {
public:
    MemoryError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_MemoryError; }
#endif
};

class NameError : public StandardError {
public:
    NameError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NameError; }
#endif
};

class NotImplementedError : public StandardError {
public:
    NotImplementedError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NotImplementedError; }
#endif
};

class OSError : public StandardError {
public:
    int __ss_errno;
    str *filename;
    str *message;
    str *strerror;

    OSError(str *message=0);
    str *__str__();
    str *__repr__();

#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OSError; }
#endif
};

class OverflowError : public StandardError {
public:
    OverflowError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OverflowError; }
#endif
};

class RuntimeError : public StandardError {
public:
    RuntimeError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_RuntimeError; }
#endif
};

class SyntaxError : public StandardError {
public:
    SyntaxError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SyntaxError; }
#endif
};

class SystemError : public StandardError {
public:
    SystemError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SystemError; }
#endif
};

class SystemExit : public BaseException {
public:
    int code;
    str *message;
    SystemExit(str *msg) { this->message = msg; this->msg = msg; this->code = 1; }
    SystemExit(__ss_int code) { this->message = NULL; this->msg = __str(code); this->code = code; }
    SystemExit() { this->message = NULL; this->msg = __str(0); this->code = 0; }
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SystemExit; }
#endif
};

class ValueError : public StandardError {
public:
    ValueError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ValueError; }
#endif
};

class ZeroDivisionError : public StandardError {
public:
    ZeroDivisionError(str *msg=0) : StandardError(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ZeroDivisionError; }
#endif
};

#ifndef __SS_NOASSERT
#define ASSERT(x, y) if(!(x)) throw new AssertionError(y);
#else
#define ASSERT(x, y)
#endif

static void __throw_index_out_of_range() { /* improve inlining */
   throw new IndexError(new str("index out of range"));
}
static void __throw_range_step_zero() {
    throw new ValueError(new str("range() step argument must not be zero"));
}
static void __throw_set_changed() {
    throw new RuntimeError(new str("set changed size during iteration"));
}
static void __throw_dict_changed() {
    throw new RuntimeError(new str("dict changed size during iteration"));
}
static void __throw_slice_step_zero() {
    throw new ValueError(new str("slice step cannot be zero"));
}
static void __throw_stop_iteration() {
    throw new StopIteration();
}

#define FAST_FOR(i, l, u, s, t1, t2) \
    if(s==0) \
        __throw_range_step_zero(); \
    for(__ ## t1 = l, __ ## t2 = u; ; __ ## t1 += s) { \
        if (s >= 0) { if (__ ## t1 >= __ ## t2) break; } \
        else { if (__ ## t1 <= __ ## t2) break; } \
        i=__ ## t1; \

#define FOR_IN_NEW(e, iter, temp, i, t) \
    __ ## temp = iter; \
    __ ## i = -1; \
    __ ## t = __ ## temp->for_in_init(); \
    while(__ ## temp->for_in_has_next(__ ## t)) \
    { \
        __ ## i ++; \
        e = __ ## temp->for_in_next(__ ## t);

#define FOR_IN_ZIP(a,b, k,l, t,u, n,m) \
    __ ## m = __SS_MIN(k->units.size(), l->units.size()); \
    __ ## t = k; \
    __ ## u = l; \
    for(__ ## n = 0; __ ## n < __ ## m; __ ## n ++) { \
        a = (__ ## t)->units[__ ## n]; \
        b = (__ ## u)->units[__ ## n];

#define FOR_IN_ENUM(i, m, temp, n) \
    __ ## temp = m; \
    for(__ ## n = 0; (unsigned int)__ ## n < (__ ## temp)->units.size(); __ ## n ++) { \
        i = (__ ## temp)->units[__ ## n]; \

#define END_FOR }

/* deprecated by FOR_IN_NEW */

#define FOR_IN_SEQ(i, m, temp, n) \
    __ ## temp = m; \
    for(__ ## n = 0; (unsigned int)__ ## n < (__ ## temp)->units.size(); __ ## n ++) { \
        i = (__ ## temp)->units[__ ## n]; \

/* typeof for MSVC */

#if defined(_MSC_VER) && _MSC_VER>=1400
namespace msvc_typeof_impl {
	/* This is a fusion of Igor Chesnokov's method (http://rsdn.ru/forum/src/1094305.aspx)
	and Steven Watanabe's method (http://lists.boost.org/Archives/boost/2006/12/115006.php)

	How it works:
	C++ allows template type inference for templated function parameters but nothing else.
	What we do is to pass the expression sent to typeof() into the templated function vartypeID()
	as its parameter, thus extracting its type. The big problem traditionally now is how to get
	that type out of the vartypeID() instance, and here's how we do it:
		1. unique_type_id() returns a monotonically increasing integer for every unique type
		   passed to it during this compilation unit. It also specialises an instance of
		   msvc_extract_type<unique_type_id, type>::id2type_impl<true>.
		2. vartypeID() returns a sized<unique_type_id> for the type where
		   sizeof(sized<unique_type_id>)==unique_type_id. We vector through sized as a means
		   of returning the unique_type_id at compile time rather than runtime.
		3. msvc_extract_type<unique_type_id> then extracts the type by using a bug in MSVC to
		   reselect the specialised child type (id2type_impl<true>) from within the specialisation
		   of itself originally performed by the above instance of unique_type_id. This bug works
		   because when MSVC calculated the signature of the specialised
		   msvc_extract_type<unique_type_id, type>::id2type_impl<true>, it does not include the
		   value of type in the signature of id2type_impl<true>. Therefore when we reselect
		   msvc_extract_type<unique_type_id>::id2type_impl<true> it erroneously returns the one
		   already in its list of instantiated types rather than correctly generating a newly
		   specialised msvc_extract_type<unique_type_id, msvc_extract_type_default_param>::id2type_impl<true>

	This bug allows the impossible and gives us a working typeof() in MSVC. Hopefully Microsoft
	won't fix this bug until they implement a native typeof.
	*/

	struct msvc_extract_type_default_param {};
	template<int ID, typename T = msvc_extract_type_default_param> struct msvc_extract_type;

	template<int ID> struct msvc_extract_type<ID, msvc_extract_type_default_param>
	{
		template<bool> struct id2type_impl;

		typedef id2type_impl<true> id2type;
	};

	template<int ID, typename T> struct msvc_extract_type : msvc_extract_type<ID, msvc_extract_type_default_param>
	{
		template<> struct id2type_impl<true> //VC8.0 specific bugfeature
		{
			typedef T type;
		};
		template<bool> struct id2type_impl;

		typedef id2type_impl<true> id2type;
	};


	template<int N> class CCounter;

	// TUnused is required to force compiler to recompile CCountOf class
	template<typename TUnused, int NTested = 0> struct CCountOf
	{
		enum
		{
			__if_exists(CCounter<NTested>) { count = CCountOf<TUnused, NTested + 1>::count }
			__if_not_exists(CCounter<NTested>) { count = NTested }
		};
	};

	template<class TTypeReg, class TUnused, int NValue> struct CProvideCounterValue { enum { value = NValue }; };

	// type_id
	#define unique_type_id(type) \
		(CProvideCounterValue< \
			/*register TYPE--ID*/ typename msvc_extract_type<CCountOf<type >::count, type>::id2type, \
			/*increment compile-time Counter*/ CCounter<CCountOf<type >::count>, \
			/*pass value of Counter*/CCountOf<type >::count \
		 >::value)

	// Lets type_id() be > than 0
	class __Increment_type_id { enum { value = unique_type_id(__Increment_type_id) }; };

	// vartypeID() returns a type with sizeof(type_id)
	template<int NSize>	class sized { char m_pad[NSize]; };
	template<typename T> typename sized<unique_type_id(T)> vartypeID(T&);
	template<typename T> typename sized<unique_type_id(const T)> vartypeID(const T&);
	template<typename T> typename sized<unique_type_id(volatile  T)> vartypeID(volatile T&);
	template<typename T> typename sized<unique_type_id(const volatile T)> vartypeID(const volatile T&);
}

#define typeof(expression) msvc_typeof_impl::msvc_extract_type<sizeof(msvc_typeof_impl::vartypeID(expression))>::id2type::type
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
    __With<typeof(e)> __with##n(e); // TODO unique id

#define WITH_VAR(e, v, n) {    \
    __With<typeof(e)> __with##n(e);      \
    typeof(e) v = __with##n;

#define END_WITH }

template<class T> static inline int __wrap(T a, int i) {
#ifndef __SS_NOWRAP
    if(i<0) return len(a)+i;
#endif
#ifndef __SS_NOBOUNDS
        if(i<0 || i>= len(a))
            __throw_index_out_of_range();
#endif
    return i;
}

/* representation */

template<class T> str *__str(T t) { if (!t) return new str("None"); return t->__str__(); }
template<class T> str *repr(T t) { if (!t) return new str("None"); return t->__repr__(); }

str *__str(void *);

/* return pointer to class object */

template<class T> class_ *__type(T t) { return t->__class__; }
template<> class_ *__type(int i);
template<> class_ *__type(double d);

/* equality, comparison */

template<class T> inline __ss_bool __eq(T a, T b) { return ((a&&b)?(a->__eq__(b)):__mbool(a==b)); }
#ifdef __SS_LONG /* XXX */
template<> inline __ss_bool __eq(__ss_int a, __ss_int b) { return __mbool(a == b); }
#endif
template<> inline __ss_bool __eq(str *a, str *b) {
    if(a&&b) {
        if (a->charcache && b->charcache) 
            return __mbool(a==b);
        else
            return __mbool(a->__eq__(b));
    } else
        return __mbool(a==b);
}
template<> inline __ss_bool __eq(int a, int b) { return __mbool(a == b); }
template<> inline __ss_bool __eq(__ss_bool a, __ss_bool b) { return __mbool(a == b); }
template<> inline __ss_bool __eq(double a, double b) { return __mbool(a == b); }
template<> inline __ss_bool __eq(void *a, void *b) { return __mbool(a == b); }

template<class T> inline __ss_bool __ne(T a, T b) { return ((a&&b)?(a->__ne__(b)):__mbool(a!=b)); }
template<> inline __ss_bool __ne(int a, int b) { return __mbool(a != b); }
template<> inline __ss_bool __ne(double a, double b) { return __mbool(a != b); }
template<> inline __ss_bool __ne(void *a, void *b) { return __mbool(a != b); }
template<class T> inline __ss_bool __gt(T a, T b) { return a->__gt__(b); }
template<> inline __ss_bool __gt(int a, int b) { return __mbool(a > b); }
template<> inline __ss_bool __gt(double a, double b) { return __mbool(a > b); }
template<class T> inline __ss_bool __ge(T a, T b) { return a->__ge__(b); }
template<> inline __ss_bool __ge(int a, int b) { return __mbool(a >= b); }
template<> inline __ss_bool __ge(double a, double b) { return __mbool(a >= b); }
template<class T> inline __ss_bool __lt(T a, T b) { return a->__lt__(b); }
template<> inline __ss_bool __lt(int a, int b) { return __mbool(a < b); }
template<> inline __ss_bool __lt(double a, double b) { return __mbool(a < b); }
template<class T> inline __ss_bool __le(T a, T b) { return a->__le__(b); }
template<> inline __ss_bool __le(int a, int b) { return __mbool(a <= b); }
template<> inline __ss_bool __le(double a, double b) { return __mbool(a <= b); }

/* add */

template<class T> inline T __add(T a, T b) { return a->__add__(b); }
#ifdef __SS_LONG
template<> inline __ss_int __add(__ss_int a, __ss_int b) { return a + b; }
#endif
template<> inline int __add(int a, int b) { return a + b; }
template<> inline double __add(double a, double b) { return a + b; }

/* reverse */

template<class U> U __add2(double a, U b) { return b->__add__(a); }
template<class U> U __sub2(double a, U b) { return b->__rsub__(a); }
template<class T> T __mul2(__ss_int n, T a) { return a->__mul__(n); }
template<class T> T __mul2(__ss_bool n, T a) { return a->__mul__(n.value); }
template<class T> T __mul2(double n, T a) { return a->__mul__(n); }
template<class T> T __div2(__ss_int n, T a) { return a->__rdiv__(n); }
template<class T> T __div2(double n, T a) { return a->__rdiv__(n); }

str *__add_strs(int n, str *a, str *b, str *c);
str *__add_strs(int n, str *a, str *b, str *c, str *d);
str *__add_strs(int n, str *a, str *b, str *c, str *d, str *e);
str *__add_strs(int n, ...);

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
template<> inline double __copy(double d) { return d; }
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
template<> inline double __deepcopy(double d, dict<void *, pyobj *> *) { return d; }
template<> inline void *__deepcopy(void *p, dict<void *, pyobj *> *) { return p; }

/* len */

template<class T> inline __ss_int len(T x) { return x->__len__(); }
template<class T> inline __ss_int len(list<T> *x) { return x->units.size(); } /* XXX more general solution? */


/* bool */

inline __ss_int __ss_bool::operator+(__ss_bool b) { return value+b.value; }
inline __ss_bool __ss_bool::operator==(__ss_bool b) { __ss_bool c; c.value=value==b.value; return c; }
inline __ss_bool __ss_bool::operator&(__ss_bool b) { __ss_bool c; c.value=value&b.value; return c; }
inline __ss_bool __ss_bool::operator|(__ss_bool b) { __ss_bool c; c.value=value|b.value; return c; }
inline __ss_bool __ss_bool::operator^(__ss_bool b) { __ss_bool c; c.value=value^b.value; return c; }
inline bool __ss_bool::operator!() { return !value; }
inline __ss_bool::operator bool() { return bool(value); }

inline __ss_bool ___bool() { return __mbool(false); }

template<class T> inline __ss_bool ___bool(T x) { return __mbool(x && x->__nonzero__()); }
#ifdef __SS_LONG
template<> inline __ss_bool ___bool(__ss_int x) { return __mbool(x!=0); }
#endif
template<> inline __ss_bool ___bool(int x) { return __mbool(x!=0); }
template<> inline __ss_bool ___bool(bool x) { return __mbool(x); }
template<> inline __ss_bool ___bool(__ss_bool x) { return x; }
template<> inline __ss_bool ___bool(double x) { return __mbool(x!=0); }
template<> inline __ss_bool ___bool(void *) { return False; }
template<> inline __ss_bool ___bool(long int) { return False; } /* XXX bool(None) 64-bit */

/* and, or, not */

#define __OR(a, b, t) ((___bool(__ ## t = a))?(__ ## t):(b))
#define __AND(a, b, t) ((!___bool(__ ## t = a))?(__ ## t):(b))
#define __NOT(x) (__mbool(!x))

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
    pyiter<T>::for_in_loop __3;
    int __2;
    pyiter<T> *__1;
    FOR_IN_NEW(e,this,1,2,3)
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

template<class T> inline int pyseq<T>::for_in_init() {
    return 0;
}

template<class T> inline bool pyseq<T>::for_in_has_next(int i) {
    return i != __len__(); /* XXX opt end cond */
}

template<class T> inline T pyseq<T>::for_in_next(int &i) {
    return __getitem__(i++);
}

/* 
dict implementation, partially derived from CPython,
copyright Python Software Foundation (http://www.python.org/download/releases/2.6.2/license/) */

#define INIT_NONZERO_SET_SLOTS(so) do {				\
	(so)->table = (so)->smalltable;				\
	(so)->mask = MINSIZE - 1;				\
    } while(0)


#define EMPTY_TO_MINSIZE(so) do {				\
	memset((so)->smalltable, 0, sizeof((so)->smalltable));	\
	(so)->used = (so)->fill = 0;				\
	INIT_NONZERO_SET_SLOTS(so);				\
    } while(0)

template <class T> void *myallocate(int n) { return GC_MALLOC(n); }
template <> void *myallocate<__ss_int>(int n);

template <class K, class V> void *myallocate(int n) { return GC_MALLOC(n); }
template <> void *myallocate<__ss_int, __ss_int>(int n);

template<class K, class V> dict<K,V>::dict() {
    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);
}

template<class K, class V> dict<K, V>::dict(int count, ...)  {
    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);
    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        typedef tuple2<K, V> * bert;
        bert t = va_arg(ap, bert);
        __setitem__(t->__getfirst__(), t->__getsecond__());
    }
    va_end(ap);
}

template<class K, class V, class U> static inline void __add_to_dict(dict<K, V> *d, U *iter) {
    __iter<typename U::for_in_unit> *it = ___iter(iter);
    typename U::for_in_unit a, b;
    a = it->next();
    b = it->next();
    d->__setitem__(a, b);
}

template<class K, class V> static inline void __add_to_dict(dict<K, V> *d, tuple2<K, V> *t) {
    d->__setitem__(t->__getfirst__(), t->__getsecond__());
}

template<class K, class V> template<class U> dict<K, V>::dict(U *other) {
    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,other,1,2,3)
        __add_to_dict(this, e);
    END_FOR
}

template<class K, class V> dict<K, V>::dict(dict<K, V> *p)  {
    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);

    *this = *p;
}

#ifdef __SS_BIND
template<class K, class V> dict<K, V>::dict(PyObject *p) {
    if(!PyDict_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (dictionary expected)"));

    this->__class__ = cl_dict;
    EMPTY_TO_MINSIZE(this);
    PyObject *key, *value;

    PyObject *iter = PyObject_GetIter(p);
    while(key = PyIter_Next(iter)) {
        value = PyDict_GetItem(p, key);
        __setitem__(__to_ss<K>(key), __to_ss<V>(value));
        Py_DECREF(key);
    }
    Py_DECREF(iter);
}

template<class K, class V> PyObject *dict<K, V>::__to_py__() {
   PyObject *p = PyDict_New();
   int pos = 0;
   dictentry<K,V> *entry;
   while(next(&pos, &entry)) {
       PyObject *pkey = __to_py(entry->key);
       PyObject *pvalue = __to_py(entry->value);
       PyDict_SetItem(p, pkey, pvalue);
       Py_DECREF(pkey);
       Py_DECREF(pvalue);
   }
   return p;
}
#endif

template <class K, class V> dict<K,V>& dict<K,V>::operator=(const dict<K,V>& other) {
    memcpy(this, &other, sizeof(dict<K,V>));
    int table_size = sizeof(dictentry<K,V>) * (other.mask+1);
    table = (dictentry<K,V>*)myallocate<K,V>(table_size);
    memcpy(table, other.table, table_size);
    return *this;
}

template<class K, class V> __ss_bool dict<K,V>::__eq__(pyobj *p) { /* XXX check hash */
    dict<K,V> *b = (dict<K,V> *)p;

    if( b->__len__() != this->__len__())
        return False;

    int pos = 0;
    dictentry<K,V> *entry;
    while (next(&pos, &entry)) {
        if(!b->__contains__(entry))
            return False;
    }
    return True;
}

template <class K, class V> int characterize(dict<K,V> *a, dict<K,V> *b, V *pval)
{
	int i;
	int difference_found = 0;
	K akey;
	V aval;
	int cmp;

	for (i = 0; i <= a->mask; i++) {
		dictentry<K, V> *entry;
		K thiskey;
		V thisaval, thisbval;
		if (a->table[i].use != active) continue;

		thiskey = a->table[i].key;
		if (difference_found) {
			cmp = __cmp(akey, thiskey);
			if (cmp < 0) continue;
		}

		thisaval = a->table[i].value;
		entry = b->lookup(thiskey, a->table[i].hash);

		if (entry->use != active) cmp = 1;
		else {
			thisbval = entry->value;
			cmp = __cmp(thisaval, thisbval);
		}

		if (cmp != 0) {
			difference_found = 1;
			akey = thiskey;
			aval = thisaval;
		}
	}

	*pval = aval;
	return difference_found;
}


template<class K, class V> __ss_bool dict<K,V>::__ge__(dict<K,V> *s) {
    return __mbool(__cmp__(s) >= 0);
}

template<class K, class V> __ss_bool dict<K,V>::__le__(dict<K,V> *s) {
    return __mbool(__cmp__(s) <= 0);
}

template<class K, class V> __ss_bool dict<K,V>::__lt__(dict<K,V> *s) {
    return __mbool(__cmp__(s) < 0);
}

template<class K, class V> __ss_bool dict<K,V>::__gt__(dict<K,V> *s) {
    return __mbool(__cmp__(s) > 0);
}

template<class K, class V> __ss_int dict<K,V>::__cmp__(pyobj *p) {
    dict<K,V> *s = (dict<K,V> *)p;
	int difference_found;
	V aval, bval;

    if (this->used < s->used) return -1;
    else if (this->used > s->used) return 1;

	difference_found = characterize(this, s, &aval);
	if (!difference_found) return 0;

	characterize(s, this, &bval);

	return __cmp(aval, bval);
}

template <class K, class V> dictentry<K,V>* dict<K,V>::lookup(K key, long hash) const {

    int i = hash & mask;
    dictentry<K,V>* entry = &table[i];
    if (!(entry->use) || __eq(entry->key, key))
        return entry;

    dictentry <K,V>* freeslot;

    if (entry->use == dummy)
        freeslot = entry;
    else
        freeslot = NULL;

    unsigned int perturb;
    for (perturb = hash; ; perturb >>= PERTURB_SHIFT) {
        i = (i << 2) + i + perturb + 1;
        entry = &table[i & mask];
        if (!(entry->use)) {
            if (freeslot != NULL)
                entry = freeslot;
            break;
        }
        if (__eq(entry->key, key))
            break;

        else if (entry->use == dummy && freeslot == NULL)
            freeslot = entry;
	}
	return entry;
}

template <class K, class V> void dict<K,V>::insert_key(K key, V value, long hash) {
    dictentry<K,V>* entry;

    entry = lookup(key, hash);
    if (!(entry->use)) {
        fill++;
        entry->key = key;
        entry->value = value;
        entry->hash = hash;
        entry->use = active;
        used++;
    }
    else if (entry->use == dummy) {
        entry->key = key;
        entry->value = value;
        entry->hash = hash;
        entry->use = active;
        used++;
    }
    else {
		entry->value = value;
	}
}

template <class K, class V> void *dict<K,V>::__setitem__(K key, V value)
{
    long hash = hasher<K>(key);
    int n_used = used;

    insert_key(key, value, hash);
    if ((used > n_used && fill*3 >= (mask+1)*2))
        resize(used>50000 ? used*2 : used*4);
    return NULL;
}

template<class T> T __none() { return NULL; }
template<> int __none();
template<> double __none();

template <class K, class V> V dict<K,V>::__getitem__(K key) {
	register long hash = hasher<K>(key);
	register dictentry<K, V> *entry;

	entry = lookup(key, hash);

	if (entry->use != active)
		throw new KeyError(repr(key));
	
	return entry->value;
}

template<class K, class V> void *dict<K,V>::__addtoitem__(K key, V value) {
	register long hash = hasher<K>(key);
	register dictentry<K, V> *entry;

	entry = lookup(key, hash);
	if (entry->use != active)
		throw new KeyError(repr(key));

    entry->value = __add(entry->value, value);
    return NULL;
}

template <class K, class V> V dict<K,V>::get(K key) {
    register long hash = hasher<K>(key);
	register dictentry<K, V> *entry;

	entry = lookup(key, hash);
	if (entry->use != active)
        return __none<V>();
	
	return entry->value;
}

template <class K, class V> V dict<K,V>::get(K key, V d) {
    register long hash = hasher<K>(key);
	register dictentry<K, V> *entry;

	entry = lookup(key, hash);
	if (entry->use != active)
		return d;
	
	return entry->value;
}

template <class K, class V> V dict<K,V>::setdefault(K key, V value)
{
    register long hash = hasher<K>(key);
	register dictentry<K, V> *entry;

	entry = lookup(key, hash);

    if (entry->use != active)
		__setitem__(key, value);

	return entry->value;
}

template <class K, class V> void *dict<K,V>::__delitem__(K key) {
    if (!do_discard(key)) throw new KeyError(repr(key));
}

template <class K, class V> int dict<K,V>::do_discard(K key) {
	register long hash = hasher<K>(key);
	register dictentry<K,V> *entry;

	entry = lookup(key, hash);

	if (entry->use != active)
		return DISCARD_NOTFOUND; // nothing to discard

	entry->use = dummy;
	used--;
	return DISCARD_FOUND;
}

template <class K, class V> list<K> *dict<K,V>::keys() {
	int pos, i;
	dictentry<K,V> *entry;
	list<K> *ret = new list<K>;
    ret->units.resize(used);
	pos = i = 0;
	while (next(&pos, &entry))
        ret->units[i++] = entry->key;
    return ret;
}

template <class K, class V> list<V> *dict<K,V>::values() {
	int pos, i;
	dictentry<K,V> *entry;
	list<V> *ret = new list<V>;
    ret->units.resize(used);
	pos = i = 0;
	while (next(&pos, &entry))
        ret->units[i++] = entry->value;
	return ret;
}

template <class K, class V> list<tuple2<K, V> *> *dict<K,V>::items() {
	int pos, i;
	dictentry<K,V> *entry;
	list<tuple2<K, V> *> *ret = new list<tuple2<K, V> *>;
    ret->units.resize(used);
	pos = i = 0;
	while (next(&pos, &entry))
        ret->units[i++] = new tuple2<K, V>(2, entry->key, entry->value);
    return ret;
}

template<class K, class V> V dict<K,V>::pop(K key) {
	register long hash = hasher<K>(key);
    register dictentry<K,V> *entry;

    entry = lookup(key, hash);

	if (entry->use != active)
		throw new KeyError(__str(key));

	entry->use = dummy;
	used--;
	return entry->value;
}

template<class K, class V> tuple2<K,V> *dict<K,V>::popitem() {
    register int i = 0;
	register dictentry<K,V> *entry;

	if (used == 0)
		throw new KeyError(new str("popitem(): dictionary is empty"));

	entry = &table[0];
	if (entry->use != active) {
		i = entry->hash;
		if (i > mask || i < 1)
			i = 1;	/* skip slot 0 */
		while ((entry = &table[i])->use != active) {
			i++;
			if (i > mask)
				i = 1;
		}
	}
	entry->use = dummy;
	used--;
	table[0].hash = i + 1;  /* next place to start */
	return new tuple2<K,V>(entry->key, entry->value);
}

/*
 * Iterate over a dict table.  Use like so:
 *
 *     int pos;
 *     dictentry<K,V> *entry;
 *     pos = 0;   # important!  pos should not otherwise be changed by you
 *     while (dict_next(yourdict, &pos, &entry)) {
 *              Refer to borrowed reference in entry->key.
 *     }
 */
template <class K, class V> int dict<K,V>::next(int *pos_ptr, dictentry<K,V> **entry_ptr)
{
	int i;

	i = *pos_ptr;

	while (i <= mask && (table[i].use != active))
		i++;
	*pos_ptr = i+1;
	if (i > mask)
		return 0;
	*entry_ptr = &table[i];
	return 1;
}

/*
Internal routine used by dict_table_resize() to insert an item which is
known to be absent from the dict.  This routine also assumes that
the dict contains no deleted entries.  Besides the performance benefit,
using insert() in resize() is dangerous (SF bug #1456209).
*/
template <class K, class V> void dict<K,V>::insert_clean(K key, V value, long hash)
{
	int i;
	unsigned int perturb;
	register dictentry<K,V> *entry;

	i = hash & mask;

	entry = &table[i];
	for (perturb = hash; entry->use; perturb >>= PERTURB_SHIFT) {
		i = (i << 2) + i + perturb + 1;
		entry = &table[i & mask];
	}
	fill++;
	entry->key = key;
	entry->value = value;
	entry->hash = hash;
	entry->use = active;
	used++;
}


/*
Restructure the table by allocating a new table and reinserting all
keys again.  When entries have been deleted, the new table may
actually be smaller than the old one.
*/
template <class K, class V> void dict<K,V>::resize(int minused)
{
	int newsize;
	dictentry<K,V> *oldtable, *newtable, *entry;
	int i;
	dictentry<K,V> small_copy[MINSIZE];

	/* Find the smallest table size > minused. */
	for (newsize = MINSIZE;
	     newsize <= minused && newsize > 0;
	     newsize <<= 1)
		;
	if (newsize <= 0) {
		//XXX raise memory error
	}

	/* Get space for a new table. */
	oldtable = table;

	if (newsize == MINSIZE) {
		/* A large table is shrinking, or we can't get any smaller. */
		newtable = smalltable;
		if (newtable == oldtable) {
			if (fill == used) {
				/* No dummies, so no point doing anything. */
				return;
			}
			/* We're not going to resize it, but rebuild the
			   table anyway to purge old dummy entries.
			   Subtle:  This is *necessary* if fill==size,
			   as dict_lookkey needs at least one virgin slot to
			   terminate failing searches.  If fill < size, it's
			   merely desirable, as dummies slow searches. */
			memcpy(small_copy, oldtable, sizeof(small_copy));
			oldtable = small_copy;
		}
	}
	else {
        newtable = (dictentry<K,V>*) myallocate<K,V>(sizeof(dictentry<K,V>) * newsize);
	}

	/* Make the dict empty, using the new table. */
	table = newtable;
	mask = newsize - 1;

	memset(newtable, 0, sizeof(dictentry<K,V>) * newsize);

    i = used;
    used = 0;
	fill = 0;

	/* Copy the data over;
	   dummy entries aren't copied over */
	for (entry = oldtable; i > 0; entry++) {
		if (entry->use == active) {
			/* ACTIVE */
			--i;
			insert_clean(entry->key, entry->value, entry->hash);
		}
	}
}

template<class K, class V> str *dict<K,V>::__repr__() {
    str *r = new str("{");
    dictentry<K,V> *entry;
    
    int i = __len__();
    int pos = 0;

    while (next(&pos, &entry)) {
		--i;
        r->unit += repr(entry->key)->unit + ": " + repr(entry->value)->unit;
        if( i > 0 )
           r->unit += ", ";
    }

    r->unit += "}";
    return r;
}

template<class K, class V> __ss_int dict<K,V>::__len__() {
    return used;
}

template <class K, class V> __ss_bool dict<K,V>::__contains__(K key) {
    long hash = hasher(key);
	dictentry<K,V> *entry;

	entry = lookup(key, hash);

	return __mbool(entry->use==active);
}

template <class K, class V> __ss_bool dict<K,V>::__contains__(dictentry<K,V>* entry) {
	entry = lookup(entry->key, entry->hash);

	return __mbool(entry->use == active);
}

template <class K, class V> __ss_bool dict<K,V>::has_key(K key) {
	return __contains__(key);
}

template <class K, class V> void *dict<K,V>::clear()
{
	dictentry<K,V> *entry, *table;
	int table_is_malloced;
	ssize_t fill;
	dictentry<K,V> small_copy[MINSIZE];

    table = this->table;
	table_is_malloced = table != smalltable;

	/* This is delicate.  During the process of clearing the dict,
	 * decrefs can cause the dict to mutate.  To avoid fatal confusion
	 * (voice of experience), we have to make the dict empty before
	 * clearing the slots, and never refer to anything via so->ref while
	 * clearing.
	 */
	fill = this->fill;
	if (table_is_malloced)
		EMPTY_TO_MINSIZE(this);

	else if (fill > 0) {
		/* It's a small table with something that needs to be cleared.
		 * Afraid the only safe way is to copy the dict entries into
		 * another small table first.
		 */
		// ffao: is this really needed without reference counting?
		//memcpy(small_copy, table, sizeof(small_copy));
		//table = small_copy;
		EMPTY_TO_MINSIZE(this);
	}
	/* else it's a small table that's already empty */

	/* if (table_is_malloced)
		PyMem_DEL(table); */
	return NULL;
}

template <class K, class V> void *dict<K,V>::update(dict<K,V>* other)
{
	register int i;
	register dictentry<K,V> *entry;

	/* Do one big resize at the start, rather than
	 * incrementally resizing as we insert new keys.  Expect
	 * that there will be no (or few) overlapping keys.
	 */
	if ((fill + other->used)*3 >= (mask+1)*2)
	   resize((used + other->used)*2);
	for (i = 0; i <= other->mask; i++) {
		entry = &other->table[i];
		if (entry->use == active) {
			insert_key(entry->key, entry->value, entry->hash);
		}
	}
    return NULL;
}

template <class K, class V> template<class U> void *dict<K,V>::update(U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,iter,1,2,3)
		__setitem__(e->__getitem__(0), e->__getitem__(1));
    END_FOR
    return NULL;
}

template<class K, class V> dict<K,V> *dict<K,V>::copy() {
    dict<K,V> *c = new dict<K,V>;
    *c = *this;
    return c;
}

template<class K, class V> dict<K,V> *dict<K,V>::__copy__() {
    dict<K,V> *c = new dict<K,V>;
    *c = *this;
    return c;
}

template<class K, class V> dict<K,V> *dict<K,V>::__deepcopy__(dict<void *, pyobj *> *memo) {
    dict<K,V> *c = new dict<K,V>();
    memo->__setitem__(this, c);
    K e;
    dict<K,V>::for_in_loop __3;
    int __2;
    dict<K,V> *__1;
    FOR_IN_NEW(e,this,1,2,3)
        c->__setitem__(__deepcopy(e, memo), __deepcopy(this->__getitem__(e), memo));
    END_FOR
    return c;
}

/* list methods */

template<class T> list<T>::list() {
    this->__class__ = cl_list;
}

template<class T> list<T>::list(int count, ...) {
    this->__class__ = cl_list;
    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        T t = va_arg(ap, T);
        this->units.push_back(t);
    }
    va_end(ap);
}

template<class T> template<class U> list<T>::list(U *iter) {
    this->__class__ = cl_list;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        this->units.push_back(e);
    END_FOR
}

template<class T> list<T>::list(list<T> *p) {
    this->__class__ = cl_list;
    this->units = p->units;
}

template<class T> list<T>::list(tuple2<T, T> *p) {
    this->__class__ = cl_list;
    this->units = p->units;
}

template<class T> list<T>::list(str *s) {
    this->__class__ = cl_list;
    this->units.resize(len(s));
    int sz = s->unit.size();
    for(int i=0; i<sz; i++)
        this->units[i] = __char_cache[((unsigned char)(s->unit[i]))];
}

#ifdef __SS_BIND
template<class T> list<T>::list(PyObject *p) {
    if(!PyList_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (list expected)"));

    this->__class__ = cl_list;
    int size = PyList_Size(p);
    for(int i=0; i<size; i++)
        append(__to_ss<T>(PyList_GetItem(p, i)));
}

template<class T> PyObject *list<T>::__to_py__() {
    int len = this->__len__();
    PyObject *p = PyList_New(len);
    for(int i=0; i<len; i++)
        PyList_SetItem(p, i, __to_py(this->__getitem__(i)));
    return p;
}
#endif

template<class T> void list<T>::clear() {
    units.resize(0);
}

template<class T> void list<T>::resize(__ss_int i) {
    units.resize(i);
}

template<class T> __ss_int list<T>::__len__() {
    return units.size();
}

template<class T> T list<T>::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return units[i];
}

template<class T> __ss_bool list<T>::__eq__(pyobj *p) {
   list<T> *b = (list<T> *)p;
   unsigned int len = this->units.size();
   if(b->units.size() != len) return False;
   for(unsigned int i = 0; i < len; i++)
       if(!__eq(this->units[i], b->units[i]))
           return False;
   return True;
}

template<class T> void *list<T>::append(T a) {
    this->units.push_back(a);
    return NULL;
}

template<class T> template<class U> void *list<T>::extend(U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        this->units.push_back(e);
    END_FOR
    return NULL;
}

template<class T> void *list<T>::extend(list<T> *p) {
    int l1, l2;
    l1 = this->__len__(); l2 = p->__len__();
    this->units.resize(l1+l2);
    memcpy(&(this->units[l1]), &(p->units[0]), sizeof(T)*l2);
    return NULL;
}
template<class T> void *list<T>::extend(tuple2<T,T> *p) {
    int l1, l2;
    l1 = this->__len__(); l2 = p->__len__();
    this->units.resize(l1+l2);
    memcpy(&(this->units[l1]), &(p->units[0]), sizeof(T)*l2);
    return NULL;
}

template<class T> void *list<T>::extend(str *s) {
    int sz = s->unit.size();
    for(int i=0; i<sz; i++)
        this->units.push_back(__char_cache[((unsigned char)(s->unit[i]))]);
    return NULL;
}

template<class T> inline T list<T>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return this->units[i];
}

template<class T> void *list<T>::__setitem__(__ss_int i, T e) {
    i = __wrap(this, i);
    units[i] = e;
    return NULL;
}

template<class T> void *list<T>::__delitem__(__ss_int i) {
    i = __wrap(this, i);
    units.erase(units.begin()+i,units.begin()+i+1);
    return NULL;
}

template<class T> int list<T>::empty() {
    return units.empty();
}

template<class T> list<T> *list<T>::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    list<T> *c = new list<T>();
    slicenr(x, l, u, s, this->__len__());
    if(s == 1) {
        c->units.resize(u-l);
        memcpy(&(c->units[0]), &(this->units[l]), sizeof(T)*(u-l));
    } else if(s > 0)
        for(int i=l; i<u; i += s)
            c->units.push_back(units[i]);
    else
        for(int i=l; i>u; i += s)
            c->units.push_back(units[i]);
    return c;
}

template<class T> void *list<T>::__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, pyiter<T> *b) {
    list<T> *la = new list<T>(); /* XXX avoid intermediate list */
    typename pyiter<T>::for_in_unit e;
    typename pyiter<T>::for_in_loop __3;
    int __2;
    pyiter<T> *__1;
    FOR_IN_NEW(e,b,1,2,3)
        la->units.push_back(e);
    END_FOR
    this->__setslice__(x, l, u, s, la);
    return NULL;
}

template<class T> void *list<T>::__setslice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s, list<T> *la) {
    slicenr(x, l, u, s, this->__len__());

    if(x&4 && s != 1) { // x&4: extended slice (step 's' is given), check if sizes match
        int slicesize;
        if(l == u) slicesize = 0; // XXX ugly
        else if(s > 0 && u < l) slicesize=0;
        else if(s < 0 && l < u) slicesize=0;
        else {
            int slicelen = std::abs(u-l);
            int absstep = std::abs(s);
            slicesize = slicelen/absstep;
            if(slicelen%absstep) slicesize += 1;
        }

        if(slicesize != len(la))
            throw new ValueError(__modtuple(new str("attempt to assign sequence of size %d to extended slice of size %d"), new tuple2<__ss_int,__ss_int>(2, len(la), (__ss_int)slicesize)));
    }

    if(s == 1) {
        if(l <= u) {
            this->units.erase(this->units.begin()+l, this->units.begin()+u);
            this->units.insert(this->units.begin()+l, la->units.begin(), la->units.end());
        } else
            this->units.insert(this->units.begin()+l, la->units.begin(), la->units.end());
    }
    else {
        int i, j;
        if(s > 0)
            for(i = 0, j = l; j < u; i++, j += s)
                this->units[j] = la->units[i];
        else
            for(i = 0, j = l; j > u; i++, j += s)
                this->units[j] = la->units[i];
    }

    return NULL;
}

template<class T> void *list<T>::__delete__(__ss_int i) {
    i = __wrap(this, i);
    units.erase(units.begin()+i,units.begin()+i+1);
    return NULL;
}

template<class T> void *list<T>::__delete__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    slicenr(x, l, u, s, this->__len__());

    if(s == 1)
        __delslice__(l, u);
    else {
        __GC_VECTOR(T) v;
        for(int i=0; i<this->__len__();i++)
            if((i+l) % s)
                v.push_back(this->units[i]);
        units = v;
    }
    return NULL;
}

template<class T> void *list<T>::__delslice__(__ss_int a, __ss_int b) {
    if(a>this->__len__()) return NULL;
    if(b>this->__len__()) b = this->__len__();
    units.erase(units.begin()+a,units.begin()+b);
    return NULL;
}

template<class T> __ss_bool list<T>::__contains__(T a) {
    int size = this->units.size();
    for(int i=0; i<size; i++)
        if(__eq(this->units[i], a))
            return True;
    return False;
}

template<class T> list<T> *list<T>::__add__(list<T> *b) {
    int l1 = this->__len__();
    int l2 = b->__len__();

    list<T> *c = new list<T>();
    c->units.resize(l1+l2);

    if(l1==1) c->units[0] = this->units[0];
    else memcpy(&(c->units[0]), &(this->units[0]), sizeof(T)*l1);
    if(l2==1) c->units[l1] = b->units[0];
    else memcpy(&(c->units[l1]), &(b->units[0]), sizeof(T)*l2);

    return c;
}

template<class T> list<T> *list<T>::__mul__(__ss_int b) {
    list<T> *c = new list<T>();
    if(b<=0) return c;
    __ss_int len = this->units.size();
    if(len==1)
        c->units.assign(b, this->units[0]);
    else {
        c->units.resize(b*len);
        for(__ss_int i=0; i<b; i++)
            memcpy(&(c->units[i*len]), &(this->units[0]), sizeof(T)*len);
    }
    return c;
}

template<class T> list<T> *list<T>::__copy__() {
    list<T> *c = new list<T>();
    c->units = this->units;
    return c;
}

template<class T> list<T> *list<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    list<T> *c = new list<T>();
    memo->__setitem__(this, c);
    c->units.resize(this->__len__());
    for(int i=0; i<this->__len__(); i++)
        c->units[i] = __deepcopy(this->units[i], memo);
    return c;
}

template<class T> template<class U> list<T> *list<T>::__iadd__(U *iter) {
    extend(iter);
    return this;
}

template<class T> list<T> *list<T>::__imul__(__ss_int n) {
    __ss_int l1 = this->__len__();
    this->units.resize(l1*n);
    for(__ss_int i = 1; i <= n-1; i++)
        memcpy(&(this->units[l1*i]), &(this->units[0]), sizeof(T)*l1);
    return this;
}

template<class T> __ss_int list<T>::index(T a) { return index(a, 0, this->__len__()); }
template<class T> __ss_int list<T>::index(T a, __ss_int s) { return index(a, s, this->__len__()); }
template<class T> __ss_int list<T>::index(T a, __ss_int s, __ss_int e) {
    __ss_int one = 1;
    slicenr(7, s, e, one, this->__len__());
    for(__ss_int i = s; i<e;i++)
        if(__eq(a,units[i]))
            return i;
    throw new ValueError(new str("list.index(x): x not in list"));
}

template<class T> __ss_int list<T>::count(T a) {
    __ss_int c = 0;
    __ss_int len = this->__len__();
    for(__ss_int i = 0; i<len;i++)
        if(__eq(a,units[i]))
            c++;
    return c;
}

template<class T> str *list<T>::__repr__() {
    str *r = new str("[");
    int len = this->__len__();
    for(int i = 0; i<len;i++) {
        r->unit += repr(units[i])->unit;
        if (i<len-1)
            r->unit += ", ";
    }
    r->unit += "]";
    return r;
}

template<class T> T list<T>::pop(int i) {
    int len = this->__len__();
    if(len==0)
        throw new IndexError(new str("pop from empty list"));
    if(i<0) 
        i = len+i;
    if(i<0 or i>=len)
        throw new IndexError(new str("pop index out of range"));
    T e = units[i];
    units.erase(units.begin()+i);
    return e;
}
template<class T> T list<T>::pop() {
    return pop(-1);
}

template<class T> void *list<T>::reverse() {
    std::reverse(this->units.begin(), this->units.end());
    return NULL;
}

template<class T> template <class U> void *list<T>::sort(__ss_int (*cmp)(T, T), U (*key)(T), __ss_int reverse) {
    if(key) {
        if(reverse)
            std::sort(units.begin(), units.end(), cpp_cmp_key_rev<T, U>(key));
        else
            std::sort(units.begin(), units.end(), cpp_cmp_key<T, U>(key));
    }
    else if(cmp) {
        if(reverse)
            std::sort(units.begin(), units.end(), cpp_cmp_custom_rev<T>(cmp));
        else
            std::sort(units.begin(), units.end(), cpp_cmp_custom<T>(cmp));
    } else {
        if(reverse)
            std::sort(units.begin(), units.end(), cpp_cmp_rev<T>);
        else
            std::sort(units.begin(), units.end(), cpp_cmp<T>);
    }

    return NULL;
}

template<class T> template <class U> void *list<T>::sort(__ss_int cmp, U (*key)(T), __ss_int reverse) {
    return sort((__ss_int(*)(T,T))0, key, reverse);
}
template<class T> void *list<T>::sort(__ss_int (*cmp)(T, T), __ss_int, __ss_int reverse) {
    return sort(cmp, (__ss_int(*)(T))0, reverse);
}
template<class T> void *list<T>::sort(__ss_int, __ss_int, __ss_int reverse) {
    return sort((__ss_int(*)(T,T))0, (__ss_int(*)(T))0, reverse);
}

template<class T> void *list<T>::insert(int m, T e) {
    int len = this->__len__();
    if (m<0) m = len+m;
    if (m<0) m = 0;
    if (m>=len) m = len;
    units.insert(units.begin()+m, e);
    return NULL;
}

template<class T> void *list<T>::remove(T e) {
    for(int i = 0; i < this->__len__(); i++)
        if(__eq(units[i], e)) {
            units.erase(units.begin()+i);
            return NULL;
        }
    throw new ValueError(new str("list.remove(x): x not in list"));
}

template<class T> inline bool list<T>::for_in_has_next(int i) {
    return i != units.size(); /* XXX opt end cond */
}

template<class T> inline T list<T>::for_in_next(int &i) {
    return units[i++];
}

/* str methods */

inline str *str::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return __char_cache[((unsigned char)(unit[i]))];
}

inline str *str::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return __char_cache[((unsigned char)(unit[i]))];
}

inline __ss_int str::__len__() {
    return unit.size();
}

inline bool str::for_in_has_next(int i) {
    return i != unit.size(); /* XXX opt end cond */
}

inline str *str::for_in_next(int &i) {
    return __char_cache[((unsigned char)(unit[i++]))];
}

template <class U> str *str::join(U *iter) {
    int sz, total, __2, tsz;
    bool only_ones = true;
    int unitsize = unit.size();
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    U *__1;
    __join_cache->units.resize(0);
    total = 0;
    FOR_IN_NEW(e,iter,1,2,3)
        __join_cache->units.push_back(e);
        sz = e->unit.size();
        if(sz != 1)
            only_ones = false;
        total += sz;
    END_FOR
    return __join(__join_cache, only_ones, total);
}

/* __iter methods */

template<class T> __iter<T> *__iter<T>::__iter__() { 
    __stop_iteration = false; 
    return this; 
}

template<class T> T __iter<T>::next() { /* __get_next can be overloaded instead to avoid (slow) exception handling */
    __result = this->__get_next();
    if(__stop_iteration)
        throw new StopIteration();
    return __result;
} 

template<class T> T __iter<T>::__get_next() {
    try {
        __result = this->next();
    } catch (StopIteration *) {
        __stop_iteration = true;
    }
    return __result;
}

/*
set implementation, partially derived from CPython,
copyright Python Software Foundation (http://www.python.org/download/releases/2.6.2/license/)
*/

template <class T> set<T>::set(int frozen) : frozen(frozen) {
    this->__class__ = cl_set;
    this->hash = -1;
    EMPTY_TO_MINSIZE(this);
}

#ifdef __SS_BIND
#if (PY_MAJOR_VERSION == 2)
#if (PY_MINOR_VERSION > 4)

template<class T> set<T>::set(PyObject *p) {
    this->__class__ = cl_set;
    this->hash = -1;
    EMPTY_TO_MINSIZE(this);
    if(PyFrozenSet_CheckExact(p))
        frozen = 1;
    else if(PyAnySet_CheckExact(p))
        frozen = 0;
    else
        throw new TypeError(new str("error in conversion to Shed Skin (set expected)"));

    PyObject *iter = PyObject_GetIter(p), *item;
    while(item = PyIter_Next(iter)) {
        add(__to_ss<T>(item));
        Py_DECREF(item);
    }
    Py_DECREF(iter);
}

template<class T> PyObject *set<T>::__to_py__() {
    list<T> *l = new list<T>(this); /* XXX optimize */
    PyObject *s;
    PyObject *p = __to_py(l);
    if(frozen)
        s = PyFrozenSet_New(p);
    else
        s = PySet_New(p);
    Py_DECREF(p);
    return s;
}

#endif
#endif
#endif

template<class T> template<class U> set<T>::set(U *other, int frozen) {
    this->__class__ = cl_set;
    this->frozen = frozen;
    this->hash = -1;
    EMPTY_TO_MINSIZE(this);
    update(other);
}

template<class T> template<class U> set<T>::set(U *other) {
    this->__class__ = cl_set;
    this->frozen = 0;
    this->hash = -1;
    EMPTY_TO_MINSIZE(this);
    update(other);
}

template <class T> set<T>& set<T>::operator=(const set<T>& other) {
    // copy test
    /*int i;
    for (i=0; i<8; i++) {
        smalltable[i].use = unused;
    }

    table = smalltable;
    mask = MINSIZE - 1;
    used = 0;
    fill = 0;

    update(other);*/

    memcpy(this, &other, sizeof(set<T>));
    int table_size = sizeof(setentry<T>) * (other.mask+1);
    table = (setentry<T>*)myallocate<T>(table_size);
    memcpy(table, other.table, table_size);
    return *this;
}

template<class T> __ss_bool set<T>::__eq__(pyobj *p) { /* XXX check hash */
    set<T> *b = (set<T> *)p;

    if( b->__len__() != this->__len__())
        return False;

    int pos = 0;
    setentry<T> *entry;
    while (next(&pos, &entry)) {
        if(!b->__contains__(entry))
            return False;
    }
    return True;
}

template <class T> void *set<T>::remove(T key) {
    if (!do_discard(key)) throw new KeyError(repr(key));
    return NULL;
}

template<class T> __ss_bool set<T>::__ge__(set<T> *s) {
    return issuperset(s);
}

template<class T> __ss_bool set<T>::__le__(set<T> *s) {
    return issubset(s);
}

template<class T> __ss_bool set<T>::__lt__(set<T> *s) {
    return issubset(s);
}

template<class T> __ss_bool set<T>::__gt__(set<T> *s) {
    return issuperset(s);
}

template<class T> __ss_int set<T>::__cmp__(pyobj *p) {
    /* XXX sometimes TypeError, sometimes not? */
    set<T> *s = (set<T> *)p;
    if(issubset(s)) return -1;
    else if(issuperset(s)) return 1;
    return 0;
}

template<class T> int set<T>::__hash__() {
    if(!this->frozen)
        throw new TypeError(new str("unhashable type: 'set'"));
    long h, hash = 1927868237L;
    if (this->hash != -1)
        return this->hash;
    hash *= __len__() + 1;
    int pos = 0;
    setentry<T> *entry;
    while (next(&pos, &entry)) {
        h = entry->hash;
        hash ^= (h ^ (h << 16) ^ 89869747L)  * 3644798167u;
    }
    hash = hash * 69069L + 907133923L;
    if (hash == -1)
        hash = 590923713L;
    this->hash = hash;
    return hash;
}

template <class T> setentry<T>* set<T>::lookup(T key, long hash) const {

    int i = hash & mask;
    setentry<T>* entry = &table[i];
    if (!(entry->use) || __eq(entry->key, key))
        return entry;

    setentry <T>* freeslot;

    if (entry->use == dummy)
        freeslot = entry;
    else
        freeslot = NULL;

    unsigned int perturb;
    for (perturb = hash; ; perturb >>= PERTURB_SHIFT) {
        i = (i << 2) + i + perturb + 1;
        entry = &table[i & mask];
        if (!(entry->use)) {
            if (freeslot != NULL)
                entry = freeslot;
            break;
        }
        if (__eq(entry->key, key))
            break;

        else if (entry->use == dummy && freeslot == NULL)
            freeslot = entry;
	}
	return entry;
}

template <class T> void set<T>::insert_key(T key, long hash) {
    setentry<T>* entry;

    entry = lookup(key, hash);
    if (!(entry->use)) {
        fill++;
        entry->key = key;
        entry->hash = hash;
        entry->use = active;
        used++;
    }
    else if (entry->use == dummy) {
        entry->key = key;
        entry->hash = hash;
        entry->use = active;
        used++;
    }
}

template <class T> void *set<T>::add(T key)
{
    long hash = hasher<T>(key);
    int n_used = used;
    insert_key(key, hash);
    if ((used > n_used && fill*3 >= (mask+1)*2))
        resize(used>50000 ? used*2 : used*4);
    return NULL;
}

template <class T> void *set<T>::add(setentry<T>* entry)
{
    int n_used = used;

    insert_key(entry->key, entry->hash);
    if ((used > n_used && fill*3 >= (mask+1)*2))
        resize(used>50000 ? used*2 : used*4);
    return NULL;
}

template <class T> int freeze(set<T> *key) {
    int orig_frozen = key->frozen;
    key->frozen = 1;
    return orig_frozen;
}
template <class T> void unfreeze(set<T> *key, int orig_frozen) {
    key->frozen = orig_frozen;
}
template <class U> int freeze(U key) {
    return 0;
}
template <class U> void unfreeze(U, int orig_frozen) {
}

template <class T> void *set<T>::discard(T key) {
    do_discard(key);
    return NULL;
}

template <class T> int set<T>::do_discard(T key) {
    int orig_frozen = freeze(key);
	register long hash = hasher<T>(key);
	register setentry<T> *entry;

	entry = lookup(key, hash);
    unfreeze(key, orig_frozen);

	if (entry->use != active)
		return DISCARD_NOTFOUND; // nothing to discard

	entry->use = dummy;
	used--;
	return DISCARD_FOUND;
}

template<class T> T set<T>::pop() {
    register int i = 0;
	register setentry<T> *entry;

	if (used == 0)
		throw new KeyError(new str("pop from an empty set"));

	entry = &table[0];
	if (entry->use != active) {
		i = entry->hash;
		if (i > mask || i < 1)
			i = 1;	/* skip slot 0 */
		while ((entry = &table[i])->use != active) {
			i++;
			if (i > mask)
				i = 1;
		}
	}
	entry->use = dummy;
	used--;
	table[0].hash = i + 1;  /* next place to start */
	return entry->key;
}

/*
 * Iterate over a set table.  Use like so:
 *
 *     Py_ssize_t pos;
 *     setentry *entry;
 *     pos = 0;   # important!  pos should not otherwise be changed by you
 *     while (set_next(yourset, &pos, &entry)) {
 *              Refer to borrowed reference in entry->key.
 *     }
 */
template <class T> int set<T>::next(int *pos_ptr, setentry<T> **entry_ptr)
{
	int i;

	i = *pos_ptr;

	while (i <= mask && (table[i].use != active))
		i++;
	*pos_ptr = i+1;
	if (i > mask)
		return 0;
	*entry_ptr = &table[i];
	return 1;
}

/*
Internal routine used by set_table_resize() to insert an item which is
known to be absent from the set.  This routine also assumes that
the set contains no deleted entries.  Besides the performance benefit,
using insert() in resize() is dangerous (SF bug #1456209).
*/
template <class T> void set<T>::insert_clean(T key, long hash)
{
	int i;
	unsigned int perturb;
	register setentry<T> *entry;

	i = hash & mask;

	entry = &table[i];
	for (perturb = hash; entry->use; perturb >>= PERTURB_SHIFT) {
		i = (i << 2) + i + perturb + 1;
		entry = &table[i & mask];
	}
	fill++;
	entry->key = key;
	entry->hash = hash;
	entry->use = active;
	used++;
}


/*
Restructure the table by allocating a new table and reinserting all
keys again.  When entries have been deleted, the new table may
actually be smaller than the old one.
*/
template <class T> void set<T>::resize(int minused)
{
	int newsize;
	setentry<T> *oldtable, *newtable, *entry;
	int i;
	setentry<T> small_copy[MINSIZE];

	/* Find the smallest table size > minused. */
	for (newsize = MINSIZE;
	     newsize <= minused && newsize > 0;
	     newsize <<= 1)
		;
	if (newsize <= 0) {
		//XXX raise memory error
	}

	/* Get space for a new table. */
	oldtable = table;

	if (newsize == MINSIZE) {
		/* A large table is shrinking, or we can't get any smaller. */
		newtable = smalltable;
		if (newtable == oldtable) {
			if (fill == used) {
				/* No dummies, so no point doing anything. */
				return;
			}
			/* We're not going to resize it, but rebuild the
			   table anyway to purge old dummy entries.
			   Subtle:  This is *necessary* if fill==size,
			   as set_lookkey needs at least one virgin slot to
			   terminate failing searches.  If fill < size, it's
			   merely desirable, as dummies slow searches. */
			memcpy(small_copy, oldtable, sizeof(small_copy));
			oldtable = small_copy;
		}
	}
	else {
        newtable = (setentry<T>*) myallocate<T>(sizeof(setentry<T>) * newsize);
	}

	/* Make the set empty, using the new table. */
	table = newtable;
	mask = newsize - 1;

	memset(newtable, 0, sizeof(setentry<T>) * newsize);

    i = used;
    used = 0;
	fill = 0;

	/* Copy the data over;
	   dummy entries aren't copied over */
	for (entry = oldtable; i > 0; entry++) {
		if (entry->use == active) {
			/* ACTIVE */
			--i;
			insert_clean(entry->key, entry->hash);
		}
	}
}

template<class T> str *set<T>::__repr__() {
    str *r;
    if(this->frozen) r = new str("frozenset([");
    else r = new str("set([");

    int rest = used-1;

    int pos = 0;
    setentry<T>* entry;
    while (next(&pos, &entry)) {
        T e = entry->key;
        r->unit += repr(e)->unit;
        if(rest)
           r->unit += ", ";
        --rest;
    }
    r->unit += "])";
    return r;
}

template<class T> __ss_int set<T>::__len__() {
    return used;
}

template <class T> __ss_bool set<T>::__contains__(T key) {
    long hash = hasher(key);
	setentry<T> *entry;

	entry = lookup(key, hash);

	return __mbool(entry->use==active);
}

template <class T> __ss_bool set<T>::__contains__(setentry<T>* entry) {
	entry = lookup(entry->key, entry->hash);

	return __mbool(entry->use == active);
}

template <class T> void *set<T>::clear()
{
	setentry<T> *entry, *table;
	int table_is_malloced;
#if defined( _MSC_VER )
	size_t fill;
#else
	ssize_t fill;
#endif
	setentry<T> small_copy[MINSIZE];

    table = this->table;
	table_is_malloced = table != smalltable;

	/* This is delicate.  During the process of clearing the set,
	 * decrefs can cause the set to mutate.  To avoid fatal confusion
	 * (voice of experience), we have to make the set empty before
	 * clearing the slots, and never refer to anything via so->ref while
	 * clearing.
	 */
	fill = this->fill;
	if (table_is_malloced)
		EMPTY_TO_MINSIZE(this);

	else if (fill > 0) {
		/* It's a small table with something that needs to be cleared.
		 * Afraid the only safe way is to copy the set entries into
		 * another small table first.
		 */
		// ffao: is this really needed without reference counting?
		//memcpy(small_copy, table, sizeof(small_copy));
		//table = small_copy;
		EMPTY_TO_MINSIZE(this);
	}
	/* else it's a small table that's already empty */

	/* if (table_is_malloced)
		PyMem_DEL(table); */
	return NULL;
}


template<class T> template<class U> void *set<T>::update(U *iter) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        add(e);
    END_FOR
    return NULL;
}

template <class T> void *set<T>::update(set<T>* other)
{
	register int i;
	register setentry<T> *entry;

	/* if (other == this || other->used == 0)
		// a.update(a) or a.update({}); nothing to do
		return 0; */
	/* Do one big resize at the start, rather than
	 * incrementally resizing as we insert new keys.  Expect
	 * that there will be no (or few) overlapping keys.
	 */
	if ((fill + other->used)*3 >= (mask+1)*2)
	   resize((used + other->used)*2);
	for (i = 0; i <= other->mask; i++) {
		entry = &other->table[i];
		if (entry->use == active) {
			insert_key(entry->key, entry->hash);
		}
	}
    return NULL;
}

template<class T> set<T> *set<T>::__ss_union(pyiter<T> *s) {
    set<T> *c = new set<T>(this->frozen);
    *c = *this;
    c->update(s);

    return c;
}

template<class T> set<T> *set<T>::__ss_union(set<T> *s) {
    set<T> *a, *b;
    set<T> *c = new set<T>(this->frozen);

    if(len(s) < len(this)) { a = s; b = this; }
    else { a = this; b = s; }

    *c = *b;
    c->update(a);

    return c;
}

template<class T> set<T> *set<T>::symmetric_difference(set<T> *s) {
    set<T> *a, *b;
    set<T> *c = new set<T>(this->frozen);

    if(len(s) < len(this)) { a = s; b = this; }
    else { a = this; b = s; }

    *c = *b;

    int pos = 0;
    setentry<T> *entry;

    while (a->next(&pos, &entry)) {
        if (b->__contains__(entry)) 
            c->discard(entry->key);
        else
            c->add(entry);
    }

    return c;
}

template<class T> set<T> *set<T>::intersection(set<T> *s) {
    set<T> *a, *b;
    set<T> *c = new set<T>(this->frozen);

    if(len(s) < len(this)) { a = s; b = this; }
    else { a = this; b = s; }

    int pos = 0;
    setentry<T> *entry;

    while (a->next(&pos, &entry)) {
        if(b->__contains__(entry))
            c->add(entry);
    }

    return c;
}

template <class T> set<T>* set<T>::difference(set<T> *other)
{
    set<T>* result = new set<T>;
    int pos = 0;
    setentry<T> *entry;

    while (next(&pos, &entry)) {
        if (!other->__contains__(entry)) {
            result->add(entry);
        }
    }

    return result;
}

template<class T> set<T> *set<T>::__and__(set<T> *s) {
    return intersection(s);
}
template<class T> set<T> *set<T>::__or__(set<T> *s) {
    return __ss_union(s);
}
template<class T> set<T> *set<T>::__xor__(set<T> *s) {
    return symmetric_difference(s);
}
template<class T> set<T> *set<T>::__sub__(set<T> *s) {
    return difference(s);
}
template<class T> set<T> *set<T>::__iand__(set<T> *s) {
    *this = intersection(s);
    return this;
}
template<class T> set<T> *set<T>::__ior__(set<T> *s) {
    *this = __ss_union(s);
    return this;
}
template<class T> set<T> *set<T>::__ixor__(set<T> *s) {
    *this = symmetric_difference(s);
    return this;
}
template<class T> set<T> *set<T>::__isub__(set<T> *s) {
    *this = difference(s);
    return this;
}


template<class T> void *set<T>::difference_update(set<T> *s) {
    set<T> *c = difference(s);
    *this = *c; /* XXX don't copy */
    return NULL;
}

template<class T> void *set<T>::symmetric_difference_update(set<T> *s) {
    set<T> *c = symmetric_difference(s);
    *this = *c;
    return NULL;
}

template<class T> void *set<T>::intersection_update(set<T> *s) {
    set<T> *c = intersection(s);
    *this = *c;
    return NULL;
}

template<class T> set<T> *set<T>::copy() {
    set<T> *c = new set<T>(this->frozen);
    *c = *this;
    return c;
}

template<class T> __ss_bool set<T>::issubset(set<T> *s) {
    if(__len__() > s->__len__()) { return False; }
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN_NEW(e,this,1,2,3)
        if(!s->__contains__(e))
            return False;
    END_FOR
    return True;
}

template<class T> __ss_bool set<T>::issuperset(set<T> *s) {
    if(__len__() < s->__len__()) return False;
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN_NEW(e,s,1,2,3)
        if(!__contains__(e))
            return False;
    END_FOR
    return True;
}

template<class T> __ss_bool set<T>::issubset(pyiter<T> *s) {
    return issubset(new set<T>(s));
}

template<class T> __ss_bool set<T>::issuperset(pyiter<T> *s) {
    return issuperset(new set<T>(s));
}

template<class T> set<T> *set<T>::__copy__() {
    set<T> *c = new set<T>();
    *c = *this;
    return c;
}

template<class T> set<T> *set<T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    set<T> *c = new set<T>();
    memo->__setitem__(this, c);
    typename set<T>::for_in_unit e;
    typename set<T>::for_in_loop __3;
    int __2;
    set<T> *__1;
    FOR_IN_NEW(e,this,1,2,3)
        c->add(__deepcopy(e, memo));
    END_FOR
    return c;
}

template<class T> __setiter<T>::__setiter(set<T> *p) {
    this->p = p;
    this->pos = 0;
    this->si_used = p->used;
}

template<class T> T __setiter<T>::next() {
    if (si_used != p->used) {
        si_used = -1;
        __throw_set_changed();
    }
    int ret = p->next(&pos, &entry);
    if (!ret) __throw_stop_iteration();
    return entry->key;
}

/* tuple2 methods */

template<class T> void tuple2<T, T>::__init2__(T a, T b) {
    units.push_back(a);
    units.push_back(b);
}

template<class T> tuple2<T, T>::tuple2() {
    this->__class__ = cl_tuple;
}

template<class T> tuple2<T, T>::tuple2(int count, ...) {
    this->__class__ = cl_tuple;
    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        T t = va_arg(ap, T);
        this->units.push_back(t);
    }
    va_end(ap);
}

template<class T> template<class U> tuple2<T, T>::tuple2(U *iter) {
    this->__class__ = cl_tuple;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        this->units.push_back(e);
    END_FOR
}

template<class T> tuple2<T, T>::tuple2(list<T> *p) {
    this->__class__ = cl_tuple;
    this->units = p->units;
}

template<class T> tuple2<T, T>::tuple2(tuple2<T, T> *p) {
    this->__class__ = cl_tuple;
    this->units = p->units;
}

template<class T> tuple2<T, T>::tuple2(str *s) {
    this->__class__ = cl_tuple;
    this->units.resize(len(s));
    int sz = s->unit.size();
    for(int i=0; i<sz; i++)
        this->units[i] = __char_cache[((unsigned char)(s->unit[i]))];
}

template<class T> T tuple2<T, T>::__getfirst__() {
    return this->units[0];
}
template<class T> T tuple2<T, T>::__getsecond__() {
    return this->units[1];
}
template<class T> inline T tuple2<T, T>::__getfast__(__ss_int i) {
    i = __wrap(this, i);
    return this->units[i];
}

template<class T> __ss_int tuple2<T, T>::__len__() {
    return units.size();
}

template<class T> T tuple2<T, T>::__getitem__(__ss_int i) {
    i = __wrap(this, i);
    return units[i];
}

template<class T> str *tuple2<T, T>::__repr__() {
    str *r = new str("(");
    for(int i = 0; i<this->__len__();i++) {
        r->unit += repr(this->units[i])->unit;
        if(this->__len__() == 1 )
            r->unit += ",";
        if(i<this->__len__()-1)
            r->unit += ", ";
    }
    r->unit += ")";
    return r;
}

template<class T> tuple2<T,T> *tuple2<T, T>::__add__(tuple2<T,T> *b) {
    tuple2<T,T> *c = new tuple2<T,T>();
    for(int i = 0; i<this->__len__();i++)
        c->units.push_back(this->units[i]);
    for(int i = 0; i<b->__len__();i++)
        c->units.push_back(b->units[i]);
    return c;
}
template<class T> tuple2<T,T> *tuple2<T, T>::__iadd__(tuple2<T,T> *b) {
    return __add__(b);
}

template<class T> tuple2<T,T> *tuple2<T, T>::__mul__(__ss_int b) {
    tuple2<T,T> *c = new tuple2<T,T>();
    if(b<=0) return c;
    __ss_int hop = this->__len__(); /* XXX merge with list */
    if(hop==1)
        c->units.insert(c->units.begin(), b, this->units[0]);
    else
        for(__ss_int i=0; i<b; i++)
            for(__ss_int j=0; j<hop; j++)
                c->units.push_back(this->units[j]);
    return c;
}
template<class T> tuple2<T,T> *tuple2<T, T>::__imul__(__ss_int b) {
    return __mul__(b);
}

template<class T> __ss_bool tuple2<T, T>::__contains__(T a) {
    for(int i=0; i<this->__len__(); i++)
        if(__eq(this->units[i], a))
            return True;
    return False;
}

template<class T> __ss_bool tuple2<T, T>::__eq__(pyobj *p) {
    tuple2<T,T> *b;
    b = (tuple2<T,T> *)p;
    unsigned int sz = this->units.size();
    if(b->units.size() != sz)
        return False;
    for(unsigned int i=0; i<sz; i++)
        if(!__eq(this->units[i], b->units[i]))
            return False;
    return True;
}

template<class T> tuple2<T,T> *tuple2<T, T>::__slice__(__ss_int x, __ss_int l, __ss_int u, __ss_int s) {
    tuple2<T,T> *c = new tuple2<T,T>();
    slicenr(x, l, u, s, this->__len__());
    if(s == 1) {
        c->units.resize(u-l);
        memcpy(&(c->units[0]), &(this->units[l]), sizeof(T)*(u-l));
    } else if(s > 0)
        for(int i=l; i<u; i += s)
            c->units.push_back(units[i]);
    else
        for(int i=l; i>u; i += s)
            c->units.push_back(units[i]);
    return c;
}

template<class T> int tuple2<T, T>::__hash__() {
    int seed = 0;
    int sz = this->units.size();
    for(int i = 0; i<sz; i++)
        seed = hash_combine(seed, hasher<T>(this->units[i]));
    return seed;
}

template<class T> tuple2<T,T> *tuple2<T,T>::__copy__() {
    tuple2<T,T> *c = new tuple2<T,T>();
    c->units = this->units;
    return c;
}

template<class T> tuple2<T,T> *tuple2<T,T>::__deepcopy__(dict<void *, pyobj *> *memo) {
    tuple2<T,T> *c = new tuple2<T,T>();
    memo->__setitem__(this, c);
    c->units.resize(this->__len__());
    for(int i=0; i<this->__len__(); i++)
        c->units[i] = __deepcopy(this->units[i], memo);
    return c;
}

template<class T> inline bool tuple2<T,T>::for_in_has_next(int i) {
    return i != units.size(); /* XXX opt end cond */
}

template<class T> inline T tuple2<T,T>::for_in_next(int &i) {
    return units[i++];
}

#ifdef __SS_BIND
template<class T> tuple2<T, T>::tuple2(PyObject *p) {
    if(!PyTuple_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (tuple expected)"));

    this->__class__ = cl_tuple;
    int size = PyTuple_Size(p);
    for(int i=0; i<size; i++)
        this->units.push_back(__to_ss<T>(PyTuple_GetItem(p, i)));
}

template<class T> PyObject *tuple2<T, T>::__to_py__() {
    int len = this->__len__();
    PyObject *p = PyTuple_New(len);
    for(int i=0; i<len; i++)
        PyTuple_SetItem(p, i, __to_py(this->__getitem__(i)));
    return p;
}
#endif

/* tuple2 methods (binary) */

template<class A, class B> void tuple2<A, B>::__init2__(A a, B b) {
    first = a;
    second = b;
}

template<class A, class B> tuple2<A, B>::tuple2() {
    this->__class__ = cl_tuple;
}

template<class A, class B> tuple2<A, B>::tuple2(int, A a, B b) {
    this->__class__ = cl_tuple;
    first = a;
    second = b;
}

template<class A, class B> A tuple2<A, B>::__getfirst__() {
    return first;
}
template<class A, class B> B tuple2<A, B>::__getsecond__() {
    return second;
}

template<class A, class B> __ss_int tuple2<A, B>::__len__() {
    return 2;
}

template<class A, class B> __ss_bool tuple2<A, B>::__eq__(tuple2<A,B> *b) {
    return __mbool(__eq(first, b->__getfirst__()) && __eq(second, b->__getsecond__()));
}

template<class A, class B> __ss_int tuple2<A, B>::__cmp__(pyobj *p) {
    if (!p) return 1;
    tuple2<A,B> *b = (tuple2<A,B> *)p;
    if(int c = __cmp(first, b->first)) return c;
    return __cmp(second, b->second);
}

template<class A, class B> int tuple2<A, B>::__hash__() {
    int seed = 0;
    seed = hash_combine(seed, hasher<A>(first));
    seed = hash_combine(seed, hasher<B>(second));
    return seed;
}

template<class A, class B> str *tuple2<A, B>::__repr__() {
    __GC_STRING s = "("+repr(first)->unit+", "+repr(second)->unit+")";
    return new str(s);
}

template<class A, class B> tuple2<A,B> *tuple2<A,B>::__copy__() {
    return new tuple2<A,B>(2, first, second);
}
template<class A, class B> tuple2<A,B> *tuple2<A,B>::__deepcopy__(dict<void *, pyobj *> *memo) {
    tuple2<A,B> *n = new tuple2<A,B>();
    memo->__setitem__(this, n);
    n->first = __deepcopy(first, memo);
    n->second = __deepcopy(second, memo);
    return n;
}

#ifdef __SS_BIND
template<class A, class B> tuple2<A, B>::tuple2(PyObject *p) {
    if(!PyTuple_Check(p))
        throw new TypeError(new str("error in conversion to Shed Skin (tuple expected)"));

    this->__class__ = cl_tuple;
    first = __to_ss<A>(PyTuple_GetItem(p, 0));
    second = __to_ss<B>(PyTuple_GetItem(p, 1));
}

template<class A, class B> PyObject *tuple2<A, B>::__to_py__() {
    PyObject *p = PyTuple_New(2);
    PyTuple_SetItem(p, 0, __to_py(first));
    PyTuple_SetItem(p, 1, __to_py(second));
    return p;
}
#endif

/* binding args */

#ifdef __SS_BIND
template<class T> T __ss_arg(const char *name, int pos, int has_default, T default_value, PyObject *args, PyObject *kwargs) {
    PyObject *kwarg;
    int nrofargs = PyTuple_Size(args);
    if (pos < nrofargs)
        return __to_ss<T>(PyTuple_GetItem(args, pos));
    else if (kwargs && (kwarg = PyDict_GetItemString(kwargs, name)))
        return __to_ss<T>(kwarg);
    else if (has_default)
        return default_value;
    else
        throw new TypeError(new str("missing argument"));
}
#endif

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

template<class T> T __seqiter<T>::next() {
    if(counter==size)
        __throw_stop_iteration();
    return p->__getitem__(counter++);
}

template<class K, class V> __dictiterkeys<K, V>::__dictiterkeys(dict<K,V> *p) {
    this->p = p;
    this->pos = 0;
    this->si_used = p->used;
}

template<class K, class V> K __dictiterkeys<K, V>::next() {
    if (si_used != p->used) {
        si_used = -1;
        __throw_dict_changed();
    }
    int ret = p->next(&pos, &entry);
    if (!ret) __throw_stop_iteration();
    return entry->key;
}

template<class K, class V> __dictitervalues<K, V>::__dictitervalues(dict<K,V> *p) {
    this->p = p;
    this->pos = 0;
    this->si_used = p->used;
}

template<class K, class V> V __dictitervalues<K, V>::next() {
    if (si_used != p->used) {
        si_used = -1;
        __throw_dict_changed();
    }
    int ret = p->next(&pos, &entry);
    if (!ret) __throw_stop_iteration();
    return entry->value;
}

template<class K, class V> __dictiteritems<K, V>::__dictiteritems(dict<K,V> *p) {
    this->p = p;
    this->pos = 0;
    this->si_used = p->used;
}

template<class K, class V> tuple2<K, V> *__dictiteritems<K, V>::next() {
    if (si_used != p->used) {
        si_used = -1;
        __throw_dict_changed();
    }
    int ret = p->next(&pos, &entry);
    if (!ret) __throw_stop_iteration();
    return new tuple2<K, V>(2, entry->key, entry->value);
}

/* sum */

template<class A> struct __sumtype1 { typedef A type; };
template<> struct __sumtype1<__ss_bool> { typedef int type; };

template<class A, class B> struct __sumtype2 { typedef A type; };
template<> struct __sumtype2<__ss_bool, __ss_bool> { typedef __ss_int type; };
template<> struct __sumtype2<__ss_bool, __ss_int> { typedef __ss_int type; };
template<> struct __sumtype2<__ss_bool, double> { typedef double type; };
template<> struct __sumtype2<__ss_int, double> { typedef double type; };

template <class U> typename __sumtype1<typename U::for_in_unit>::type __sum(U *iter) {
    typename __sumtype1<typename U::for_in_unit>::type result;
    result = (typename __sumtype1<typename U::for_in_unit>::type)0;
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    bool first = true;
    FOR_IN_NEW(e,iter,1,2,3)
        if(first) {
            result = (typename __sumtype1<typename U::for_in_unit>::type)e;
            first = false;
        }
        else
            result = __add(result, (typename __sumtype1<typename U::for_in_unit>::type)e);
    END_FOR
    return result;
}

template <class U, class B> typename __sumtype2<typename U::for_in_unit,B>::type __sum(U *iter, B b) {
    typename __sumtype1<typename U::for_in_unit>::type result1 = __sum(iter);
    return __add((typename __sumtype2<typename U::for_in_unit,B>::type)b, (typename __sumtype2<typename U::for_in_unit,B>::type)result1);
}

/* max */

template<class A, class B> typename A::for_in_unit ___max(int, B (*key)(typename A::for_in_unit), A *iter) {
    typename A::for_in_unit max;
    B maxkey, maxkey2;
    int first = 1;
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        if(key) {
            maxkey2 = key(e);
            if(first || __cmp(maxkey2, maxkey) == 1) {
                max = e;
                maxkey = maxkey2;
            }
        } else if(first || __cmp(e, max) == 1)
            max = e;
        if(first)
            first = 0;
    END_FOR
    if(first)
        throw new ValueError(new str("max() arg is an empty sequence"));
    return max;
}

/* XXX copy-pasto */
template<class A, class B> typename A::for_in_unit ___max(int, pycall1<B, typename A::for_in_unit> *key, A *iter) {
    typename A::for_in_unit max;
    B maxkey, maxkey2;
    int first = 1;
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        if(key) {
            maxkey2 = key->__call__(e);
            if(first || __cmp(maxkey2, maxkey) == 1) {
                max = e;
                maxkey = maxkey2;
            }
        } else if(first || __cmp(e, max) == 1)
            max = e;
        if(first)
            first = 0;
    END_FOR
    if(first)
        throw new ValueError(new str("max() arg is an empty sequence"));
    return max;
}
template<class A> typename A::for_in_unit ___max(int nn, int, A *iter) { return ___max(nn, (int (*)(typename A::for_in_unit))0, iter); }

template<class T, class B> inline T ___max(int, B (*key)(T), T a, T b) { return (__cmp(key(a), key(b))==1)?a:b; }
template<class T> inline  T ___max(int, int, T a, T b) { return (__cmp(a, b)==1)?a:b; }

template<class T, class B> T ___max(int n, B (*key)(T), T a, T b, T c, ...) {
    T m = ___max(2, key, ___max(2, key, a, b), c);
    B maxkey = key(m);
    va_list ap;
    va_start(ap, c);
    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(key(t),maxkey)==1)
            m=t;
    }
    va_end(ap);
    return m;
}
template<class T> T ___max(int n, int key, T a, T b, T c, ...) {
    T m = ___max(2, key, ___max(2, key, a, b), c);
    va_list ap;
    va_start(ap, c);
    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(t,m)==1) m=t;
    }
    va_end(ap);
    return m;
}

/* min */

template<class A, class B> typename A::for_in_unit ___min(int, B (*key)(typename A::for_in_unit), A *iter) {
    typename A::for_in_unit min;
    B minkey, minkey2;
    int first = 1;
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        if(key) {
            minkey2 = key(e);
            if(first || __cmp(minkey2, minkey) == -1) {
                min = e;
                minkey = minkey2;
            }
        } else if(first || __cmp(e, min) == -1)
            min = e;
        if(first)
            first = 0;
    END_FOR
    if(first)
        throw new ValueError(new str("min() arg is an empty sequence"));
    return min;
}
template<class A> typename A::for_in_unit ___min(int nn, int, A *iter) { return ___min(nn, (int (*)(typename A::for_in_unit))0, iter); }

template<class T, class B> inline T ___min(int, B (*key)(T), T a, T b) { return (__cmp(key(a), key(b))==-1)?a:b; }
template<class T> inline  T ___min(int, int, T a, T b) { return (__cmp(a, b)==-1)?a:b; }

template<class T, class B> T ___min(int n, B (*key)(T), T a, T b, T c, ...) {
    T m = ___min(2, key, ___min(2, key, a, b), c);
    B minkey = key(m);
    va_list ap;
    va_start(ap, c);
    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(key(t),minkey)==-1)
            m=t;
    }
    va_end(ap);
    return m;
}
template<class T> T ___min(int n, int key, T a, T b, T c, ...) { /* XXX */
    T m = ___min(2, key, ___min(2, key, a, b), c);
    va_list ap;
    va_start(ap, c);
    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(t,m)==-1)
            m=t;
    }
    va_end(ap);
    return m;
}

/* sorted */

template <class U, class V, class W> list<typename U::for_in_unit> *sorted(U *iter, V cmp, W key, __ss_int reverse) {
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    list<typename U::for_in_unit> *l = new list<typename U::for_in_unit>();
    FOR_IN_NEW(e,iter,1,2,3)
        l->units.push_back(e);
    END_FOR
    l->sort(cmp, key, reverse);
    return l;
}

template <class A, class V, class W> list<A> *sorted(list<A> *x, V cmp, W key, __ss_int reverse) {
    list<A> *l = new list<A>();
    l->units = x->units;
    l->sort(cmp, key, reverse);
    return l;
}

template <class A, class V, class W> list<A> *sorted(tuple2<A,A> *x, V cmp, W key, __ss_int reverse) {
    list<A> *l = new list<A>();
    l->units = x->units;
    l->sort(cmp, key, reverse);
    return l;
}

template <class V, class W> list<str *> *sorted(str *x, V cmp, W key, __ss_int reverse) {
    list<str *> *l = new list<str *>(x);
    l->sort(cmp, key, reverse);
    return l;
}

/* reversed */

template<class A> class __ss_reverse : public __iter<A> {
public:
    pyseq<A> *p;
    __ss_int i;
    __ss_reverse(pyseq<A> *p) {
        this->p = p;
        i = len(p);
    }

    A __get_next() {
        if(i>0)
            return p->__getitem__(--i); /* XXX avoid wrap, str spec? */
        this->__stop_iteration = true;
    }
};

template <class A> __ss_reverse<A> *reversed(pyiter<A> *x) {
    return new __ss_reverse<A>(new list<A>(x));
}
template <class A> __ss_reverse<A> *reversed(pyseq<A> *x) {
    return new __ss_reverse<A>(x);
}
__iter<__ss_int> *reversed(__xrange *x);

/* enumerate */

template<class A> class __enumiter : public __iter<tuple2<__ss_int, A> *> {
public:
    __iter<A> *p;
    __ss_int i;

    __enumiter(pyiter<A> *p) {
        this->p = ___iter(p);
        i = 0;
    }

    tuple2<__ss_int, A> *next() {
        return new tuple2<__ss_int, A>(2, i++, p->next());
    }
};

template <class A> __iter<tuple2<__ss_int, A> *> *enumerate(pyiter<A> *x) {
    return new __enumiter<A>(x);
}

/* zip */

list<tuple2<void *, void *> *> *__zip(int nn);

template <class A> list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *> *__zip(int nn, A *iter) {
    list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *> *result = (new list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *>());
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        result->append((new tuple2<typename A::for_in_unit, typename A::for_in_unit>(1, e)));
    END_FOR
    return result;
}

template <class A, class B> list<tuple2<typename A::for_in_unit, typename B::for_in_unit> *> *__zip(int, A *itera, B *iterb) {
    list<tuple2<typename A::for_in_unit, typename B::for_in_unit> *> *result = (new list<tuple2<typename A::for_in_unit, typename B::for_in_unit> *>());
    tuple2<typename A::for_in_unit, typename B::for_in_unit> *tuples;
    int count = -1;
    if(A::is_pyseq && B::is_pyseq) {
        count = __SS_MIN(len(itera), len(iterb));
        tuples = new tuple2<typename A::for_in_unit, typename B::for_in_unit>[count];
        result->units.resize(count);
    }
    typename A::for_in_unit e;
    typename A::for_in_loop __3 = itera->for_in_init();
    typename B::for_in_unit f;
    typename B::for_in_loop __6 = iterb->for_in_init();
    int i = 0;
    while(itera->for_in_has_next(__3) and iterb->for_in_has_next(__6)) {
        e = itera->for_in_next(__3);
        f = iterb->for_in_next(__6);
        if(count == -1)
            result->append((new tuple2<typename A::for_in_unit, typename B::for_in_unit>(2, e, f)));
        else {
            tuples[i].__init2__(e, f);
            result->units[i] = &tuples[i];
            i++;
        }
    }
    return result;
}

template <class A, class B, class C> list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *> *__zip(int, A *itera, B *iterb, C *iterc) {
    list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *> *result = (new list<tuple2<typename A::for_in_unit, typename A::for_in_unit> *>());
    tuple2<typename A::for_in_unit, typename A::for_in_unit> *tuples;
    int count = -1;
    if(A::is_pyseq && B::is_pyseq && C::is_pyseq) {
        count = __SS_MIN3(len(itera), len(iterb), len(iterc));
        tuples = new tuple2<typename A::for_in_unit, typename A::for_in_unit>[count];
        result->units.resize(count);
    }
    typename A::for_in_unit e;
    typename A::for_in_loop __3 = itera->for_in_init();
    typename B::for_in_unit f;
    typename B::for_in_loop __6 = iterb->for_in_init();
    typename C::for_in_unit g;
    typename C::for_in_loop __7 = iterc->for_in_init();
    int i = 0;
    while(itera->for_in_has_next(__3) and iterb->for_in_has_next(__6) and iterc->for_in_has_next(__7)) {
        e = itera->for_in_next(__3);
        f = iterb->for_in_next(__6);
        g = iterc->for_in_next(__7);
        if(count == -1)
            result->append((new tuple2<typename A::for_in_unit, typename A::for_in_unit>(3, e, f, g)));
        else {
            tuples[i].units.push_back(e);
            tuples[i].units.push_back(f);
            tuples[i].units.push_back(g);
            result->units[i] = &tuples[i];
            i++;
        }
    }
    return result;
}

/* next */

template <class A> A next(__iter<A> *iter1, A fillvalue) {
    try {
        return iter1->next();
    } catch(StopIteration *) {
        return fillvalue;
    }
}
template <class A> A next(__iter<A> *iter1, void *) { return next(iter1, (A)NULL); }
template <class A> A next(__iter<A> *iter1) { return iter1->next(); }

/* map */

template <class A, class B> list<B> *map(int, B (*func)(typename A::for_in_unit), A *iter) {
    if(!func)
        throw new ValueError(new str("'map' function argument cannot be None"));
    list<B> *result = new list<B>();
    int count = -1;
    if(A::is_pyseq) {
        count = len(iter);
        result->units.resize(count);
    }
    typename A::for_in_unit e;
    typename A::for_in_loop __3 = iter->for_in_init();
    int i = 0;
    while(iter->for_in_has_next(__3)) {
        e = iter->for_in_next(__3);
        if(count == -1)
            result->append((*func)(e));
        else
            result->units[i++] = (*func)(e);
    }
    return result;
}

template <class A, class B, class C> list<A> *map(int n, A (*func)(B, C), pyiter<B> *b, pyiter<C> *c) {
    if(!func)
        throw new ValueError(new str("'map' function argument cannot be None"));
    list<A> *result = new list<A>();
    __iter<B> *itb = b->__iter__();
    __iter<C> *itc = c->__iter__();
    B nextb;
    C nextc;
    int total;
    while(1) {
        total = 0;
        try { nextb = next(itb); total += 1; } catch (StopIteration *) { nextb = 0; }
        try { nextc = next(itc); total += 1; } catch (StopIteration *) { nextc = 0; }
        if(total == 0)
            break;
        result->append((*func)(nextb, nextc));
    }
    return result;
}

template <class A, class B, class C, class D> list<A> *map(int, A (*func)(B, C, D), pyiter<B> *b1, pyiter<C> *b2, pyiter<D> *b3) {
    if(!func)
        throw new ValueError(new str("'map' function argument cannot be None"));
    list<A> *result = new list<A>();
    __iter<B> *itb1 = b1->__iter__();
    __iter<C> *itb2 = b2->__iter__();
    __iter<D> *itb3 = b3->__iter__();
    B nextb1;
    C nextb2;
    D nextb3;
    int total;
    while(1)  {
        total = 0;
        try { nextb1 = next(itb1); total += 1; } catch (StopIteration *) { nextb1 = 0; }
        try { nextb2 = next(itb2); total += 1; } catch (StopIteration *) { nextb2 = 0; }
        try { nextb3 = next(itb3); total += 1; } catch (StopIteration *) { nextb3 = 0; }
        if(total == 0)
            break;
        result->append((*func)(nextb1, nextb2, nextb3));
    }
    return result;
}

/* reduce */

template<class A> typename A::for_in_unit reduce(typename A::for_in_unit (*func)(typename A::for_in_unit, typename A::for_in_unit), A *iter, typename A::for_in_unit initial) {
    typename A::for_in_unit result = initial;
    typename A::for_in_loop __7 = iter->for_in_init();
    while(iter->for_in_has_next(__7))
        result = (*func)(result, iter->for_in_next(__7));
    return result;
}

template<class A> typename A::for_in_unit reduce(typename A::for_in_unit (*func)(typename A::for_in_unit, typename A::for_in_unit), A *iter) {
    typename A::for_in_unit result;
    typename A::for_in_loop __7 = iter->for_in_init();
    int first = 1;
    while(iter->for_in_has_next(__7)) {
        if(first) {
            result = iter->for_in_next(__7);
            first = 0;
        } else
            result = (*func)(result, iter->for_in_next(__7));
    }
    if(first) 
        throw new TypeError(new str("reduce() of empty sequence with no initial value"));
    return result;
}

/* filter */

template <class A, class B> list<typename A::for_in_unit> *filter(B (*func)(typename A::for_in_unit), A *iter) {
    list<typename A::for_in_unit> *result = new list<typename A::for_in_unit>();
    typename A::for_in_unit e;
    typename A::for_in_loop __3 = iter->for_in_init();
    while(iter->for_in_has_next(__3)) {
        e = iter->for_in_next(__3);
        if(func) {
            if(___bool((*func)(e)))
                result->append(e);
        } else if(___bool(e))
            result->append(e);
    }
    return result;
}

template <class A, class B> tuple2<A,A> *filter(B (*func)(A), tuple2<A,A> *a) {
    tuple2<A,A> *result = new tuple2<A,A>();
    int size = len(a);
    A e;
    for(int i=0; i<size; i++) {
        e = a->units[i];
        if(func) {
            if(___bool((*func)(e)))
                result->units.push_back(e);
        } else if(___bool(e))
            result->units.push_back(e);
    }
    return result;
}

template <class B> str *filter(B (*func)(str *), str *a) {
    str *result = new str();
    int size = len(a);
    char e;
    str *c;
    for(int i=0; i<size; i++) {
        e = a->unit[i];
        if(func) {
            c = __char_cache[((unsigned char)e)];
            if(___bool((*func)(c)))
                result->unit.push_back(e);
        } else 
            result->unit.push_back(e);
    }
    return result;
}

template <class A> list<A> *filter(void *func, pyiter<A> *a) { return filter(((int(*)(A))(func)), a); }
inline str *filter(void *func, str *a) { return filter(((int(*)(str *))(func)), a); }
template <class A> tuple2<A,A> *filter(void *func, tuple2<A,A> *a) { return filter(((int(*)(A))(func)), a); }

/* pow */

template<class A, class B> double __power(A a, B b);
template<> inline double __power(__ss_int a, double b) { return pow(a,b); }
template<> inline double __power(double a, __ss_int b) { return pow(a,b); }

complex *__power(complex *a, complex *b);
complex *__power(complex *a, __ss_int b);
complex *__power(complex *a, double b);

template<class A> A __power(A a, A b);
template<> inline double __power(double a, double b) { return pow(a,b); }

template<> inline __ss_int __power(__ss_int a, __ss_int b) {
    switch(b) {
        case 2: return a*a;
        case 3: return a*a*a;
        case 4: return a*a*a*a;
        case 5: return a*a*a*a*a;
        case 6: return a*a*a*a*a*a;
        case 7: return a*a*a*a*a*a*a;
        case 8: return a*a*a*a*a*a*a*a;
        case 9: return a*a*a*a*a*a*a*a*a;
        case 10: return a*a*a*a*a*a*a*a*a*a;
    }
    __ss_int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = (res*tmp);
        }
        tmp = (tmp*tmp);
        b = (b/2);
    }
    return res;
}

#ifdef __SS_LONG
inline __ss_int __power(__ss_int a, __ss_int b, __ss_int c) {
    __ss_int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = ((res*tmp)%c);
        }
        tmp = ((tmp*tmp)%c);
        b = (b/2);
    }
    return res;
}
#endif

inline int __power(int a, int b, int c) {
    int res, tmp;

    res = 1;
    tmp = a;

    while((b>0)) {
        if ((b%2)) {
            res = ((res*tmp)%c);
        }
        tmp = ((tmp*tmp)%c);
        b = (b/2);
    }
    return res;
}

/* division */

template<class A, class B> double __divs(A a, B b);
template<> inline double __divs(__ss_int a, double b) { return (double)a/b; }
template<> inline double __divs(double a, __ss_int b) { return a/((double)b); }

template<class A> A __divs(A a, A b);
template<> inline double __divs(double a, double b) { return a/b; }
#ifdef __SS_LONG
template<> inline __ss_int __divs(__ss_int a, __ss_int b) {
    if(a<0 && b>0) return (a-b+1)/b;
    else if(b<0 && a>0) return (a-b-1)/b;
    else return a/b;
}
#endif
template<> inline int __divs(int a, int b) {
    if(a<0 && b>0) return (a-b+1)/b;
    else if(b<0 && a>0) return (a-b-1)/b;
    else return a/b;
}

template<class A, class B> double __floordiv(A a, B b);
template<> inline double __floordiv(__ss_int a, double b) { return floor((double)a/b); }
template<> inline double __floordiv(double a, __ss_int b) { return floor(a/((double)b)); }

template<class A> inline A __floordiv(A a, A b) { return a->__floordiv__(b); }
template<> inline double __floordiv(double a, double b) { return floor(a/b); }

#ifdef __SS_LONG /* XXX */
template<> inline __ss_int __floordiv(__ss_int a, __ss_int b) { return (__ss_int)floor((double)a/b); } /* XXX */
#endif
template<> inline int __floordiv(int a, int b) { return (int)floor((double)a/b); } /* XXX */

/* modulo */

template<class A> A __mods(A a, A b);
#ifdef __SS_LONG /* XXX */
template<> inline __ss_int __mods(__ss_int a, __ss_int b) {
    int m = a%b;
    if((m<0 && b>0)||(m>0 && b<0)) m+=b;
    return m;
}
#endif
template<> inline int __mods(int a, int b) {
    int m = a%b;
    if((m<0 && b>0)||(m>0 && b<0)) m+=b;
    return m;
}
template<> inline double __mods(double a, double b) {
    double f = fmod(a,b);
    if((f<0 && b>0)||(f>0 && b<0)) f+=b;
    return f;
}

template<class A, class B> double __mods(A a, B b);
#ifdef __SS_LONG
template<> inline double __mods(__ss_int a, double b) { return __mods((double)a, b); }
template<> inline double __mods(double a, __ss_int b) { return __mods(a, (double)b); }
#endif
template<> inline double __mods(int a, double b) { return __mods((double)a, b); }
template<> inline double __mods(double a, int b) { return __mods(a, (double)b); }

/* divmod */

template<class A> inline tuple2<A, A> *divmod(A a, A b) { return a->__divmod__(b); }
template<> inline tuple2<double, double> *divmod(double a, double b) {
    return new tuple2<double, double>(2, __floordiv(a,b), __mods(a,b));
}
#ifdef __SS_LONG
template<> inline tuple2<__ss_int, __ss_int> *divmod(__ss_int a, __ss_int b) {
    return new tuple2<__ss_int, __ss_int>(2, __floordiv(a,b), __mods(a,b));
}
#endif
template<> inline tuple2<int, int> *divmod(int a, int b) {
    return new tuple2<int, int>(2, __floordiv(a,b), __mods(a,b));
}
template<class A, class B> tuple2<double, double> *divmod(A a, B b);
#ifdef __SS_LONG
template<> inline tuple2<double, double> *divmod(double a, __ss_int b) { return divmod(a, (double)b); }
template<> inline tuple2<double, double> *divmod(__ss_int a, double b) { return divmod((double)a, b); }
#endif
template<> inline tuple2<double, double> *divmod(double a, int b) { return divmod(a, (double)b); }
template<> inline tuple2<double, double> *divmod(int a, double b) { return divmod((double)a, b); }

tuple2<complex *, complex *> *divmod(complex *a, double b);
tuple2<complex *, complex *> *divmod(complex *a, __ss_int b);

/* dict.fromkeys */

namespace __dict__ {
    template<class A, class B> dict<A, B> *fromkeys(pyiter<A> *f, B b) {
        dict<A, B> *d = new dict<A, B>();
        typename pyiter<A>::for_in_unit e;
        typename pyiter<A>::for_in_loop __3;
        int __2;
        pyiter<A> *__1;
        FOR_IN_NEW(e,f,1,2,3)
            d->__setitem__(e, b);
        END_FOR
        return d;
    }

    template<class A> dict<A, void *> *fromkeys(pyiter<A> *f) {
        return fromkeys(f, (void *)0);
    }

}

/* string formatting */

int __fmtpos(str *fmt);
int __fmtpos2(str *fmt);
void __modfill(str **fmt, pyobj *t, str **s);
str *mod_to_c2(pyobj *t);
int_ *mod_to_int(pyobj *t);
float_ *mod_to_float(pyobj *t);

template<class T> str *__modtuple(str *fmt, tuple2<T,T> *t) {
    list<pyobj *> *vals = new list<pyobj *>();
    for(int i=0;i<len(t);i++)
        vals->append(___box(t->__getitem__(i)));
    return __mod4(fmt, vals);
}

template<class A, class B> str *__modtuple(str *fmt, tuple2<A,B> *t) {
    list<pyobj *> *vals = new list<pyobj *>(2, ___box(t->__getfirst__()), ___box(t->__getsecond__()));
    return __mod4(fmt, vals);
}

template<class T> str *__moddict(str *v, dict<str *, T> *d) {
    str *const_6 = new str(")");
    int i, pos, pos2;
    list<str *> *names = (new list<str *>());

    while((pos = __fmtpos2(v)) != -1) {
        pos2 = v->find(const_6, pos);
        names->append(v->__slice__(3, (pos+2), pos2, 0));
        v = (v->__slice__(2, 0, (pos+1), 0))->__add__(v->__slice__(1, (pos2+1), 0, 0));
    }

    list<pyobj *> *vals = new list<pyobj *>();
    for(i=0;i<len(names);i++)
        vals->append(___box(d->__getitem__(names->__getitem__(i))));
    return __mod4(v, vals);
}

/* boxing */

template<class T> T ___box(T t) { return t; } /* XXX */
#ifdef __SS_LONG
int_ *___box(__ss_int);
#endif
int_ *___box(int);
int_ *___box(unsigned int); /* XXX */
int_ *___box(unsigned long);
int_ *___box(unsigned long long);
bool_ *___box(__ss_bool);
float_ *___box(double);

/* any */

template<class A> __ss_bool any(A *iter) {
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        if(___bool(e))
            return True;
    END_FOR
    return False;
}

/* all */

template<class A> __ss_bool all(A *iter) {
    typename A::for_in_unit e;
    typename A::for_in_loop __3;
    int __2;
    A *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        if(!___bool(e))
            return False;
    END_FOR
    return True;
}

/* ord, chr */

int ord(str *c);

static void __throw_chr_out_of_range() { /* improve inlining */
    throw new ValueError(new str("chr() arg not in range(256)"));
}
inline str *chr(int i) {
    if(i < 0 || i > 255)
        __throw_chr_out_of_range();
    return __char_cache[i];
}
inline str *chr(__ss_bool b) { return chr(b.value); }

template<class T> inline str *chr(T t) {
    return chr(t->__int__());
}

#ifdef __SS_LONG
inline str *chr(__ss_int i) {
    return chr((int)i);
}

template<> inline str *hex(__ss_int i) {
    return hex((int)i);
}
template<> inline str *oct(__ss_int i) {
    return oct((int)i);
}
template<> inline str *bin(__ss_int i) {
    return bin((int)i);
}
#endif

/* complex */

template<class T> complex::complex(T t) {
    __class__ = cl_complex;
    real = __float(t);
    imag = 0;
}

#ifdef __SS_BIND
PyObject *__ss__newobj__(PyObject *, PyObject *args, PyObject *kwargs);
#endif

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

/* file */

template<class U> void *file::writelines(U *iter) {
    __check_closed();
    typename U::for_in_unit e;
    typename U::for_in_loop __3;
    int __2;
    U *__1;
    FOR_IN_NEW(e,iter,1,2,3)
        write(e);
    END_FOR
    return NULL;
}

} // namespace __shedskin__
#endif
