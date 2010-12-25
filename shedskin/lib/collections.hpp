#ifndef __COLLECTIONS_HPP
#define __COLLECTIONS_HPP

#include "builtin.hpp"
#include <deque>

using namespace __shedskin__;

namespace __collections__ {

template <class A> class deque;
template <class T> class __dequeiter;

extern class_ *cl_deque;
template <class A> class deque : public pyiter<A> {
public:
    std::deque<A, gc_allocator<A> > units;
    typename std::deque<A, gc_allocator<A> >::iterator iter;

    /* XXX modulo rotate, specialized reversed, copy, deepcopy */

    deque(pyiter<A> *iterable=0) {
        this->__class__ = cl_deque;
        if(iterable)
            extend(iterable);
    }

    void *append(A a) {
        units.push_back(a);
        return NULL;
    }

    void *appendleft(A a) {
        units.push_front(a);
        return NULL;
    }

    A pop() {
        if(units.empty())
            throw new IndexError(new str("pop from an empty deque"));
        A x = units.back();
        units.pop_back();
        return x;
    }

    A popleft() {
        if(units.empty())
            throw new IndexError(new str("pop from an empty deque"));
        A x = units.front();
        units.pop_front();
        return x;
    }

    A __getitem__(__ss_int i) {
        i = __wrap(this, i);
        return units[i];
    }

    void *__setitem__(__ss_int i, A value) {
        i = __wrap(this, i);
        units[i] = value;
        return NULL;
    }

    void *__delitem__(__ss_int i) {
        i = __wrap(this, i);
        units.erase(units.begin()+i);
        return NULL;
    }

    __ss_bool __contains__(A value) {
        iter = units.begin();
        while(iter != units.end())
            if(*iter++ == value)
                return True;
        return False;
    }

    __ss_int __len__() {
        return units.size();
    }

    __iter<A> *__iter__() {
         return new __dequeiter<A>(this);
    }

    str * __repr__() {
        str *r = new str("deque([");
        for(__ss_int i = 0; i<this->__len__();i++) {
            r->unit += repr(units[i])->unit;
            if (i<this->__len__()-1)
                r->unit += ", ";
        }
        r->unit += "])";
        return r;
    }

    template<class U> void *extend(U *iter) {
        typename U::for_in_unit e;
        typename U::for_in_loop __3;
        int __2;
        U *__1;
        FOR_IN_NEW(e,iter,1,2,3)
           append(e);
        END_FOR
        return NULL;
    }

    template<class U> void *extendleft(U *iter) {
        typename U::for_in_unit e;
        typename U::for_in_loop __3;
        int __2;
        U *__1;
        FOR_IN_NEW(e,iter,1,2,3)
           appendleft(e);
        END_FOR
        return NULL;
    }

   void *remove(A value) {
       iter = units.begin();
       while(iter != units.end()) {
           if(*iter == value) {
               units.erase(iter);
               return NULL;
           }
           iter++;
       }
       throw new ValueError(new str("hops"));
       return NULL;
   }

   void *rotate(__ss_int n) {
       if(!units.empty()) {
           n = n % __len__();
           if(n<0)
               for(__ss_int i=0; i>n; i--)
                   append(popleft());
           else
               for(__ss_int i=0; i<n; i++)
                   appendleft(pop());
       }
       return NULL;
   }

   void *clear() {
       units.clear();
       return NULL;
   }

   __ss_int truth() {
       return !units.empty();
   }

   deque<A> *__copy__() {
       deque<A> *c = new deque<A>();
       c->units = this->units;
       return c;
   }

   deque<A> *__deepcopy__(dict<void *, pyobj *> *memo) {
       deque<A> *c = new deque<A>();
       memo->__setitem__(this, c);
       for(__ss_int i=0; i<this->__len__(); i++)
           c->units.push_back(__deepcopy(this->units[i], memo));
       return c;
   }

};

template <class T> class __dequeiter : public __iter<T> {
public:
    deque<T> *p;
    __ss_int i, size;

    __dequeiter(deque<T> *p) {
        this->p = p;
        size = p->units.size();
        i = 0;
    }

    T next() {
        if(i == size)
            throw new StopIteration();
        return p->units[i++];
    }
};

template <class T> class __dequereviter : public __iter<T> {
public:
    deque<T> *p;
    __ss_int i;

    __dequereviter(deque<T> *p) {
        this->p = p;
        i = p->units.size()-1;
    }

    T next() {
        if(i >= 0)
            return p->units[i--];
        throw new StopIteration();
    }
};

template <class T> __iter<T> *reversed(deque<T> *d) {
    return new __dequereviter<T>(d);
}

template <class K, class V> class defaultdict : public dict<K, V> {
    V (*func)();

public:
    defaultdict(V (*func)()=NULL) {
        this->func = func;
    }

    defaultdict(V (*func)(), dict<K, V> *d) : dict<K,V>(d) {
        this->func = func;
    }

    defaultdict(V (*func)(), pyiter<tuple2<K, V> *> *i) { /* XXX */
        this->func = func;
        tuple2<K, __ss_int> *k;
        typename pyiter<tuple2<K, V> *>::for_in_loop __3;
        int __2;
        pyiter<tuple2<K, V> *> *__1;
        FOR_IN_NEW(k,i,1,2,3)
            this->__setitem__(k->__getfirst__(), k->__getsecond__());
        END_FOR
    }

    V __getitem__(K key) {
        register long hash = hasher<K>(key);
        register dictentry<K, V> *entry;
        entry = lookup(key, hash);
        if (entry->use != active)
            return __missing__(key);
        return entry->value;
    }

    V __missing__(K k) {
        if(func) {
            V v = func();
            this->__setitem__(k, v);
            return v;
        }
        throw new KeyError(repr(k));
    }

    void *__addtoitem__(K key, V value) { /* XXX */
        register long hash = hasher<K>(key);
        register dictentry<K, V> *entry;
        entry = lookup(key, hash);
        if (entry->use != active) {
            if(func)
                __setitem__(key, __add(func(), value));
            else
                throw new KeyError(repr(key));
        } else
            entry->value = __add(entry->value, value);
        return NULL;
    }

    str *__repr__() {
        return __add_strs(3, new str("defaultdict("), dict<K, V>::__repr__(), new str(")"));
    }

#ifdef __SS_BIND
    defaultdict(PyObject *p) { /* XXX merge with dict */
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
#endif

};

void __init();

} // module namespace

namespace __defaultdict__ {
    using __collections__::defaultdict;

    template<class A, class B> defaultdict<A, B> *fromkeys(pyiter<A> *f, B b) {
        defaultdict<A, B> *d = new defaultdict<A, B>();
        A e;
        typename pyiter<A>::for_in_loop __3;
        int __2;
        pyiter<A> *__1;
        FOR_IN_NEW(e,f,1,2,3)
            d->__setitem__(e, b);
        END_FOR
        return d;
    }

    template<class A> defaultdict<A, __ss_int> *fromkeys(pyiter<A> *f) {
        return fromkeys(f, 0);
    }

}
#endif
