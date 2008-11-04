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

    int append(A a) {
        units.push_back(a);
    }

    int appendleft(A a) {
        units.push_front(a);
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

    A __getitem__(int i) {
        i = __wrap(this, i);
        return units[i];
    }

    void *__setitem__(int i, A value) {
        i = __wrap(this, i);
        units[i] = value;
        return NULL;
    } 

    void *__delitem__(int i) {
        i = __wrap(this, i);
        units.erase(units.begin()+i);
        return NULL;
    }

    int __contains__(A value) {
        iter = units.begin();
        while(iter != units.end()) 
            if(*iter++ == value) 
                return 1;
        return 0;
    }

    int __len__() {
        return units.size();
    }

    __iter<A> *__iter__() {
         return new __dequeiter<A>(this);
    }

    str * __repr__() {
        str *r = new str("deque([");
        for(int i = 0; i<this->__len__();i++) {
            r->unit += repr(units[i])->unit;
            if (i<this->__len__()-1)
                r->unit += ", ";
        }
        r->unit += "])";
        return r;
   }
   
   void *extend(pyiter<A> *p) {
       __iter<A> *__0;
       A e;
       FOR_IN(e, p, 0)
           append(e);
       END_FOR
       return NULL;
   }

   void *extendleft(pyiter<A> *p) {
       __iter<A> *__0;
       A e;
       FOR_IN(e, p, 0)
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

   void *rotate(int n) {
       if(!units.empty()) {
           n = n % __len__();
           if(n<0) 
               for(int i=0; i>n; i--) 
                   append(popleft());
           else 
               for(int i=0; i<n; i++) 
                   appendleft(pop());
       }
       return NULL;
   }
   
   void *clear() {
       units.clear();
       return NULL;
   }

   int truth() {
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
       for(int i=0; i<this->__len__(); i++)
           c->units.push_back(__deepcopy(this->units[i], memo));
       return c;
   }

};

template <class T> class __dequeiter : public __iter<T> {
public:
    deque<T> *p;
    int i, size;

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
    int i;

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

#define __GC_HASH_MAP2 __gnu_cxx::hash_map<K, V, __shedskin__::hashfunc<K>, hasheq<K>, gc_allocator<std::pair<K, V> > >

template <class K, class V> class defaultdict : public dict<K, V> {
    typename __GC_HASH_MAP2::iterator iter;

public:
    defaultdict() {
    }

    defaultdict(dict<K, V> *d) {

    }

    defaultdict(pyiter<tuple2<K, V> *> *i) {

    }

    V __getitem__(K k) {
        iter = this->units.find(k);
        if(iter == this->units.end()) return __missing__(k);
        return iter->second;
    }

    V __missing__(K k) { 
        V v = new (typename dereference<V>::type)(); 
        return (this->units[k] = v);
    } 

    void *_addtoitem__(K k, V v) {
        iter = this->units.find(k);
        if(iter == this->units.end()) {
            V defval = new (typename dereference<V>::type)();
            this->units[k] = __add(defval, v);
        }
        else  
            iter->second = __add(iter->second, v);
        return NULL;
    } 

    str *__repr__() {
        return __add_strs(3, new str("defaultdict("), dict<K, V>::__repr__(), new str(")"));
    }
};

#define __GC_HASH_MAPI __gnu_cxx::hash_map<K, int, __shedskin__::hashfunc<K>, hasheq<K>, gc_allocator<std::pair<K, int> > >

template<class K> class defaultdict<K, int> : public dict<K, int> {
    typename __GC_HASH_MAPI::iterator iter;
public:
    defaultdict() {
    }

    defaultdict(dict<K, int> *d) {
        this->units = d->units;
    }

    defaultdict(pyiter<tuple2<K, int> *> *i) {
       __iter<tuple2<K, int> *> *__0;
       tuple2<K, int> *k;

       FOR_IN(k, i, 0)
           this->units[k->__getfirst__()] = k->__getsecond__();
       END_FOR
    }

    int __missing__(K k) {
        return (this->units[k] = 0);
    }

    int __getitem__(K k) {
        iter = this->units.find(k);
        if(iter == this->units.end()) return __missing__(k);
        return iter->second;
    }

    void *__addtoitem__(K k, int v) {
        iter = this->units.find(k);
        if(iter == this->units.end()) 
            this->units[k] = v;
        else  
            iter->second = iter->second+v;
        return NULL;
    } 

    str *__repr__() {
        return __add_strs(3, new str("defaultdict("), dict<K, int>::__repr__(), new str(")"));
    }
};


#define __GC_HASH_MAPD __gnu_cxx::hash_map<K, double, __shedskin__::hashfunc<K>, hasheq<K>, gc_allocator<std::pair<K, double> > >

template<class K> class defaultdict<K, double> : public dict<K, double> {
    typename __GC_HASH_MAPD::iterator iter;
public:
    defaultdict() {
    }

    defaultdict(dict<K, double> *d) {

    }

    defaultdict(pyiter<tuple2<K, double> *> *i) {

    }

    double __missing__(K k) {
        return (this->units[k] = 0);
    }

    double __getitem__(K k) {
        iter = this->units.find(k);
        if(iter == this->units.end()) return __missing__(k);
        return iter->second;
    }

    void *__addtoitem__(K k, double v) {
        iter = this->units.find(k);
        if(iter == this->units.end()) 
            this->units[k] = v;
        else  
            iter->second = iter->second+v;
        return NULL;
    } 

    str *__repr__() {
        return __add_strs(3, new str("defaultdict("), dict<K, double>::__repr__(), new str(")"));
    }
};

void __init();

} // module namespace

namespace __defaultdict__ {
    using __collections__::defaultdict;

    template<class A, class B> defaultdict<A, B> *fromkeys(pyiter<A> *f, B b) {
        defaultdict<A, B> *d = new defaultdict<A, B>();
        A e;
        __iter<A> *__0;
        FOR_IN(e, f, 0)
            d->__setitem__(e, b);
        END_FOR
        return d;
    }

    template<class A> defaultdict<A, int> *fromkeys(pyiter<A> *f) {
        return fromkeys(f, 0);
    }

}
#endif
