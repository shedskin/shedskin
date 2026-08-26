/* Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE) */

#ifndef __COLLECTIONS_HPP
#define __COLLECTIONS_HPP

#include "builtin.hpp"
#include <deque>

using namespace __shedskin__;

namespace __collections__ {

template <class A> class deque;
template <class T> class __dequeiter;
template <class K, class V> class Counter;
template <class K, class V> class __counterelements;

extern class_ *cl_deque;
extern class_ *cl_defaultdict;
extern class_ *cl_counter;
template <class A> class deque : public pyiter<A> {
public:
#ifdef __SS_NOGC
    std::deque<A> units;
    typename std::deque<A>::iterator iter;
#else
    std::deque<A, gc_allocator<A> > units;
    typename std::deque<A, gc_allocator<A> >::iterator iter;
#endif
    __ss_int maxlen = -1;

    /* XXX modulo rotate */

    deque(pyiter<A> *iterable=0, __ss_int _maxlen=-1) {
        this->__class__ = cl_deque;
        if(_maxlen < -1)
            throw new ValueError(new str("maxlen must be non-negative"));
        this->maxlen = _maxlen;
        if(iterable)
            extend(iterable);
    }

    deque<A> *copy() {
        deque<A> *result = new deque<A>();
        result->units = units;
        result->maxlen = maxlen;
        return result;
    }

    void *append(A a) {
        units.push_back(a);
        if(maxlen != -1 && units.size() > maxlen)
            units.pop_front();
        return NULL;
    }

    void *appendleft(A a) {
        units.push_front(a);
        if(maxlen != -1 && units.size() > maxlen)
            units.pop_back();
        return NULL;
    }

    void *insert(__ss_int index, A a) {
        if(maxlen != -1 && units.size() == maxlen)
            throw new IndexError(new str("deque already at its maximum size"));
        __ss_int len = this->__len__();
        if(index < 0)
            index = (len + index < 0) ? 0 : len + index;
        else if(index > len)
            index = len;
        units.insert(units.begin() + index, a);
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

    __ss_bool __eq__(pyobj *p) {
        deque<A> *b = (deque<A> *)p;
        size_t len = units.size();
        if(b->units.size() != len)
            return False;
        for(size_t i = 0; i < len; i++)
            if(!__eq(units[i], b->units[i]))
                return False;
        return True;
    }

    __ss_int __hash__() {
        throw new TypeError(new str("unhashable type: 'deque'"));
    }

    __ss_bool __contains__(A value) {
        iter = units.begin();
        while(iter != units.end()) {
            if(__eq(*iter, value))
                return True;
            iter++;
        }
        return False;
    }

    __ss_int __len__() {
        return (__ss_int)units.size();
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
        r->unit += "]";
        if(this->maxlen != -1)
            r->unit += ", maxlen=" + __str(this->maxlen)->unit;
        r->unit += ")";
        return r;
    }

    template<class U> void *extend(U *iter_) {
        typename U::for_in_unit e;
        typename U::for_in_loop __3;
        int __2;
        U *__1;
        FOR_IN(e,iter_,1,2,3)
           append(e);
        END_FOR
        return NULL;
    }

    template<class U> void *extendleft(U *iter_) {
        typename U::for_in_unit e;
        typename U::for_in_loop __3;
        int __2;
        U *__1;
        FOR_IN(e,iter_,1,2,3)
           appendleft(e);
        END_FOR
        return NULL;
    }

   void *remove(A value) {
       iter = units.begin();
       while(iter != units.end()) {
           if(__eq(*iter, value)) {
               units.erase(iter);
               return NULL;
           }
           iter++;
       }
       throw new ValueError(new str("deque.remove(x): x not in deque"));
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

   void *reverse() {
       std::reverse(units.begin(), units.end());
       return NULL;
   }

   __ss_int count(A value) {
       __ss_int result = 0;
       iter = units.begin();
       while(iter != units.end()) {
            if(__eq(*iter, value))
                result++;
            iter++;
       }
       return result;
   }

   __ss_int index(A value, __ss_int start, __ss_int stop) {
       __ss_int one = 1;
       slicenr(7, start, stop, one, this->__len__());
       for(__ss_int i=start; i < stop; i++) {
           if(__eq(units[i], value))
               return i;
       }
       throw new ValueError(new str("value is not in deque"));
   }

   __ss_int index(A value) {
       return index(value, 0, this->__len__());
   }

   __ss_int index(A value, __ss_int start) {
       return index(value, start, this->__len__());
   }

   __ss_int truth() {
       return !units.empty();
   }

   deque<A> *__copy__() {
       return copy();
   }

   deque<A> *__deepcopy__(dict<void *, pyobj *> *memo) {
       deque<A> *c = new deque<A>();
       memo->__setitem__(this, c);
       for(__ss_int i=0; i<this->__len__(); i++)
           c->units.push_back(__deepcopy(this->units[i], memo));
       c->maxlen = maxlen;
       return c;
   }

};

template <class T> class __dequeiter : public __iter<T> {
public:
    deque<T> *p;
    size_t i, size;

    __dequeiter(deque<T> *d) {
        p = d;
        size = p->units.size();
        i = 0;
    }

    T __next__() {
        if(i == size)
            throw new StopIteration();
        return p->units[i++];
    }
};

template <class T> class __dequereviter : public __iter<T> {
public:
    deque<T> *p;
    __ss_int i;

    __dequereviter(deque<T> *p_) {
        p = p_;
        i = (__ss_int)(p_->units.size())-1;
    }

    T __next__() {
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
    defaultdict(V (*func_)()=NULL) {
        this->__class__ = cl_defaultdict;
        func = func_;
    }

    defaultdict(V (*func_)(), dict<K, V> *d) : dict<K,V>(d) {
        this->__class__ = cl_defaultdict;
        func = func_;
    }

    defaultdict(V (*func_)(), pyiter<tuple2<K, V> *> *i) { /* XXX */
        this->__class__ = cl_defaultdict;
        func = func_;
        tuple2<K, V> *k;
        typename pyiter<tuple2<K, V> *>::for_in_loop __3;
        int __2;
        pyiter<tuple2<K, V> *> *__1;
        FOR_IN(k,i,1,2,3)
            this->__setitem__(k->__getfirst__(), k->__getsecond__());
        END_FOR
    }

    V __getitem__(K key) {
        typename __GC_DICT<K, V>::iterator it = this->gcd.find(key);
        if(it == this->gcd.end())
            return __missing__(key);
        return (*it).second;
    }

    V __missing__(K k) {
        if(func) {
            V v = func();
            this->__setitem__(k, v);
            return v;
        }
        throw new KeyError(repr(k));
    }

    void *__addtoitem__(K key, V value) {
        typename __GC_DICT<K, V>::iterator it = this->gcd.find(key);
        if(it == this->gcd.end()) {
            if(func)
                this->__setitem__(key, __add(func(), value));
            else
                throw new KeyError(repr(key));
        }
        else {
            (*it).second = __add((*it).second, value);
        }

        return NULL;
    }

    str *__repr__() {
        return __add_strs(3, new str("defaultdict("), dict<K, V>::__repr__(), new str(")"));
    }

    defaultdict<K, V> *copy() {
        defaultdict<K,V> *c = new defaultdict<K,V>(func);
        c->gcd = this->gcd;
        return c;
    }

    defaultdict<K, V> *__copy__() {
        return copy();
    }

    defaultdict<K, V> *__deepcopy__(dict<void *, pyobj *> *memo) {
        defaultdict<K,V> *c = new defaultdict<K,V>(func);
        memo->__setitem__(this, c);
        K e;
        typename dict<K,V>::for_in_loop __3;
        int __2;
        dict<K,V> *__1;
        FOR_IN(e,this,1,2,3)
            c->__setitem__(__deepcopy(e, memo), __deepcopy(this->__getitem__(e), memo));
        END_FOR
        return c;
    }

    defaultdict<K, V> *__or__(dict<K,V> *other) {
        defaultdict<K,V> *result = copy();
        result->update(other);
        return result;
    }

    defaultdict<K, V> *__ior__(dict<K,V> *other) {
        this->update(other);
        return this;
    }

#ifdef __SS_BIND
    defaultdict(PyObject *p) { /* XXX merge with dict */
        if(!PyDict_Check(p))
            throw new TypeError(new str("error in conversion to Shed Skin (dictionary expected)"));

        this->__class__ = cl_defaultdict;
        PyObject *key, *value;

        PyObject *iter = PyObject_GetIter(p);
        while ((key = PyIter_Next(iter))) {
            value = PyDict_GetItem(p, key);
            this->__setitem__(__to_ss<K>(key), __to_ss<V>(value));
            Py_DECREF(key);
        }
        Py_DECREF(iter);
    }
#endif

};

/* Counter.elements(): repeats each key `value` times (counts <= 0 skipped) */
template <class K, class V> class __counterelements : public __iter<K> {
public:
    Counter<K, V> *p;
    typename __GC_DICT<K, V>::iterator it;
    V left;

    __counterelements(Counter<K, V> *p) {
        this->p = p;
        it = p->gcd.begin();
        left = 0;
    }

    K __next__() {
        while(left <= 0) {
            if(it == p->gcd.end())
                __throw_stop_iteration();
            left = (*it).second;
            if(left <= 0)
                ++it;
        }
        K result = (*it).first;
        left = left - 1;
        if(left <= 0)
            ++it;
        return result;
    }

    inline str *__str__() { return new str("Counter_elements"); }
};

template <class K, class V> class Counter : public dict<K, V> {
public:
    Counter() {
        this->__class__ = cl_counter;
    }

    Counter(dict<K, V> *d) : dict<K, V>(d) {
        this->__class__ = cl_counter;
    }

    Counter(pyiter<K> *i) { /* count element occurrences */
        this->__class__ = cl_counter;
        K e;
        typename pyiter<K>::for_in_loop __3;
        int __2;
        pyiter<K> *__1;
        FOR_IN(e, i, 1, 2, 3)
            __addtoitem__(e, 1);
        END_FOR
    }

#ifdef __SS_BIND
    Counter(PyObject *p) { /* XXX merge with dict */
        if(!PyDict_Check(p))
            throw new TypeError(new str("error in conversion to Shed Skin (dictionary expected)"));

        this->__class__ = cl_counter;
        PyObject *key, *value;

        PyObject *iter = PyObject_GetIter(p);
        while ((key = PyIter_Next(iter))) {
            value = PyDict_GetItem(p, key);
            this->__setitem__(__to_ss<K>(key), __to_ss<V>(value));
            Py_DECREF(key);
        }
        Py_DECREF(iter);
    }
#endif

    /* unlike defaultdict, missing keys are never inserted */
    V __getitem__(K key) {
        typename __GC_DICT<K, V>::iterator it = this->gcd.find(key);
        if(it == this->gcd.end())
            return __missing__(key);
        return (*it).second;
    }

    V __missing__(K /*key*/) {
        return V();
    }

    void *__addtoitem__(K key, V value) { /* backs `counter[key] += n` */
        typename __GC_DICT<K, V>::iterator it = this->gcd.find(key);
        if(it == this->gcd.end())
            this->__setitem__(key, value);
        else
            (*it).second = (*it).second + value;
        return NULL;
    }

    str *__repr__() {
        return __add_strs(3, new str("Counter("), dict<K, V>::__repr__(), new str(")"));
    }

    Counter<K, V> *copy() {
        Counter<K, V> *c = new Counter<K, V>();
        c->gcd = this->gcd;
        return c;
    }
    Counter<K, V> *__copy__() {
        return copy();
    }
    Counter<K, V> *__deepcopy__(dict<void *, pyobj *> *memo) {
        Counter<K, V> *c = new Counter<K, V>();
        memo->__setitem__(this, c);
        K e;
        typename dict<K, V>::for_in_loop __3;
        int __2;
        dict<K, V> *__1;
        FOR_IN(e, this, 1, 2, 3)
            c->__setitem__(__deepcopy(e, memo), __deepcopy(this->__getitem__(e), memo));
        END_FOR
        return c;
    }

    /* update()/subtract(): mapping arg copies/subtracts counts as-is;
       iterable arg counts occurrences of each element. A single templated
       method (branching via if constexpr) is required here, not two
       differently-named overloads: unlike constructors, regular method
       calls are codegen'd using the literal source method name, so C++
       overload resolution -- not name-based redirection -- has to do the
       dict-vs-iterable dispatch. See dict<K,V>::update for the same
       pattern. The Python-level updateiter()/subtractiter()/__ior__iter()
       stubs exist only so CPA can type-check the non-dict call shape. */
    template <class U> void *update(U *other) {
        if constexpr (std::is_base_of_v<dict<K, V>, U>) {
            for(auto &kv : other->gcd)
                __addtoitem__(kv.first, kv.second);
        } else {
            K e;
            typename U::for_in_loop __3;
            int __2;
            U *__1;
            FOR_IN(e, other, 1, 2, 3)
                __addtoitem__(e, 1);
            END_FOR
        }
        return NULL;
    }

    template <class U> void *subtract(U *other) {
        if constexpr (std::is_base_of_v<dict<K, V>, U>) {
            for(auto &kv : other->gcd)
                __addtoitem__(kv.first, -kv.second);
        } else {
            K e;
            typename U::for_in_loop __3;
            int __2;
            U *__1;
            FOR_IN(e, other, 1, 2, 3)
                __addtoitem__(e, -1);
            END_FOR
        }
        return NULL;
    }

    /* n<0 (default) means "all", matching e.g. deque's maxlen=-1 convention */
    list<tuple2<K, V> *> *most_common(__ss_int n=-1) {
        list<tuple2<K, V> *> *result = new list<tuple2<K, V> *>();
        for(auto &kv : this->gcd)
            result->units.push_back(new tuple2<K, V>(2, kv.first, kv.second));
        std::stable_sort(result->units.begin(), result->units.end(),
            [](tuple2<K, V> *a, tuple2<K, V> *b) { return a->second > b->second; });
        if(n >= 0 && (size_t)n < result->units.size())
            result->units.resize((size_t)n);
        return result;
    }

    __counterelements<K, V> *elements() {
        return new __counterelements<K, V>(this);
    }

    /* +, -, &, | all drop non-positive results, matching CPython */
    Counter<K, V> *__add__(Counter<K, V> *other) {
        return __combine(other, true, true);
    }
    Counter<K, V> *__sub__(Counter<K, V> *other) {
        return __combine(other, false, true);
    }
    Counter<K, V> *__and__(Counter<K, V> *other) {
        Counter<K, V> *result = new Counter<K, V>();
        K e;
        typename dict<K, V>::for_in_loop __3;
        int __2;
        dict<K, V> *__1;
        FOR_IN(e, this, 1, 2, 3)
            V a = this->__getitem__(e);
            V b = other->__getitem__(e);
            V m = (a < b) ? a : b;
            if(m > 0)
                result->__setitem__(e, m);
        END_FOR
        return result;
    }
    Counter<K, V> *__or__(Counter<K, V> *other) {
        Counter<K, V> *result = new Counter<K, V>();
        K e;
        typename dict<K, V>::for_in_loop __3;
        int __2;
        dict<K, V> *__1;
        FOR_IN(e, this, 1, 2, 3)
            V a = this->__getitem__(e);
            V b = other->__getitem__(e);
            V m = (a > b) ? a : b;
            if(m > 0)
                result->__setitem__(e, m);
        END_FOR
        FOR_IN(e, other, 1, 2, 3)
            if(!this->__contains__(e)) {
                V b = other->__getitem__(e);
                if(b > 0)
                    result->__setitem__(e, b);
            }
        END_FOR
        return result;
    }

    Counter<K, V> *__pos__() {
        return __combine(new Counter<K, V>(), true, true);
    }
    Counter<K, V> *__neg__() {
        Counter<K, V> *result = new Counter<K, V>();
        K e;
        typename dict<K, V>::for_in_loop __3;
        int __2;
        dict<K, V> *__1;
        FOR_IN(e, this, 1, 2, 3)
            V v = this->__getitem__(e);
            if(v < 0)
                result->__setitem__(e, -v);
        END_FOR
        return result;
    }

    Counter<K, V> *__iadd__(Counter<K, V> *other) {
        this->gcd = __combine(other, true, true)->gcd;
        return this;
    }
    Counter<K, V> *__isub__(Counter<K, V> *other) {
        this->gcd = __combine(other, false, true)->gcd;
        return this;
    }
    Counter<K, V> *__iand__(Counter<K, V> *other) {
        this->gcd = __and__(other)->gcd;
        return this;
    }
    template <class U> Counter<K, V> *__ior__(U *other) {
        if constexpr (std::is_same_v<Counter<K, V>, U>) {
            this->gcd = __or__(other)->gcd;
        } else {
            Counter<K, V> *o = new Counter<K, V>(other);
            this->gcd = __or__(o)->gcd;
        }
        return this;
    }

private:
    /* shared helper for __add__/__sub__/__pos__: unions keys from both
       operands, combines with +/-, keeps positive results only when
       positive_only is set */
    Counter<K, V> *__combine(Counter<K, V> *other, bool add, bool positive_only) {
        Counter<K, V> *result = new Counter<K, V>();
        K e;
        typename dict<K, V>::for_in_loop __3;
        int __2;
        dict<K, V> *__1;
        FOR_IN(e, this, 1, 2, 3)
            V a = this->__getitem__(e);
            V b = other->__getitem__(e);
            V v = add ? (a + b) : (a - b);
            if(!positive_only || v > 0)
                result->__setitem__(e, v);
        END_FOR
        FOR_IN(e, other, 1, 2, 3)
            if(!this->__contains__(e)) {
                V a = V();
                V b = other->__getitem__(e);
                V v = add ? (a + b) : (a - b);
                if(!positive_only || v > 0)
                    result->__setitem__(e, v);
            }
        END_FOR
        return result;
    }
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
        FOR_IN(e,f,1,2,3)
            d->__setitem__(e, b);
        END_FOR
        return d;
    }

    template<class A> defaultdict<A, void *> *fromkeys(pyiter<A> *f) {
        return fromkeys(f, (void *)0);
    }

}
#endif
