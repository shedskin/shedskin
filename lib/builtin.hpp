#ifndef BUILTIN_HPP
#define BUILTIN_HPP

#ifdef __SS_BIND
#include <Python.h>
#endif

#include <gc/gc_allocator.h>
#include <gc/gc_cpp.h>

#include <vector>
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

#include <ext/hash_map>
#include <ext/hash_set>

namespace __shedskin__ {

/* builtin class forward declarations */

class class_;
class pyobj;
class str;
class int_;
class float_;
class file;
class complex;

template <class T> class pyiter;
template <class T> class pyseq;

template <class T> class __iter;
template <class T> class __seqiter;
template <class T> class __setiter;
template <class T, class U> class __dictiterkeys;
template <class T, class U> class __dictitervalues;
template <class T, class U> class __dictiteritems;
class __fileiter;
class __striter;
class __xrange;
class __rangeiter;

template <class T> class list;
template <class A, class B> class tuple2;

template <class T> class set;
template <class K, class V> class dict;

class Exception;
class AssertionError; class KeyError; class ValueError; class IndexError;
class NotImplementedError; class IOError; class OSError; class SyntaxError;
class StopIteration; class TypeError; class RuntimeError; class OverflowError;

/* builtin function forward declarations */

template<class T> list<T> *__list(pyiter<T> *p);
template<class T> list<T> *__list(pyseq<T> *p);

template<class T> tuple2<T,T> *__tuple(pyiter<T> *p);
template<class T> tuple2<T,T> *__tuple(pyseq<T> *p);

template<class K, class V> dict<K,V> *__dict(pyiter<tuple2<K, V> *> *p);
template<class K, class V> dict<K,V> *__dict(dict<K,V> *p);
template<class K> dict<K,K> *__dict(pyiter<list<K> *> *p);

int __int(str *s, int base);
inline int __int() { return 0; }
template<class T> inline int __int(T t) { return t->__int__(); }
template<> inline int __int(str *s) { return __int(s, 10); }
template<> inline int __int(int i) { return i; }
template<> inline int __int(bool b) { return b; }
template<> inline int __int(double d) { return (int)d; }

inline double __float() { return 0; }
template<class T> inline double __float(T t) { return t->__float__(); }
template<> inline double __float(int p) { return p; }
template<> inline double __float(bool b) { return __float((int)b); }
template<> inline double __float(double d) { return d; }
template<> double __float(str *s);

str *__str();
template<class T> str *__str(T t);
template<> str *__str(double t);
str *__str(int t, int base=10);
str *__str(bool b);

template<class T> str *repr(T t);
template<> str *repr(double t);
template<> str *repr(int t);
template<> str *repr(bool b);
template<> str *repr(void *t);

file *open(str *name, str *flags = 0);
str *raw_input(str *msg = 0);

void print(int n,  ...);
void print(file *f, int n, ...);
void printc(int n, ...); /* print comma */
void printc(file *f, int n, ...);

int isinstance(pyobj *, class_ *);
int isinstance(pyobj *, tuple2<class_ *, class_ *> *);

list<int> *range(int b);
list<int> *range(int a, int b, int s=1);

__xrange *xrange(int b);
__xrange *xrange(int a, int b, int s=1);

int ord(str *c);

str *chr(int i);
str *chr(bool b);
template<class T> str *chr(T t) {
    return chr(t->__int__());
}

double ___round(double a);
double ___round(double a, int n);

template<class T> inline T __abs(T t) { return t->__abs__(); }
template<> inline int __abs(int a) { return a<0?-a:a; }
template<> inline double __abs(double a) { return a<0?-a:a; }
inline int __abs(bool b) { return __abs((int)b); }
double __abs(complex *c);

template<class T> str *hex(T t) {
    return t->__hex__();
}
template<> str *hex(int a);
template<> str *hex(bool b);

template<class T> str *oct(T t) {
    return t->__oct__();
}
template<> str *oct(int a);
template<> str *oct(bool b);

str *__mod4(str *fmt, list<pyobj *> *vals);
str *__modct(str *fmt, int n, ...);
str *__modcd(str *fmt, list<str *> *l, ...);

template<class T> str *__modtuple(str *fmt, tuple2<T,T> *t); 
template<class A, class B> str *__modtuple(str *fmt, tuple2<A,B> *t);

/* internal use */

#define __GC_VECTOR(T) std::vector< T, gc_allocator< T > >
#define __GC_STRING std::basic_string<char,std::char_traits<char>,gc_allocator<char> >
#define __GC_HASH_SET __gnu_cxx::hash_set<T, hashfunc<T>, hasheq<T>, gc_allocator<T> >
#define __GC_HASH_MAP __gnu_cxx::hash_map<K, V, hashfunc<K>, hasheq<K>, gc_allocator<std::pair<K, V> > >

#ifdef __sun
#define INFINITY __builtin_inff()
#endif

#define __SS_MIN(a,b) ((a) < (b) ? (a) : (b))
#define __SS_MIN3(a,b,c) (__SS_MIN((a), __SS_MIN((b), (c)))) 
#define __SS_MAX(a,b) ((a) > (b) ? (a) : (b))
#define __SS_MAX3(a,b,c) (__SS_MAX((a), __SS_MAX((b), (c))))

void __init();
void __exit(int code=0);
void quit(int code=0);
void __ss_exit(int code=0);
void slicenr(int x, int &l, int&u, int&s, int len);

/* hashing */

static inline int hash_combine(int seed, int other) {
    return seed ^ (other + 0x9e3779b9 + (seed << 6) + (seed >> 2));
}

template<class T> inline int hasher(T t) {
    if(t == NULL) return 0;
    return t->__hash__();
};
template<> inline int hasher(int a) { return a; }
template<> inline int hasher(void *a) { return (intptr_t)a; }
template<> inline int hasher(double v) {
    int hipart, expo; /* modified from CPython */
    v = frexp(v, &expo);
    v *= 32768.0; /* 2**15 */
    hipart = (int)v;   /* take the top 16 bits */
    v = (v - (double)hipart) * 32768.0; /* get the next 16 bits */
    return hipart + (int)v + (expo << 15);
}

template<class T> class hashfunc
{
    public: int operator()(T t) const { return hasher<T>(t); }
};

template<class T> class hasheq {
    public: int operator()(T t, T v) const { return __eq(t,v); }
};

/* comparison */

template<class T> inline int __cmp(T a, T b) {
    return a->__cmp__(b);
}

template<> inline int __cmp(int a, int b) { 
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
} 

template<> inline int __cmp(double a, double b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}
template<> inline int __cmp(void *a, void *b) {
    if(a < b) return -1;
    else if(a > b) return 1;
    return 0;
}

template<class T> int cpp_cmp(T a, T b) { 
    return __cmp(a, b) == -1;
}
template<class T> int cpp_cmp_rev(T a, T b) {
    return __cmp(a, b) == 1;
}
template<class T> class cpp_cmp_custom {
    typedef int (*hork)(T, T);
    hork cmp;
    public:
    cpp_cmp_custom(hork a) { cmp = a; }
    int operator()(T a, T b) const { return cmp(a,b) == -1; }
};
template<class T> class cpp_cmp_custom_rev {
    typedef int (*hork)(T, T);
    hork cmp;
    public:
    cpp_cmp_custom_rev(hork a) { cmp = a; }
    int operator()(T a, T b) const { return cmp(a,b) == 1; }
};

template<class T> struct dereference {}; 
template<class T> struct dereference <T*> {
    typedef T type;
};

/* binding */

#ifdef __SS_BIND
template<class T> T __to_ss(PyObject *p) {
    if(p==Py_None) return NULL;
    return new (typename dereference<T>::type)(p); /* isn't C++ pretty :-) */
}

template<> int __to_ss(PyObject *p);
template<> double __to_ss(PyObject *p);
template<> void *__to_ss(PyObject *p);

template<class T> PyObject *__to_py(T t) {
    if(!t) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    return t->__to_py__(); 
}

template<> PyObject *__to_py(int i);
template<> PyObject *__to_py(double i);
template<> PyObject *__to_py(void *);

extern dict<void *, void *> *__ss_proxy;
#endif

/* externs */

extern class_ *cl_str_, *cl_int_, *cl_float_, *cl_complex, *cl_list, *cl_tuple, *cl_dict, *cl_set, *cl_object, *cl_xrange, *cl_rangeiter;

extern __GC_VECTOR(str *) __letters;

/* builtin class declarations */

class pyobj : public gc {
public:
    class_ *__class__;

    virtual str *__repr__();
    virtual str *__str__() { return __repr__(); }

    virtual int __hash__() {
        return __gnu_cxx::hash<intptr_t>()((intptr_t)this);
    }

    virtual int __eq__(pyobj *p) { return this == p; }
    virtual int __ne__(pyobj *p) { return !__eq__(p); }

    virtual int __cmp__(pyobj *p) {
        return __cmp<void *>(this, p);
    }

    virtual int __gt__(pyobj *p) { return __cmp__(p) == 1; }
    virtual int __lt__(pyobj *p) { return __cmp__(p) == -1; }
    virtual int __ge__(pyobj *p) { return __cmp__(p) != -1; }
    virtual int __le__(pyobj *p) { return __cmp__(p) != 1; }

    virtual pyobj *__copy__() { return this; }
    virtual pyobj *__deepcopy__(dict<void *, pyobj *> *memo) { return this; }

    virtual int __len__() { return 1; } /* XXX exceptions? */
    virtual int __nonzero__() { return __len__() != 0; }
    virtual int __int__() { return 0; }

};

class class_: public pyobj {
public:
    int low, high;
    str *__name__;

    class_(const char *name, int low, int high);
    str *__repr__();
    int __eq__(pyobj *c);

};

class int_ : public pyobj {
public:
    int unit;
    int_(int i);
    str *__repr__();
};

class float_ : public pyobj {
public:
    double unit;
    float_(double f);
    str *__repr__();
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

    int __eq__(pyobj *p);
    int __hash__();
    int __nonzero__();

#ifdef __SS_BIND
    complex(PyObject *);
    PyObject *__to_py__();
#endif
};

template<class T> complex::complex(T t) {
    __class__ = cl_complex;
    real = __float(t);
    imag = 0;
}

template <class T> class pyiter : public pyobj {
public:
    virtual __iter<T> *__iter__() = 0;

};

template<class T> class __iter : public pyiter<T> {
public:
    virtual T next() = 0;

    __iter<T> *__iter__() { return this; }

    T temp; /* used by FOR_IN macros */
    int for_has_next();
    T for_get_next();

    str *__repr__();
};

template <class T> __iter<T> *___iter(pyiter<T> *p) {
    return p->__iter__();
}

template <class T> class pyseq : public pyiter<T> {
public:
    std::vector<T, gc_allocator<T> > units;

    virtual int __len__() {
        return units.size();
    }

    virtual T __getitem__(int i) {
        i = __wrap(this, i);
        return units[i];
    }

    virtual void *append(T t) {
        units.push_back(t);
        return NULL;
    }

    virtual void slice(int x, int l, int u, int s, pyseq<T> *c) {
        slicenr(x, l, u, s, __len__());
        if(s == 1) {
            c->units.resize(u-l);
            memcpy(&(c->units[0]), &(this->units[l]), sizeof(T)*(u-l));
        } else if(s > 0)
            for(int i=l; i<u; i += s)
                c->append(units[i]);
        else
            for(int i=l; i>u; i += s)
                c->append(units[i]);
    }

    virtual int __cmp__(pyobj *p) {
        pyseq<T> *b = (pyseq<T> *)p;
        int i, cmp;
        int mnm = __min(this->__len__(), b->__len__());

        for(i = 0; i < mnm; i++) {
            cmp = __cmp(this->units[i], b->units[i]);
            if(cmp)
                return cmp;
        }
        return __cmp(this->__len__(), b->__len__());
    }

    virtual int __contains__(T t) {

    }

    void resize(int n) {
        units.resize(n);
    }

    __seqiter<T> *__iter__() { 
        return new __seqiter<T>(this);
    }

};

template <class T> class __seqiter : public __iter<T> {
public:
    int counter;
    pyseq<T> *p;
    __seqiter<T>();
    __seqiter<T>(pyseq<T> *p);
    T next();
};

template <class T> class list : public pyseq<T> {
public:
    using pyseq<T>::units;

    list();
    list(int count, ...);

    void clear();
    void *__setitem__(int i, T e);
    void *__delitem__(int i);
    //void init(int count, ...);
    int empty();
    list<T> *__slice__(int x, int l, int u, int s);
    void *__setslice__(int x, int l, int u, int s, pyiter<T> *b);
    void *__setslice__(int x, int l, int u, int s, list<T> *b);
    void *__delete__(int i);
    void *__delete__(int x, int l, int u, int s);
    void *__delslice__(int a, int b);
    int __contains__(T a);

    list<T> *__add__(list<T> *b);
    list<T> *__mul__(int b);

    list<T> *__iadd__(pyiter<T> *b);
    list<T> *__iadd__(pyseq<T> *b);
    list<T> *__iadd__(str *s);
    list<T> *__imul__(int n);

    void *extend(pyiter<T> *p);
    void *extend(pyseq<T> *p);
    void *extend(str *s);

    int index(T a);
    int index(T a, int s);
    int index(T a, int s, int e); 

    int count(T a);
    str *__repr__();
    int __eq__(pyobj *l);

    T __getfirst__() { return this->units[0]; } // XXX remove
    T __getsecond__() { return this->units[1]; }
    T __getfast__(int i) {
        i = __wrap(this, i);
        return this->units[i];
    }

    T pop();
    T pop(int m);
    void *remove(T e);
    void *insert(int m, T e);

    void *reverse();
    void *sort(int (*cmp)(T, T), int key, int reverse);

    list<T> *__copy__();
    list<T> *__deepcopy__(dict<void *, pyobj *> *memo);

#ifdef __SS_BIND
    list(PyObject *);
    PyObject *__to_py__();
#endif
};

template<class A, class B> class tuple2 : public pyseq<A> {
public:
    A first;
    B second;

    tuple2();
    tuple2(int n, A a, B b);

    void __init2__(A a, B b) {
        first = a;
        second = b;
    }

    A __getfirst__();
    B __getsecond__();

    str *__repr__();

    //void init(int count, A a, B b);

    int __contains__(A a);
    int __contains__(B b);

    int __len__();

    int __eq__(tuple2<A,B> *b);
    int __cmp__(pyobj *p);
    int __hash__();

    tuple2<A,B> *__copy__();
    tuple2<A,B> *__deepcopy__(dict<void *, pyobj *> *memo);

#ifdef __SS_BIND
    tuple2(PyObject *p);
    PyObject *__to_py__();
#endif
};
 
class str : public pyseq<str *> {
public:
    __GC_STRING unit;
    int cached_hash; 

    str();
    str(const char *s);
    str(__GC_STRING s);
    str(const char *s, int size); /* '\0' delimiter in C */

    int __contains__(str *s);
    str *strip(str *chars=0);
    str *lstrip(str *chars=0);
    str *rstrip(str *chars=0);
    list<str *> *split(str *sep=0, int maxsplit=-1);
    int __eq__(pyobj *s);
    str *__add__(str *b);
    str *join(pyiter<str *> *l);
    str *__join(pyseq<str *> *l, int total_len);
    str *join(pyseq<str *> *l);
    str *join(str *s);
    str *__str__();
    str *__repr__();
    str *__mul__(int n);
    str *__getitem__(int i);
    str *__getfirst__();
    str *__getsecond__();
    int __len__();
    str *__slice__(int x, int l, int u, int s);

    list<str *> *rsplit(str *sep = 0, int maxsplit = -1);
    int istitle(void);
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

    int count(str *s, int start=0);
    int count(str *s, int start, int end);
    int startswith(str *s, int start=0);
    int startswith(str *s, int start, int end);
    int endswith(str *s, int start=0);
    int endswith(str *s, int start, int end);

    str *upper();
    str *lower();
    str *title();
    str *capitalize();
    str *replace(str *a, str *b, int c=-1);
    str *translate(str *table, str *delchars=0);
    str *swapcase();
    str *center(int w, str *fill=0);

    int __ctype_function(int (*cfunc)(int));
    int isspace();
    int isalpha();
    int isdigit();
    int islower();
    int isupper();
    int isalnum();
    
    str *zfill(int width);
    str *expandtabs(int width=8); 

    str *ljust(int width, str *fchar=0);
    str *rjust(int width, str *fchar=0);

    int __cmp__(pyobj *p);
    int __hash__();

    int __int__(); /* XXX compilation warning for int(pyseq<str *> *) */ 

    __seqiter<str *> *__iter__();

    //str *sorted();

    str *__iadd__(str *b);
    str *__imul__(int n);

#ifdef __SS_BIND
    str(PyObject *p); 
    PyObject *__to_py__();
#endif
};

class __striter : public __seqiter<str *> {
public:
    int counter, size;
    str *p;

    __striter(str *p); 
    str *next();
}; 

template<class T> class tuple2<T,T> : public pyseq<T> {
public:
    using pyseq<T>::units;

    tuple2();
    tuple2(int count, ...);

    void __init2__(T a, T b) {
        units.resize(2);
        units[0] = a;
        units[1] = b;
    }

    T __getfirst__();
    T __getsecond__();

    T __getfast__(int i);

    str *__repr__();

    tuple2<T,T> *__add__(tuple2<T,T> *b);
    tuple2<T,T> *__mul__(int b);

    tuple2<T,T> *__iadd__(tuple2<T,T> *b);
    tuple2<T,T> *__imul__(int n);

    //void init(int count, ...);

    int __contains__(T a);
    int __eq__(pyobj *p);

    tuple2<T,T> *__slice__(int x, int l, int u, int s);

    int __hash__();

    tuple2<T,T> *__deepcopy__(dict<void *, pyobj *> *memo);
    tuple2<T,T> *__copy__();

#ifdef __SS_BIND
    tuple2(PyObject *p);
    PyObject *__to_py__();
#endif
};

template <class K, class V> class dict : public pyiter<K> {
public:
    __GC_HASH_MAP units;
    typename __GC_HASH_MAP::iterator it;

    dict();
    dict(int count, ...);
    void *__setitem__(K k, V v);
    V __getitem__(K k);
    void *__delitem__(K k);
    list<K> *keys();
    list<V> *values();
    list<tuple2<K, V> *> *items();
    int __len__();
    str *__repr__();
    int has_key(K k);
    void *clear();
    dict<K,V> *copy();
    V get(K k);
    V get(K k, V v);
    V pop(K k);
    tuple2<K, V> *popitem();
    void *update(dict<K, V> *e);
    int __contains__(K k);
    int __eq__(pyobj *e);
    V setdefault(K k, V v=0);

    __dictiterkeys<K, V> *__iter__();
    __dictiterkeys<K, V> *iterkeys();
    __dictitervalues<K, V> *itervalues();
    __dictiteritems<K, V> *iteritems();

    dict<K, V> *__deepcopy__(dict<void *, pyobj *> *memo);
    dict<K, V> *__copy__();

    void *__addtoitem__(K k, V v);

#ifdef __SS_BIND
    dict(PyObject *);
    PyObject *__to_py__();
#endif
};

template <class K, class V> class __dictiterkeys : public __iter<K> {
public:
    dict<K, V> *p;
    typename __GC_HASH_MAP::iterator iter;
    int counter;

    __dictiterkeys<K, V>(dict<K, V> *p);
    K next();
};

template <class K, class V> class __dictitervalues : public __iter<V> {
public:
    dict<K, V> *p;
    typename __GC_HASH_MAP::iterator iter;
    int counter;

    __dictitervalues<K, V>(dict<K, V> *p);
    V next();
};

template <class K, class V> class __dictiteritems : public __iter<tuple2<K, V> *> {
public:
    dict<K, V> *p;
    typename __GC_HASH_MAP::iterator iter;
    int counter;

    __dictiteritems<K, V>(dict<K, V> *p);
    tuple2<K, V> *next();
};

const int MINSIZE = 8;
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

template<class T> class set : public pyiter<T> { 
public:
    int frozen;
    int fill;
    int used;
    int mask;
    setentry<T> *table;
    setentry<T> smalltable[MINSIZE];

    set(int frozen=0);
    set(pyiter<T> *p, int frozen=0);
    set<T>& operator=(const set<T>& other);

    void *add(T key);
    void *add(setentry<T>* entry);
    void *discard(T key); 
    int do_discard(T key);
    void *remove(T key);
    T pop();

    str* __repr__();

    int __contains__(T key);
    int __contains__(setentry<T>* entry);
    int __len__();

    void *clear();
    set<T> *copy();

    void *update(pyiter<T> *s);
    void *update(const set<T>* other);

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
    
    int issubset(pyiter<T> *s);
    int issubset(set<T> *s);
    int issuperset(set<T> *s);
    int issuperset(pyiter<T> *s);

    int __gt__(set<T> *s);
    int __lt__(set<T> *s);
    int __ge__(set<T> *s);
    int __le__(set<T> *s);
    int __eq__(pyobj *p);
    int __cmp__(pyobj *p);

    __setiter<T> *__iter__() {
        return new __setiter<T>(this);
    }
    
    set<T> *__copy__();
    set<T> *__deepcopy__(dict<void *, pyobj *> *memo);

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

class file : public pyiter<str *> {
public:
    FILE *f;
    int endoffile;
    char print_lastchar;
    int print_space;

    str *name;
    str *mode;
    int closed;

    file(str *name, str *mode=0);
    file(FILE *g);
    file();

    str *read(int n=-1);
    str *readline(int n=-1);
    list<str *> *readlines();
    void *write(str *s);
    void *writelines(pyseq<str *> *p);
    void *flush();
    int __ss_fileno();

    void __check_closed();

    virtual int getchar();
    virtual void *putchar(int c);
    virtual void *seek(int i, int w=0);
    virtual void *close();

    int tell();

    str *__repr__();

    __iter<str *> *__iter__();
    str *next();

};

class __fileiter : public __iter<str *> {
public:
    file *p;
    __fileiter(file *p); 
    str *next();
}; 

class object : public pyobj {
public:
    object() { this->__class__ = cl_object; }

};

class __xrange : public pyiter<int> {
public:
    int a, b, s;

    __xrange(int a, int b, int s);
    __iter<int> *__iter__();
    int __len__();
    str *__repr__();
};

/* exceptions */

class Exception: public pyobj {
public:
    str *msg;
    Exception(str *msg=0) { __init__(msg); }
    int __init__(str *msg) { this->msg = msg; }
    int __init__(void *msg) { this->msg = 0; } /* XXX */
    int __init__(int msg) { this->msg = 0; } /* XXX */
    str *__repr__() { return msg ? msg : new str("0"); }

#ifdef __SS_BIND
   virtual PyObject *__to_py__() { return PyExc_Exception; }
#endif
};

class AssertionError : public Exception { 
public: 
    AssertionError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_AssertionError; }
#endif
};

class EOFError : public Exception {
public: 
    EOFError(str *msg=0) : Exception(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_EOFError; }
#endif
};

class FloatingPointError : public Exception {
public: 
    FloatingPointError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_FloatingPointError; }
#endif
};

class KeyError : public Exception { 
public: 
    KeyError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_KeyError; }
#endif
};

class IndexError : public Exception { 
public: 
    IndexError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_IndexError; }
#endif
};

class IOError : public Exception { 
public: 
    IOError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_IOError; }
#endif
};

class KeyboardInterrupt : public Exception {
public: 
    KeyboardInterrupt(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_KeyboardInterrupt; }
#endif
};

class MemoryError : public Exception {
public: 
    MemoryError(str *msg=0) : Exception(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_MemoryError; }
#endif
};

class NameError : public Exception {
public: 
    NameError(str *msg=0) : Exception(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NameError; }
#endif
};

class NotImplementedError : public Exception { 
public: 
    NotImplementedError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_NotImplementedError; }
#endif
};

class OSError : public Exception { 
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

class OverflowError : public Exception { 
public: 
    OverflowError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_OverflowError; }
#endif
};

class RuntimeError : public Exception { 
public: 
    RuntimeError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_RuntimeError; }
#endif
};

class SyntaxError : public Exception { 
public: 
    SyntaxError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SyntaxError; }
#endif
};

class SystemError : public Exception {
public: 
    SystemError(str *msg=0) : Exception(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SystemError; }
#endif
};

class SystemExit : public Exception {
public: 
    SystemExit(str *msg=0) : Exception(msg) {}
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_SystemExit; }
#endif
};

class TypeError : public Exception { 
public: 
    TypeError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_TypeError; }
#endif
};

class ValueError : public Exception { 
public: 
    ValueError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ValueError; }
#endif
};

class ZeroDivisionError : public Exception {
public: 
    ZeroDivisionError(str *msg=0) : Exception(msg) {} 
#ifdef __SS_BIND
    PyObject *__to_py__() { return PyExc_ZeroDivisionError; }
#endif
};

class StopIteration : public Exception { public: StopIteration(str *msg=0) : Exception(msg) {} };

#define ASSERT(x, y) if(!(x)) throw new AssertionError(y);

#define FOR_IN(i, m, temp) \
    __ ## temp = ___iter(m); \
    while((__ ## temp)->for_has_next()) { \
        i = (__ ## temp)->for_get_next(); \

#define FOR_IN_SEQ(i, m, temp, n) \
    __ ## temp = m; \
    for(__ ## n = 0; __ ## n < (__ ## temp)->units.size(); __ ## n ++) { \
        i = (__ ## temp)->units[__ ## n]; \

#define FOR_IN_ZIP(a,b, k,l, t,u, n,m) \
    __ ## m = __SS_MIN(k->units.size(), l->units.size()); \
    __ ## t = k; \
    __ ## u = l; \
    for(__ ## n = 0; __ ## n < __ ## m; __ ## n ++) { \
        a = (__ ## t)->units[__ ## n]; \
        b = (__ ## u)->units[__ ## n]; 

#define FOR_IN_T2(i, m, obj, n) \
    __ ## obj = m; \
    for(__ ## n = 0; __ ## n < 2; __ ## n ++) { \
        if (! __ ## n) i = (__ ## obj)->__getfirst__(); \
        else i = (__ ## obj)->__getsecond__(); \

#define FAST_FOR(i, l, u, s, t1, t2) \
    if(s==0) \
        throw new ValueError(new str("range() step argument must not be zero")); \
    for(__ ## t1 = l, __ ## t2 = u; __ ## t1 < __ ## t2; __ ## t1 += s) { \
        i=__ ## t1; \

#define FAST_FOR_NEG(i, l, u, s, t1, t2) \
    if(s==0) \
        throw new ValueError(new str("range() step argument must not be zero")); \
    for(__ ## t1 = l, __ ## t2 = u; __ ## t1 > __ ## t2; __ ## t1 += s) { \
        i=__ ## t1; \

#define END_FOR }

template<class T> static inline int __wrap(T a, int i) {
    #ifndef NOWRAP
    if(i<0) return len(a)+i;
    #endif
    #ifndef NOBOUNDS 
        if(i<0 || i>= len(a)) 
            throw new IndexError(new str("index out of range")); 
    #endif
    return i;
}

#define ELEM(a,i) a->units[__wrap(a,i)]

/* representation */

template<class T> str *__str(T t) { if (!t) return new str("None"); return t->__str__(); }
template<class T> str *repr(T t) { if (!t) return new str("None"); return t->__repr__(); }

str *__str(void *);

/* return pointer to class object */

template<class T> class_ *__type(T t) { return t->__class__; }
template<> class_ *__type(int i);
template<> class_ *__type(double d);

/* equality, comparison */

template<class T> inline int __eq(T a, T b) { return ((a&&b)?(a->__eq__(b)):(a==b)); }
template<> inline int __eq(int a, int b) { return a == b; }
template<> inline int __eq(double a, double b) { return a == b; }
template<> inline int __eq(void *a, void *b) { return a == b; }
template<class T> inline int __ne(T a, T b) { return ((a&&b)?(a->__ne__(b)):(a!=b)); }
template<> inline int __ne(int a, int b) { return a != b; }
template<> inline int __ne(double a, double b) { return a != b; }
template<> inline int __ne(void *a, void *b) { return a != b; }
template<class T> inline int __gt(T a, T b) { return a->__gt__(b); }
template<> inline int __gt(int a, int b) { return a > b; }
template<> inline int __gt(double a, double b) { return a > b; }
template<class T> inline int __ge(T a, T b) { return a->__ge__(b); }
template<> inline int __ge(int a, int b) { return a >= b; }
template<> inline int __ge(double a, double b) { return a >= b; }
template<class T> inline int __lt(T a, T b) { return a->__lt__(b); }
template<> inline int __lt(int a, int b) { return a < b; }
template<> inline int __lt(double a, double b) { return a < b; }
template<class T> inline int __le(T a, T b) { return a->__le__(b); }
template<> inline int __le(int a, int b) { return a <= b; }
template<> inline int __le(double a, double b) { return a <= b; }

/* add */

template<class T> inline T __add(T a, T b) { return a->__add__(b); }
template<> inline int __add(int a, int b) { return a + b; }
template<> inline double __add(double a, double b) { return a + b; }

/* reverse */

template<class U> U __add2(double a, U b) { return b->__add__(a); }
template<class U> U __sub2(double a, U b) { return b->__rsub__(a); }
template<class T> T __mul2(int n, T a) { return a->__mul__(n); }
template<class T> T __mul2(double n, T a) { return a->__mul__(n); }
template<class T> T __div2(int n, T a) { return a->__rdiv__(n); }
template<class T> T __div2(double n, T a) { return a->__rdiv__(n); }

str *__add_strs(int n, str *a, str *b, str *c);
str *__add_strs(int n, str *a, str *b, str *c, str *d);
str *__add_strs(int n, str *a, str *b, str *c, str *d, str *e);
str *__add_strs(int n, ...);

/* deep copy */

template<class T> T __deepcopy(T t, dict<void *, pyobj *> *memo=0) {
    if(!memo) 
        memo = new dict<void *, pyobj *>();

    T u = (T)(memo->get(t, 0));

    if(u) return u;
    return (T)(t->__deepcopy__(memo));
}

template<> int __deepcopy(int i, dict<void *, pyobj *> *);
template<> double __deepcopy(double d, dict<void *, pyobj *> *);
template<> void *__deepcopy(void *p, dict<void *, pyobj *> *);

template<class T> T __copy(T t) { return (T)(t->__copy__()); }
template<> int __copy(int i);
template<> double __copy(double d);
template<> void *__copy(void *p);

/* len */

template<class T> int len(T x) { return x->__len__(); }
template<class T> inline int len(list<T> *x) { return x->units.size(); } /* XXX more general solution? */

/* bool */

inline int ___bool() { return 0; }
template<class T> inline int ___bool(T x) { return (x && x->__nonzero__()); }
template<> inline int ___bool(int x) { return x!=0; }
template<> inline int ___bool(bool x) { return (int)x; }
template<> inline int ___bool(double x) { return x!=0; }

/* logical and, or */

#define __OR(a, b, t) ((___bool(__ ## t = a))?(__ ## t):(b))
#define __AND(a, b, t) ((!___bool(__ ## t = a))?(__ ## t):(b))

/* __iter<T> methods */

template<class T> int __iter<T>::for_has_next() {
    try {
        temp = next();
    } catch(StopIteration *) {
        return 0;
    }
    return 1;
}
template<class T> T __iter<T>::for_get_next() {
    return temp;
}

/* dict<K, V> methods */

template<class K, class V> dict<K,V>::dict() {
    this->__class__ = cl_dict;
}

template<class K, class V> dict<K, V>::dict(int count, ...)  {
    this->__class__ = cl_dict;
    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        typedef tuple2<K, V> * bert;
        bert t = va_arg(ap, bert);
        __setitem__(t->__getfirst__(), t->__getsecond__());
    }
    va_end(ap);
}

#ifdef __SS_BIND
template<class K, class V> dict<K, V>::dict(PyObject *p) {
    if(!PyDict_Check(p)) 
        throw new TypeError(new str("error in conversion to Shed Skin (dictionary expected)"));
    
    this->__class__ = cl_dict;
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
    int len = this->__len__();
    for (it = units.begin(); it != units.end(); it++)
        PyDict_SetItem(p, __to_py(it->first), __to_py(it->second));
    return p;
}
#endif

template<class K, class V> void *dict<K,V>::__setitem__(K k, V v) {
    units[k] = v;
    return NULL;
}

template<class T> T __none() { return NULL; }
template<> int __none(); 
template<> double __none();

template<class K, class V> V dict<K,V>::get(K k) {
    it = units.find(k);
    if(it == units.end())
        return __none<V>();
    return it->second;
}

template<class K, class V> V dict<K,V>::get(K k, V v) {
    it = units.find(k);
    if(it == units.end())
        return v;
    return it->second;
}

template<class K, class V> V dict<K,V>::setdefault(K k, V v) {
    it = units.find(k);
    if(it == units.end())
    {
        this->__setitem__(k, v);
        return v;
    }

    return it->second;
}

template<class K, class V> V dict<K,V>::pop(K k) {
    V v = this->__getitem__(k);
    units.erase(k);
    return v;
}

template<class K, class V> void *dict<K,V>::__delitem__(K k) {
    units.erase(k);
    return NULL;
}

template<class K, class V> int dict<K,V>::__len__() {
    return units.size();
}

template<class K, class V> tuple2<K,V> *dict<K,V>::popitem() {
    it = units.begin();
    tuple2<K, V> *t = new tuple2<K, V>(2, it->first, it->second);
    units.erase(it->first);
    return t;
}

template<class K, class V> list<K> *dict<K,V>::keys() {
    list<K> *l = new list<K>();
    l->units.reserve(__len__());
    for (it = units.begin(); it != units.end(); it++)
        l->append(it->first);
    return l;
}

template<class K, class V> int dict<K,V>::has_key(K k) {
    return units.find(k) != units.end();
}

template<class K, class V> void *dict<K,V>::clear() {
    this->units.clear();
    return NULL;
}

template<class K, class V> dict<K,V> *dict<K,V>::copy() {
    dict<K,V> *n = new dict<K,V>();
    n->units = units;
    return n;
}

template<class K, class V> dict<K,V> *dict<K,V>::__copy__() {
    return copy();
}

template<class K, class V> dict<K,V> *dict<K,V>::__deepcopy__(dict<void *, pyobj *> *memo) {
    dict<K,V> *n = new dict<K,V>();
    memo->__setitem__(this, n);
    for (it = units.begin(); it != units.end(); it++)
        n->units[__deepcopy(it->first, memo)] = __deepcopy(it->second, memo);
    return n;
}

template<class K, class V> dict<K,V> *__dict(dict<K,V> *p) {
    return p->copy();
}

template<class K, class V> list<V> *dict<K,V>::values() {
    list<V> *l = new list<V>();
    l->units.reserve(__len__());
    for (it = units.begin(); it != units.end(); it++)
        l->append(it->second);
    return l;
}

template<class K, class V> void *dict<K,V>::update(dict<K,V> *e) {
    for (it = e->units.begin(); it != e->units.end(); it++)
        this->__setitem__(it->first, it->second);
    return NULL;
}

template<class K, class V> list<tuple2<K,V> *> *dict<K,V>::items() {
    list<tuple2<K,V> *> *l = new list<tuple2<K,V> *>();
    l->units.reserve(__len__());
    for (it = units.begin(); it != units.end(); it++)
        l->append(new tuple2<K,V>(2, it->first, it->second));
    return l;
}

template<class K, class V> int dict<K, V>::__contains__(K k) {
    return units.find(k) != units.end();
}

template<class K, class V> str *dict<K,V>::__repr__() {
    str *r = new str("{");
    int i = units.size();

    for (it = units.begin(); it != units.end(); i--, it++) {
        r->unit += repr(it->first)->unit + ": " + repr(it->second)->unit;
        if( i > 1 )
           r->unit += ", ";
    }

    r->unit += "}";
    return r;
}

template<class K, class V> V dict<K,V>::__getitem__(K k) {
    typename __GC_HASH_MAP::iterator iter;
    iter = units.find(k);
    if(iter == units.end()) throw new KeyError(repr(k));
    return iter->second;
}

template<class K, class V> void *dict<K,V>::__addtoitem__(K k, V v) {
    typename __GC_HASH_MAP::iterator iter;
    iter = units.find(k);
    if(iter == units.end()) throw new KeyError(repr(k));
    iter->second = __add(iter->second, v);
    return NULL;
}

template<class K, class V> int dict<K,V>::__eq__(pyobj *e) {
   dict<K, V> *b = (dict<K,V> *)e;
   if( b->__len__() != this->__len__()) return 0;

   K k;
   __iter<K> *__0;
   FOR_IN(k, this, 0)
       if( !b->__contains__(k) || !__eq(this->__getitem__(k), b->__getitem__(k)))
           return 0;
   END_FOR
   return 1;
} 

template<class K, class V> __dictiterkeys<K, V> *dict<K, V>::__iter__() { 
    return new __dictiterkeys<K, V>(this);
}

template<class K, class V> __dictiterkeys<K, V> *dict<K, V>::iterkeys() {
    return new __dictiterkeys<K, V>(this);
}

template<class K, class V> __dictitervalues<K, V> *dict<K, V>::itervalues() {
    return new __dictitervalues<K, V>(this);
} 

template<class K, class V> __dictiteritems<K, V> *dict<K, V>::iteritems() {
    return new __dictiteritems<K, V>(this);
} 
    
/* list<T> methods */

template<class T> list<T>::list() {
    this->__class__ = cl_list;
}

template<class T> list<T>::list(int count, ...)  {
    this->__class__ = cl_list;
    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        T t = va_arg(ap, T);
        append(t);
    }
    va_end(ap);
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

/*template<class T> void list<T>::init(int count, ...)  {
    clear();

    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        T t = va_arg(ap, T);
        append(t);
    }
    va_end(ap);
}*/

template<class T> void list<T>::clear() {
    units.resize(0);
}

template<class T> int list<T>::__eq__(pyobj *p) {
   list<T> *b = (list<T> *)p;
   int len = this->units.size();
   if(b->units.size() != len) return 0;
   for(int i = 0; i < len; i++)
       if(!__eq(this->units[i], b->units[i]))
           return 0;
   return 1;
}

template<class T> void *list<T>::extend(pyiter<T> *p) {
    __iter<T> *__0;
    T e;
    FOR_IN(e, p, 0)
        append(e); 
    END_FOR
    return NULL;
}

template<class T> void *list<T>::extend(pyseq<T> *p) {
    int l1, l2;
    l1 = this->__len__(); l2 = p->__len__();

    this->units.resize(l1+l2);
    memcpy(&(this->units[l1]), &(p->units[0]), sizeof(T)*l2);
    return NULL;
}

template<class T> void *list<T>::extend(str *s) {
    extend((pyiter<str *> *)s);
    return NULL;
}

template<class T> void *list<T>::__setitem__(int i, T e) {
    i = __wrap(this, i);
    units[i] = e;
    return NULL;
}

template<class T> void *list<T>::__delitem__(int i) {
    i = __wrap(this, i);
    units.erase(units.begin()+i,units.begin()+i+1);
    return NULL;
}

template<class T> int list<T>::empty() {
    return units.empty();
}

template<class T> list<T> *list<T>::__slice__(int x, int l, int u, int s) {
    list<T> *c = new list<T>();
    this->slice(x, l, u, s, c);
    return c;
}

template<class T> void *list<T>::__setslice__(int x, int l, int u, int s, pyiter<T> *b) {
    T e;
    list<T> *la = new list<T>(); /* XXX avoid intermediate list */
    __iter<T> *__0;
    FOR_IN(e, b, 0)
        la->units.push_back(e);
    END_FOR
    this->__setslice__(x, l, u, s, la);
}

template<class T> void *list<T>::__setslice__(int x, int l, int u, int s, list<T> *la) {
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
            throw new ValueError(__modtuple(new str("attempt to assign sequence of size %d to extended slice of size %d"), new tuple2<int,int>(2, len(la), slicesize)));  
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

template<class T> void *list<T>::__delete__(int i) {
    i = __wrap(this, i);
    units.erase(units.begin()+i,units.begin()+i+1);
    return NULL;
}

template<class T> void *list<T>::__delete__(int x, int l, int u, int s) {
    slicenr(x, l, u, s, this->__len__());

    if(s == 1)
        __delslice__(l, u);
    else {
        std::vector<T, gc_allocator<T> > v;
        for(int i=0; i<this->__len__();i++)
            if((i+l) % s)
                v.push_back(this->units[i]);
        units = v;
    }
    return NULL;
}

template<class T> void *list<T>::__delslice__(int a, int b) {
    if(a>this->__len__()) return NULL;
    if(b>this->__len__()) b = this->__len__();
    units.erase(units.begin()+a,units.begin()+b);
    return NULL;
}

template<class T> int list<T>::__contains__(T a) {
    int size = this->units.size();
    for(int i=0; i<size; i++)
        if(__eq(this->units[i], a))
            return 1;
    return 0;
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

template<class T> list<T> *list<T>::__mul__(int b) {
    list<T> *c = new list<T>();
    if(b<=0) return c;
    int len = this->units.size();
    if(len==1)
        c->units.assign(b, this->units[0]);
    else {
        c->units.resize(b*len);
        for(int i=0; i<b; i++)
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

template<class T> list<T> *list<T>::__iadd__(pyiter<T> *b) {
    extend(b);
    return this;
}
template<class T> list<T> *list<T>::__iadd__(pyseq<T> *b) {
    extend(b);
    return this;
}
template<class T> list<T> *list<T>::__iadd__(str *s) {
    extend(s);
    return this;
}

template<class T> list<T> *list<T>::__imul__(int n) { 
    int l1 = this->__len__();
    this->units.resize(l1*n);
    for(int i = 1; i <= n-1; i++)
        memcpy(&(this->units[l1*i]), &(this->units[0]), sizeof(T)*l1);
    return this;
}

template<class T> int list<T>::index(T a) { return index(a, 0, this->__len__()); }
template<class T> int list<T>::index(T a, int s) { return index(a, s, this->__len__()); }
template<class T> int list<T>::index(T a, int s, int e) {
    int one = 1;
    slicenr(7, s, e, one, this->__len__());
    for(int i = s; i<e;i++)
        if(__eq(a,units[i]))
            return i;
    throw new ValueError(new str("list.index(x): x not in list"));
} 

template<class T> int list<T>::count(T a) {
    int c = 0;
    int len = this->__len__();
    for(int i = 0; i<len;i++)
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

template<class T> T list<T>::pop(int m) {
    if (m<0) m = this->__len__()+m;
    T e = units[m];
    units.erase(units.begin()+m);
    return e;
}
template<class T> T list<T>::pop() {
    return pop(-1);
}

template<class T> void *list<T>::reverse() {
    std::reverse(this->units.begin(), this->units.end());
    return NULL;
}

template<class T> void *list<T>::sort(int (*cmp)(T, T), int key, int reverse) {
    if(cmp) {
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

template<class T> void *list<T>::insert(int m, T e) {
    if (m<0) m = this->__len__()+m;
    units.insert(units.begin()+m, e);
    return NULL;
}

template<class T> void *list<T>::remove(T e) {
    for(int i = 0; i < this->__len__(); i++)
        if(__eq(units[i], e)) {
            units.erase(units.begin()+i);
            return NULL;
        }
    return NULL;
}

template <class T> void *myallocate(int n) { return GC_MALLOC(n); }
template <> void *myallocate<int>(int n);

#define INIT_NONZERO_SET_SLOTS(so) do {				\
	(so)->table = (so)->smalltable;				\
	(so)->mask = MINSIZE - 1;				\
    } while(0)


#define EMPTY_TO_MINSIZE(so) do {				\
	memset((so)->smalltable, 0, sizeof((so)->smalltable));	\
	(so)->used = (so)->fill = 0;				\
	INIT_NONZERO_SET_SLOTS(so);				\
    } while(0)

template <class T> set<T>::set(int frozen) : frozen(frozen) {
    this->__class__ = cl_set;
    EMPTY_TO_MINSIZE(this);
}

#ifdef __SS_BIND
#if (PY_MAJOR_VERSION == 2)
#if (PY_MINOR_VERSION > 4)

template<class T> set<T>::set(PyObject *p) {
    this->__class__ = cl_set;
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
    list<T> *l = __list(this); /* XXX optimize */
    if(frozen)
        return PyFrozenSet_New(__to_py(l)); 
    else
        return PySet_New(__to_py(l));
}

#endif
#endif
#endif

template<class T> set<T>::set(pyiter<T> *p, int frozen) {
    this->__class__ = cl_set;
    this->frozen = frozen;
    EMPTY_TO_MINSIZE(this);

    update(p);
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
}

template<class T> int set<T>::__eq__(pyobj *p) {
    set<T> *b = (set<T> *)p;

    if( b->__len__() != this->__len__()) return 0;

    int pos = 0;
    setentry<T> *entry;
    while (next(&pos, &entry)) {
        if(!b->__contains__(entry))
            return 0;
    }
    return 1;
}

template <class T> void *set<T>::remove(T key) {
    if (!do_discard(key)) throw new KeyError(repr(key));
    return NULL;
}

template<class T> int set<T>::__ge__(set<T> *s) {
    return issuperset(s);
}

template<class T> int set<T>::__le__(set<T> *s) {
    return issubset(s);
}

template<class T> int set<T>::__lt__(set<T> *s) {
    return issubset(s);
}

template<class T> int set<T>::__gt__(set<T> *s) {
    return issuperset(s);
}

template<class T> int set<T>::__cmp__(pyobj *p) {
    //note: originally SS did cmp() by using issubset() and issuperset().
    //I'm, however, following the Python specifications here...
    throw new TypeError(new str("cannot compare sets using cmp()"));
}

template<class T> int set<T>::__hash__() {
    if(!this->frozen)
        throw new TypeError(new str("unhashable type: 'set'"));
    list<int> *seeds = new list<int>();

    T e;
    __iter<T> *__0;
    FOR_IN(e, this, 0)
        seeds->append(hasher<T>(e));
    END_FOR

    seeds->sort(0, 0, 0); /* XXX */
    int seed = 0;
    for(int i = 0; i < len(seeds); i++)
        seed = hash_combine(seed, seeds->units[i]);
    return seed;
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
	register size_t i;
	register size_t perturb;
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

template<class T> int set<T>::__len__() {
    return used;
}

template <class T> int set<T>::__contains__(T key) {
    long hash = hasher(key);
	setentry<T> *entry;

	entry = lookup(key, hash);

	return entry->use==active;
}

template <class T> int set<T>::__contains__(setentry<T>* entry) {
	entry = lookup(entry->key, entry->hash);

	return entry->use == active;
}

template <class T> void *set<T>::clear()
{
	setentry<T> *entry, *table;
	int table_is_malloced;
	ssize_t fill;
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

template<class T> void *set<T>::update(pyiter<T> *s) {
    T e;
    __iter<T> *__0;
    FOR_IN(e, s, 0)
        add(e);
    END_FOR
    return NULL;
}

template <class T> void *set<T>::update(const set<T>* other)
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
        setentry<T> *new_entry = c->lookup(entry->key, entry->hash);
        if (new_entry->use == active) {
            new_entry->use = dummy;
            c->used--;
       }
        else {
            if (!(new_entry->use)) c->fill++;
            memcpy(new_entry, entry, sizeof(setentry<T>));
            c->used++;
        }
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

template<class T> int set<T>::issubset(set<T> *s) {
    if(__len__() > s->__len__()) { return 0; }
    T e;
    __iter<T> *__0;
    FOR_IN(e, this, 0)
        if(!s->__contains__(e))
            return 0;
    END_FOR
    return 1;
}

template<class T> int set<T>::issuperset(set<T> *s) {
    if(__len__() < s->__len__()) return 0;
    T e;
    __iter<T> *__0;
    FOR_IN(e, s, 0)
        if(!__contains__(e))
            return 0;
    END_FOR
    return 1;
}

template<class T> int set<T>::issubset(pyiter<T> *s) {
    return issubset(new set<T>(s));
}

template<class T> int set<T>::issuperset(pyiter<T> *s) {
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

    T e;
    __iter<T> *__0;
    FOR_IN(e, this, 0)
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
        throw new RuntimeError(new str("set changed size during iteration"));
        si_used = -1;
    }
    int ret = p->next(&pos, &entry);
    if (!ret) throw new StopIteration();
    return entry->key;
}

/* tuple2<T, T> */

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

template<class T> T tuple2<T, T>::__getfirst__() { 
    return this->units[0]; 
}
template<class T> T tuple2<T, T>::__getsecond__() { 
    return this->units[1]; 
}
template<class T> T tuple2<T, T>::__getfast__(int i) { 
    return this->units[i]; 
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

template<class T> tuple2<T,T> *tuple2<T, T>::__mul__(int b) {
    tuple2<T,T> *c = new tuple2<T,T>();
    if(b<=0) return c;
    int hop = this->__len__(); /* XXX merge with list */
    if(hop==1)
        c->units.insert(c->units.begin(), b, this->units[0]);
    else
        for(int i=0; i<b; i++)
            for(int j=0; j<hop; j++)
                c->units.push_back(this->units[j]);
    return c;
}
template<class T> tuple2<T,T> *tuple2<T, T>::__imul__(int b) {
    return __mul__(b);
}

/*template<class T> void tuple2<T, T>::init(int count, ...) {
    this->units.resize(0);

    va_list ap;
    va_start(ap, count);
    for(int i=0; i<count; i++) {
        T t = va_arg(ap, T);
        this->units.push_back(t);
    }
    va_end(ap);
} */

template<class T> int tuple2<T, T>::__contains__(T a) {
    for(int i=0; i<this->__len__(); i++)
        if(__eq(this->units[i], a))
            return 1;
    return 0;
}

template<class T> int tuple2<T, T>::__eq__(pyobj *p) {
    tuple2<T,T> *b;
    b = (tuple2<T,T> *)p;
    if( b->__len__() != this->__len__()) return 0;
    for(int i = 0; i < this->__len__(); i++)
        if(!__eq(this->units[i], b->units[i]))
            return 0;
    return 1;
}

template<class T> tuple2<T,T> *tuple2<T, T>::__slice__(int x, int l, int u, int s) {
    tuple2<T,T> *c = new tuple2<T,T>();
    this->slice(x, l, u, s, c);
    return c;
}

template<class T> int tuple2<T, T>::__hash__() {
    int seed = 0;
    for(int i = 0; i<this->__len__();i++) {
        seed = hash_combine(seed, hasher<T>(this->units[i]));
    }
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

#ifdef __SS_BIND
template<class T> tuple2<T, T>::tuple2(PyObject *p) {
    if(!PyTuple_Check(p)) 
        throw new TypeError(new str("error in conversion to Shed Skin (tuple expected)"));

    this->__class__ = cl_tuple;
    int size = PyTuple_Size(p);
    for(int i=0; i<size; i++)
        append(__to_ss<T>(PyTuple_GetItem(p, i)));
}

template<class T> PyObject *tuple2<T, T>::__to_py__() {
    int len = this->__len__();
    PyObject *p = PyTuple_New(len);
    for(int i=0; i<len; i++)
        PyTuple_SetItem(p, i, __to_py(this->__getitem__(i)));
    return p;
}
#endif

/* tuple2<A, B> */

template<class A, class B> tuple2<A, B>::tuple2() {
    this->__class__ = cl_tuple;
}

template<class A, class B> tuple2<A, B>::tuple2(int n, A a, B b) {
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

/*template<class A, class B> void tuple2<A, B>::init(int count, A a, B b) {
    first = a;
    second = b;
} */

template<class A, class B> int tuple2<A, B>::__contains__(A a) {
    return __eq(first, a);
}

template<class A, class B> int tuple2<A, B>::__contains__(B b) {
    return __eq(second, b);
}

template<class A, class B> int tuple2<A, B>::__len__() {
    return 2;
}

template<class A, class B> int tuple2<A, B>::__eq__(tuple2<A,B> *b) {
    return __eq(first, b->__getfirst__()) && __eq(second, b->__getsecond__());
}

template<class A, class B> int tuple2<A, B>::__cmp__(pyobj *p) {
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

/* iterators */

template<class T> str *__iter<T>::__repr__() {
    return new str("iterator instance"); 
}

template<class T> __seqiter<T>::__seqiter() {}
template<class T> __seqiter<T>::__seqiter(pyseq<T> *p) {
    this->p = p;
    counter = 0;
}

template<class T> T __seqiter<T>::next() {
    if(counter==p->units.size())
        throw new StopIteration();
    return p->units[counter++];
}

template<class K, class V> __dictiterkeys<K, V>::__dictiterkeys(dict<K, V> *p) {
    this->p = p;
    iter = p->units.begin();
    counter = 0;
}

template<class K, class V> K __dictiterkeys<K, V>::next() {
    if(iter == p->units.end())
        throw new StopIteration();
    return iter++->first;
}

template<class K, class V> __dictitervalues<K, V>::__dictitervalues(dict<K, V> *p) {
    this->p = p;
    iter = p->units.begin();
    counter = 0;
}

template<class K, class V> V __dictitervalues<K, V>::next() {
    if(iter == p->units.end())
        throw new StopIteration();
    return iter++->second;
}

template<class K, class V> __dictiteritems<K, V>::__dictiteritems(dict<K, V> *p) {
    this->p = p;
    iter = p->units.begin();
    counter = 0;
}

template<class K, class V> tuple2<K, V> *__dictiteritems<K, V>::next() {
    if(iter == p->units.end())
        throw new StopIteration();
    tuple2<K, V> *t = new tuple2<K, V>(2, iter->first, iter->second);
    iter++;
    return t;
}

/* builtins */

template<class T> list<T> * __list(pyiter<T> *p) {
    list<T> *result = new list<T>();
    T e;
    __iter<T> *__0;
    FOR_IN(e, p, 0)
        result->append(e);
    END_FOR
    return result;
}

template<class T> list<T> *__list(pyseq<T> *p) {
    list<T> *result = new list<T>();
/*    if(p->__class__ == cl_str_) { // why can't we specialize for str *..
        printf("crap %s!\n", ((str *)p)->unit.c_str());
        return __list((pyiter<T> *)p);
    } */
    result->units = p->units;
    return result;
}

list<str *> *__list(str *);

template<class T> tuple2<T,T> *__tuple(pyiter<T> *p) {
    tuple2<T,T> *result = new tuple2<T,T>();
    T e;
    __iter<T> *__0;
    FOR_IN(e, p, 0)
        result->append(e);
    END_FOR
    return result;
}

template<class T> tuple2<T,T> *__tuple(pyseq<T> *p) {
    tuple2<T,T> *result = new tuple2<T,T>();
    if(p->__class__ == cl_str_) /* why can't we specialize for str *.. */
        return __tuple((pyiter<T> *)p);
    result->units = p->units;
    return result;
}

template<class K, class V> dict<K,V> *__dict(pyiter<tuple2<K,V> *> *p) {
    dict<K,V> *d = new dict<K,V>();
    tuple2<K,V> *t;
    __iter<tuple2<K,V> *> *__0;
    FOR_IN(t, p, 0)
        d->__setitem__(t->__getfirst__(), t->__getsecond__());
    END_FOR
    return d;
}
template <class A> A __sum(pyiter<A> *l, A b) {
    A e;
    __iter<A> *__0;
    FOR_IN(e,l,0)
        b = __add(b, e);
    END_FOR
    return b;
}

template <class A> A __sum(pyiter<A> *l) { return __sum(l, 0); }

int __sum(pyseq<int> *l);
int __sum(pyseq<int> *l, int b);
double __sum(pyseq<int> *l, double b);
double __sum(pyseq<double> *l, double b=0);

template<class T> T __minimum(pyseq<T> *l) {
    int len = l->units.size();
    int i;
    if(len==0)
        throw new ValueError(new str("minimum of empty sequence"));
    T m = l->units[0];
    for(i=1; i<len; i++)
        if( l->units[i] < m )
            m = l->units[i];
    return m;
}

template<class T> T __maximum(pyseq<T> *l) {
    int len = l->units.size();
    int i;
    if(len==0)
        throw new ValueError(new str("maximum of empty sequence"));
    T m = l->units[0];
    for(i=1; i<len; i++)
        if( l->units[i] > m )
            m = l->units[i];
    return m;
}

template<class T> T __max(pyiter<T> *a) {
    T e, max = 0;
    int first = 1;
    __iter<T> *__0;
    FOR_IN(e, a, 0)
        if(first) {
            first = 0;
            max = e;
        }
        else if( __cmp(e,max) == 1 )
            max = e;
    END_FOR
    return max;
}

template<class T> T __max(T a, T b) {
    if(__cmp(a, b)==1) return a;
    return b;
}

template<class T> T __max(T a, T b, T c) {
    if(__cmp(a, b)==1 && __cmp(a, c)==1) return a;
    else if(__cmp(b,c)==1) return b;
    return c;
}

template<class T> T __max(int n, T a, T b, T c, ...) {
    T m = __max(a,b,c);
    va_list ap;
    va_start(ap, c);

    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(t,m)==1) m=t;
    }
    va_end(ap);

    return m;
}

template<> inline int __max(int a, int b) { return __SS_MAX(a,b); }
template<> inline int __max(int a, int b, int c) { return __SS_MAX3(a,b,c); }
template<> inline double __max(double a, double b) { return __SS_MAX(a,b); }
template<> inline double __max(double a, double b, double c) { return __SS_MAX3(a,b,c); }

template<class T> T __min(pyiter<T> *a) {
    T e, min = 0;
    int first = 1;
    __iter<T> *__0;
    FOR_IN(e, a, 0)
        if(first) {
            first = 0;
            min = e;
        }
        else if( __cmp(e,min) == -1 )
            min = e;
    END_FOR
    return min;
}

int __min(pyseq<int> *l);
double __min(pyseq<double> *l);

template<class T> T __min(T a, T b) {
    if( __cmp(a, b) == -1 ) return a;
    return b;
}

template<class T> T __min(T a, T b, T c) {
    if(__cmp(a, b)==-1 && __cmp(a, c)==-1) return a;
    else if(__cmp(b,c)==-1) return b;
    return c;
}

template<class T> T __min(int n, T a, T b, T c, ...) {
    T m = __min(a,b,c);
    va_list ap;
    va_start(ap, c);

    for(int i=0; i<n-3; i++) {
        T t = va_arg(ap, T);
        if(__cmp(t,m)==-1) m=t;
    }
    va_end(ap);

    return m;
}

template<> inline int __min(int a, int b) { return __SS_MIN(a,b); }
template<> inline int __min(int a, int b, int c) { return __SS_MIN3(a,b,c); }
template<> inline double __min(double a, double b) { return __SS_MIN(a,b); }
template<> inline double __min(double a, double b, double c) { return __SS_MIN3(a,b,c); }

template<class A> static inline list<A> *__list_comp_0(list<A> *result, pyiter<A> *a) {
    A e;
    result->clear();

    __iter<A> *__0;
    FOR_IN(e,a,0)
        result->append(e);
    END_FOR
    return result;
}

template <class A> list<A> *sorted(pyiter<A> *x, int (*cmp)(A, A), int key, int reverse) {
    list<A> *r = new list<A>();
    A e;
    __iter<A> *__0;
    FOR_IN(e, x, 0)
        r->append(e);
    END_FOR
    r->sort(cmp, key, reverse);
    return r;
}
template <class A> list<A> *sorted(pyiter<A> *x, int cmp, int key, int reverse) { /* beh */
    return sorted(x, (int (*)(A,A))0, key, reverse); 
}

template <class A> list<A> *sorted(pyseq<A> *x, int (*cmp)(A, A), int key, int reverse) {
    list<A> *r = new list<A>();
    r->units = x->units;
    r->sort(cmp, key, reverse);
    return r;
}
template <class A> list<A> *sorted(pyseq<A> *x, int cmp, int key, int reverse) { /* beh */
    return sorted(x, (int (*)(A,A))0, key, reverse); 
}

list<str *> *sorted(str *x, int (*cmp)(str *, str *), int key, int reverse);
list<str *> *sorted(str *x, int cmp, int key, int reverse); /* beh */

template<class A> class __ss_reverse : public __iter<A> {
public:
    pyseq<A> *p;
    int i;
    __ss_reverse(pyseq<A> *p) {
        this->p = p;
        i = len(p)-1;
    }

    A next() {
        if(i>=0)
            return p->units[i--];
        throw new StopIteration;
    }
};

template <class A> __iter<A> *reversed(pyiter<A> *x) { 
    return new __ss_reverse<A>(__list(x));
}
template <class A> __iter<A> *reversed(pyseq<A> *x) {
    return new __ss_reverse<A>(x);
}
__iter<str *> *reversed(str *s);
__iter<int> *reversed(__xrange *x); 

template<class A> class __enumiter : public __iter<tuple2<int, A> *> {
public:
    __iter<A> *p;
    int i;

    __enumiter(pyiter<A> *p) {
        this->p = ___iter(p);
        i = 0;
    }

    tuple2<int, A> *next() {
        return new tuple2<int, A>(2, i++, p->next());
    }
};

template <class A> __iter<tuple2<int, A> *> *enumerate(pyiter<A> *x) {
    return new __enumiter<A>(x);
}

template <class A> list<tuple2<A,A> *> *__zip1(pyiter<A> *a) {
    list<A> la;
    list<tuple2<A,A> *> *result;
    __list_comp_0(&la, a);
    int __1, __2, i;
    result = (new list<tuple2<A,A> *>());

    FAST_FOR(i,0,len(&la),1,1,2)
        result->append((new tuple2<A,A>(1, la.units[i])));
    END_FOR
    return result;
}

template <class A, class B> list<tuple2<A, B> *> *__zip2(pyiter<A> *a, pyiter<B> *b) {
    list<int> *__0;
    list<A> la;
    list<B> lb;
    int __1, __2, i;
    list<tuple2<A, B> *> *result;

    __list_comp_0(&la, a);
    __list_comp_0(&lb, b);
    result = (new list<tuple2<A, B> *>());

    FAST_FOR(i,0,__min(len(&la), len(&lb)),1,1,2)
        result->append((new tuple2<A, B>(2, la.units[i], lb.units[i])));
    END_FOR
    return result;
}

template <class A, class B> list<tuple2<A, B> *> *__zip2(pyseq<A> *a, pyseq<B> *b) {
    if(a->__class__ == cl_str_ || b->__class__ == cl_str_) /* XXX */
        return __zip2(((pyiter<A> *)((str *)a)), ((pyiter<B> *)((str *)b))); 
    list<tuple2<A, B> *> *result;
    result = new list<tuple2<A, B> *>();

    int n = __min(len(a), len(b));
    result->units.reserve(n);

    tuple2<A, B> *v = new tuple2<A, B>[n];

    for(int i=0; i<n; i++) {
        v[i].__init2__(a->units[i], b->units[i]);
        result->units.push_back(&v[i]);
    }

    return result;
}

template <class A> list<tuple2<A,A> *> *__zip3(pyiter<A> *a, pyiter<A> *b, pyiter<A> *c) {
    list<int> *__0;
    list<A> la, lb, lc;
    int __1, __2, i;

    list<tuple2<A,A> *> *result;

    __list_comp_0(&la, a);
    __list_comp_0(&lb, b);
    __list_comp_0(&lc, c);

    result = (new list<tuple2<A,A> *>());

    FAST_FOR(i,0,__min(len(&la), len(&lb), len(&lc)),1,1,2)
        result->append((new tuple2<A,A>(3, la.units[i], lb.units[i], lc.units[i])));
    END_FOR
    return result;
}

template <class A> list<tuple2<A,A> *> *__zip3(pyseq<A> *a, pyseq<A> *b, pyseq<A> *c) {
    if(a->__class__ == cl_str_ || b->__class__ == cl_str_ || c->__class__ == cl_str_) /* XXX */
        return __zip3(((pyiter<A> *)((str *)a)), ((pyiter<A> *)((str *)b)), ((pyiter<A> *)((str *)c)));
    list<tuple2<A, A> *> *result;
    result = new list<tuple2<A, A> *>();

    int n = __min(__min(len(a), len(b)), len(c));
    result->units.reserve(n);

    tuple2<A, A> *v = new tuple2<A, A>[n];

    for(int i=0; i<n; i++) {
        v[i].units.resize(3);
        v[i].units[0] = a->units[i];
        v[i].units[1] = b->units[i];
        v[i].units[2] = c->units[i];
        result->units.push_back(&v[i]);
    }

    return result;
}

/* pow */

template<class A, class B> double __power(A a, B b);
template<> double __power(double a, int b);
template<> double __power(int a, double b);

complex *__power(complex *a, complex *b);
complex *__power(complex *a, int b);
complex *__power(complex *a, double b);

template<class A> A __power(A a, A b);
template<> double __power(double a, double b);
template<> int __power(int a, int b);

int __power(int a, int b, int c);

inline int __power2(int a) { return a*a; }
inline double __power2(double a) { return a*a; }
inline int __power3(int a) { return a*a*a; }
inline double __power3(double a) { return a*a*a; }

/* division */

template<class A, class B> double __divs(A a, B b);
template<> inline double __divs(int a, double b) { return (double)a/b; }
template<> inline double __divs(double a, int b) { return a/((double)b); }

template<class A> A __divs(A a, A b);
template<> inline double __divs(double a, double b) { return a/b; }
template<> inline int __divs(int a, int b) {
    if(a<0 && b>0) return (a-b+1)/b;
    else if(b<0 && a>0) return (a-b-1)/b;
    else return a/b;
}

template<class A, class B> double __floordiv(A a, B b);
template<> inline double __floordiv(int a, double b) { return floor((double)a/b); }
template<> inline double __floordiv(double a, int b) { return floor(a/((double)b)); }

template<class A> inline A __floordiv(A a, A b) { return a->__floordiv__(b); }
template<> inline double __floordiv(double a, double b) { return floor(a/b); }
template<> inline int __floordiv(int a, int b) { return (int)floor((double)a/b); } /* XXX */

template<class A> A __mods(A a, A b);
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
template<> inline double __mods(int a, double b) { return __mods((double)a, b); }
template<> inline double __mods(double a, int b) { return __mods(a, (double)b); }

template<class A> inline tuple2<A, A> *divmod(A a, A b) { return a->__divmod__(b); }
template<> inline tuple2<double, double> *divmod(double a, double b) {
    return new tuple2<double, double>(2, __floordiv(a,b), __mods(a,b));
}
template<> inline tuple2<int, int> *divmod(int a, int b) {
    return new tuple2<int, int>(2, __floordiv(a,b), __mods(a,b));
}
template<class A, class B> tuple2<double, double> *divmod(A a, B b);
template<> inline tuple2<double, double> *divmod(double a, int b) { return divmod(a, (double)b); } 
template<> inline tuple2<double, double> *divmod(int a, double b) { return divmod((double)a, b); }

tuple2<complex *, complex *> *divmod(complex *a, double b);
tuple2<complex *, complex *> *divmod(complex *a, int b);

/* dict.fromkeys */

namespace __dict__ {
    template<class A, class B> dict<A, B> *fromkeys(pyiter<A> *f, B b) {
        dict<A, B> *d = new dict<A, B>();
        A e;
        __iter<A> *__0;
        FOR_IN(e, f, 0)
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
        vals->append(__box(t->__getitem__(i)));
    return __mod4(fmt, vals);
}

template<class A, class B> str *__modtuple(str *fmt, tuple2<A,B> *t) {
    list<pyobj *> *vals = new list<pyobj *>(2, __box(t->__getfirst__()), __box(t->__getsecond__()));
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
        vals->append(__box(d->__getitem__(names->__getitem__(i))));
    return __mod4(v, vals);
}

/* boxing */

template<class T> T __box(T t) { return t; }
int_ *__box(int);
int_ *__box(bool);
float_ *__box(double);

/* any, all */

template<class A> int any(pyiter<A> *a) {
    A b;
    __iter<A> *__0;
    FOR_IN(b,a,0)
        if(___bool(b))
            return 1;
    END_FOR
    return 0;
}

template<class A> int all(pyiter<A> *a) {
    A b;
    __iter<A> *__0;
    FOR_IN(b,a,0)
        if(!___bool(b))
            return 0;
    END_FOR
    return 1;
}

} // namespace __shedskin__
#endif
