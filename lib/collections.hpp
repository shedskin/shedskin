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

    int __setitem__(int i, A value) {
        i = __wrap(this, i);
        units[i] = value;
        return 0;
    } 

    int __delitem__(int i) {
        i = __wrap(this, i);
        units.erase(units.begin()+i);
        return 0;
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
   
   int extend(pyiter<A> *p) {
       __iter<A> *__0;
       A e;
       FOR_IN(e, p, 0)
           append(e);
       END_FOR
       return 0;
   }

   int extendleft(pyiter<A> *p) {
       __iter<A> *__0;
       A e;
       FOR_IN(e, p, 0)
           appendleft(e);
       END_FOR
       return 0;
   }
   
   int remove(A value) {
       iter = units.begin();
       while(iter != units.end()) {
           if(*iter == value) {
               units.erase(iter);
               return 0;
           }
           iter++;
       }
       throw new ValueError(new str("hops"));
   }

   int rotate(int n) {
       if(!units.empty()) {
           n = n % __len__();
           if(n<0) 
               for(int i=0; i>n; i--) 
                   append(popleft());
           else 
               for(int i=0; i<n; i++) 
                   appendleft(pop());
       }
       return 0;
   }
   
   int clear() {
       units.clear();
       return 0;
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

void __init();

} // module namespace
#endif
