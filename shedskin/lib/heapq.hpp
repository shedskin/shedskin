/* Copyright (c) 2009-2026 Jérémie Roquet <arkanosis@gmail.com>; License Expat (See LICENSE) */

#ifndef HEAPQ_HPP
#define HEAPQ_HPP

#include "builtin.hpp"
#include <cassert>

using namespace __shedskin__;

namespace __heapq__ {

/* Local helpers */

template<class T> struct Cmp {
    inline __ss_int operator()(T& first, T& second) const {
        return __cmp(first, second);
    }
};
template<class T> struct InvCmp {
    inline __ss_int operator()(T& first, T& second) const {
        return -__cmp(first, second);
    }
};
template<class T> struct CmpSecond {
    inline __ss_int operator()(T& first, T& second) const {
        return __cmp(first.second, second.second);
    }
};

template<template <class Y> class Cmp, class T> inline void _siftdown(T &heap, size_t startpos, size_t pos) {
    assert(startpos < heap.size());
    assert(pos < heap.size());

    using E = typename T::value_type;

    Cmp<E> cmp;

    E item = heap[pos];

    while (pos > startpos) {
        size_t parentpos = (pos - 1) / 2;
        E parent = heap[parentpos];

        if (cmp(item, parent) >= 0) {
            break;
        }

        heap[pos] = parent;
        pos = parentpos;
    }

    heap[pos] = item;
}

template<template <class Y> class Cmp, class T> inline void _siftup(T &heap, size_t pos) {
    assert(pos < heap.size());

    using E = typename T::value_type;

    Cmp<E> cmp;

    size_t startpos = pos;
    size_t endpos = heap.size();

    E item = heap[pos];

    for (;;) {
        size_t leftsonpos = 2 * pos + 1;
        size_t rightsonpos = leftsonpos + 1;

        if (leftsonpos >= endpos) {
            break;
        } else if (rightsonpos < endpos) {
            if (cmp(heap[leftsonpos], heap[rightsonpos]) >= 0) {
                leftsonpos = rightsonpos;
            }
        }

        heap[pos] = heap[leftsonpos];
        pos = leftsonpos;
    }

    heap[pos] = item;

    _siftdown<Cmp>(heap, startpos, pos);
}

/* Basic operations */

template<class T> inline void heapify(list<T> *l) {
    __GC_VECTOR(T) &heap = l->units;
    for (size_t i = heap.size() / 2 - 1; i != std::string::npos; --i) {
        _siftup<Cmp>(heap, i);
    }
}

template<class T> inline void heapify_max(list<T> *l) {
    __GC_VECTOR(T) &heap = l->units;
    for (size_t i = heap.size() / 2 - 1; i != std::string::npos; --i) {
        _siftup<InvCmp>(heap, i);
    }
}

template<template <class Y> class Cmp, class T, class E> inline void heappush(T &heap, E item) {
    heap.push_back(item);
    _siftdown<Cmp>(heap, 0, heap.size() - 1);
}

template<class T> inline void heappush(list<T> *l, T item) {
    heappush<Cmp>(l->units, item);
}

template<class T> inline void heappush_max(list<T> *l, T item) {
    heappush<InvCmp>(l->units, item);
}

template<template <class Y> class Cmp, class T> auto heappop(T &heap) {
    if(!heap.size())
        throw new IndexError(new str("index out of range"));
    auto item = heap.front();
    heap[0] = heap.back();
    _siftup<Cmp>(heap, 0);
    heap.pop_back();
    return item;
}

template<class T> inline T heappop(list<T> *l) {
    return heappop<Cmp>(l->units);
}

template<class T> inline T heappop_max(list<T> *l) {
    return heappop<InvCmp>(l->units);
}

template<template <class Y> class Cmp, class E, class T> E heappushpop(T &heap, E item) {
    Cmp<E> cmp;

    if (!heap.size() || cmp(item, heap.front()) < 0) {
        return item;
    }

    E item2 = heap[0];
    heap[0] = item;
    _siftup<Cmp>(heap, 0);
    return item2;
}

template<class T> inline T heappushpop(list<T> *l, T item) {
    return heappushpop<Cmp>(l->units, item);
}

template<class T> inline T heappushpop_max(list<T> *l, T item) {
    return heappushpop<InvCmp>(l->units, item);
}

template<class T> inline T heapreplace(list<T> *l, T item) {
    __GC_VECTOR(T) &heap = l->units;
    if(!heap.size())
        throw new IndexError(new str("index out of range"));
    T item2 = heap[0];
    heap[0] = item;
    _siftup<Cmp>(heap, 0);
    return item2;
}

template<class T> inline T heapreplace_max(list<T> *l, T item) {
    __GC_VECTOR(T) &heap = l->units;
    if(!heap.size())
        throw new IndexError(new str("index out of range"));
    T item2 = heap[0];
    heap[0] = item;
    _siftup<InvCmp>(heap, 0);
    return item2;
}

/* Advanced operations */

template<class T> class mergeiter;

template<class T> class mergeiter : public __iter<T> {
public:
    typedef std::pair<size_t, T> iter_heap;

    bool exhausted;
    __GC_VECTOR(__iter<T> *) iters;
    std::vector<iter_heap> heap;

    mergeiter();
    mergeiter(pyiter<T> *iterable);

    void push_iter(pyiter<T> *iterable);

    T __next__();

};

template<class T> inline mergeiter<T>::mergeiter() {
    this->exhausted = true;
}
template<class T> inline mergeiter<T>::mergeiter(pyiter<T> *iterable) {
    this->exhausted = false;
    this->push_iter(iterable);
}

template<class T> void mergeiter<T>::push_iter(pyiter<T> *iterable) {
    this->iters.push_back(iterable->__iter__());
}

template<class T> T mergeiter<T>::__next__() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    if (!this->heap.size()) {
        for (size_t i = 0; i < this->iters.size(); ++i) {
            try  {
                heappush<CmpSecond>(this->heap, iter_heap(i, this->iters[i]->__next__()));
            } catch (StopIteration *) {
            }
        }

        if (!this->heap.size()) {
            this->exhausted = true;
            throw new StopIteration();
        }
    }

    iter_heap it = heappop<CmpSecond>(this->heap);

    try  {
        heappush<CmpSecond>(this->heap, iter_heap(it.first, this->iters[it.first]->__next__()));
    } catch (StopIteration *) {
        if (!this->heap.size()) {
            this->exhausted = true;
        }
    }

    return it.second;
}

inline mergeiter<void *> *merge(__ss_int /* iterable_count */) {
    return new mergeiter<void *>();
}
template<class T, class ... Args> mergeiter<T> *merge(__ss_int, pyiter<T> *iterable, Args ... args) {
    mergeiter<T> *iter = new mergeiter<T>(iterable);
    (iter->push_iter((pyiter<T> *)args), ...);
    return iter;
}

template<class T, template <class Y> class Cmp> class nheapiter : public __iter<T> {
public:
    size_t index;
    std::vector<T> values;

    nheapiter();
    nheapiter(__ss_int n, pyiter<T> *iterable);

    T __next__();
};

template<class T, template <class Y> class Cmp> inline nheapiter<T, Cmp>::nheapiter() {
    this->index = 0;
}
template<class T, template <class Y> class Cmp> inline nheapiter<T, Cmp>::nheapiter(__ss_int n, pyiter<T> *iterable) {
    __iter<T> *iter = iterable->__iter__();
    std::vector<T> heap;

    try {
      for (__ss_int i = 0; i < n; ++i)
        heappush<Cmp>(heap, iter->__next__());
      for (; ; ) {
        heappushpop<Cmp>(heap, iter->__next__());
      }
    } catch (StopIteration *) {
        while (!heap.empty())
            this->values.push_back(heappop<Cmp>(heap));
    }

    this->index = values.size();
}

template<class T, template <class Y> class Cmp> T nheapiter<T, Cmp>::__next__() {
    if (!this->index) {
        throw new StopIteration();
    }

    return this->values[--this->index];
}

template<class T> nheapiter<T, Cmp> *nlargest(__ss_int n, pyiter<T> *iterable) {
    return new nheapiter<T, Cmp>(n, iterable);
}

template<class T> nheapiter<T, InvCmp> *nsmallest(__ss_int n, pyiter<T> *iterable) {
    return new nheapiter<T, InvCmp>(n, iterable);
}

void __init();

} // module namespace
#endif
