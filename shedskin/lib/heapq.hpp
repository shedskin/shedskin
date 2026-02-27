/* Copyright (c) 2009-2026 Jérémie Roquet <arkanosis@gmail.com>; License Expat (See LICENSE) */

#ifndef HEAPQ_HPP
#define HEAPQ_HPP

#include "builtin.hpp"
#include <cassert>

using namespace __shedskin__;

namespace __heapq__ {

/* Local helpers */

template<class T, class Key> struct Cmp {
    Key key;
    Cmp(Key key) : key(key) {}

    inline __ss_int operator()(T& first, T& second) const {
        if constexpr (std::is_same_v<Key, int> || std::is_same_v<Key, long int>)
            return __cmp(first, second);
        else
            return __cmp(key(first), key(second));
    }
};

template<class T, class Key> struct InvCmp {
    Key key;
    InvCmp(Key key) : key(key) {}

    inline __ss_int operator()(T& first, T& second) const {
        if constexpr (std::is_same_v<Key, int> || std::is_same_v<Key, long int>)
            return -__cmp(first, second);
        else
            return -__cmp(key(first), key(second));
    }
};

template<class T, class Key> struct CmpSecond {
    Key key;
    CmpSecond(Key key) : key(key) {}

    inline __ss_int operator()(T& first, T& second) const {
        if constexpr (std::is_same_v<Key, int> || std::is_same_v<Key, long int>)
            return __cmp(first.second, second.second);
        else
            return __cmp(key(first.second), key(second.second));
    }
};

template<class T, class Key> struct InvCmpSecond {
    Key key;
    InvCmpSecond(Key key) : key(key) {}

    inline __ss_int operator()(T& first, T& second) const {
        if constexpr (std::is_same_v<Key, int> || std::is_same_v<Key, long int>)
            return -__cmp(first.second, second.second);
        else
            return -__cmp(key(first.second), key(second.second));
    }
};

template<template <class Y, class Z> class Cmp, class T, class Key> inline void _siftdown(T &heap, size_t startpos, size_t pos, Key key) {
    assert(startpos < heap.size());
    assert(pos < heap.size());

    using E = typename T::value_type;

    Cmp<E, Key> cmp(key);

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

template<template <class Y, class Z> class Cmp, class T, class Key> inline void _siftup(T &heap, size_t pos, Key key) {
    assert(pos < heap.size());

    using E = typename T::value_type;

    Cmp<E, Key> cmp(key);

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

    _siftdown<Cmp>(heap, startpos, pos, key);
}

/* Basic operations */

template<class T> inline void heapify(list<T> *l) {
    __GC_VECTOR(T) &heap = l->units;
    for (size_t i = heap.size() / 2 - 1; i != std::string::npos; --i) {
        _siftup<Cmp>(heap, i, 0);
    }
}

template<class T> inline void heapify_max(list<T> *l) {
    __GC_VECTOR(T) &heap = l->units;
    for (size_t i = heap.size() / 2 - 1; i != std::string::npos; --i) {
        _siftup<InvCmp>(heap, i, 0);
    }
}

template<template <class Y, class Z> class Cmp, class Key, class T, class E> inline void heappush(T &heap, E item, Key key) {
    heap.push_back(item);
    _siftdown<Cmp>(heap, 0, heap.size() - 1, key);
}

template<class T> inline void heappush(list<T> *l, T item) {
    heappush<Cmp>(l->units, item, 0);
}

template<class T> inline void heappush_max(list<T> *l, T item) {
    heappush<InvCmp>(l->units, item, 0);
}

template<template <class Y, class Z> class Cmp, class T, class Key> auto heappop(T &heap, Key key) {
    if(!heap.size())
        throw new IndexError(new str("index out of range"));
    auto item = heap.front();
    heap[0] = heap.back();
    _siftup<Cmp>(heap, 0, key);
    heap.pop_back();
    return item;
}

template<class T> inline T heappop(list<T> *l) {
    return heappop<Cmp>(l->units, 0);
}

template<class T> inline T heappop_max(list<T> *l) {
    return heappop<InvCmp>(l->units, 0);
}

template<template <class Y, class Z> class Cmp, class Key, class E, class T> E heappushpop(T &heap, E item, Key key) {
    Cmp<E, Key> cmp(key);

    if (!heap.size() || cmp(item, heap.front()) < 0) {
        return item;
    }

    E item2 = heap[0];
    heap[0] = item;
    _siftup<Cmp>(heap, 0, key);
    return item2;
}

template<class T> inline T heappushpop(list<T> *l, T item) {
    return heappushpop<Cmp>(l->units, item, 0);
}

template<class T> inline T heappushpop_max(list<T> *l, T item) {
    return heappushpop<InvCmp>(l->units, item, 0);
}

template<class T> inline T heapreplace(list<T> *l, T item) {
    __GC_VECTOR(T) &heap = l->units;
    if(!heap.size())
        throw new IndexError(new str("index out of range"));
    T item2 = heap[0];
    heap[0] = item;
    _siftup<Cmp>(heap, 0, 0);
    return item2;
}

template<class T> inline T heapreplace_max(list<T> *l, T item) {
    __GC_VECTOR(T) &heap = l->units;
    if(!heap.size())
        throw new IndexError(new str("index out of range"));
    T item2 = heap[0];
    heap[0] = item;
    _siftup<InvCmp>(heap, 0, 0);
    return item2;
}

/* merge */

template<class T, class Key> class mergeiter : public __iter<T> {
public:
    typedef std::pair<size_t, T> iter_heap;
    Key key;
    bool reverse;

    bool exhausted;
    __GC_VECTOR(__iter<T> *) iters;
    std::vector<iter_heap> heap;

    mergeiter();
    mergeiter(pyiter<T> *iterable, Key key, bool reverse);

    void push_iter(pyiter<T> *iterable);

    T __next__();

};

template<class T, class Key> inline mergeiter<T, Key>::mergeiter() {
    this->exhausted = true;
    this->reverse = false;
}
template<class T, class Key> inline mergeiter<T, Key>::mergeiter(pyiter<T> *iterable, Key key, bool reverse) {
    this->exhausted = false;
    this->key = key;
    this->reverse = reverse;
    this->push_iter(iterable);
}

template<class T, class Key> void mergeiter<T, Key>::push_iter(pyiter<T> *iterable) {
    this->iters.push_back(iterable->__iter__());
}

template<class T, class Key> T mergeiter<T, Key>::__next__() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    if (!this->heap.size()) {
        for (size_t i = 0; i < this->iters.size(); ++i) {
            try  {
                if(reverse)
                    heappush<InvCmpSecond>(this->heap, iter_heap(i, this->iters[i]->__next__()), this->key);
                else
                    heappush<CmpSecond>(this->heap, iter_heap(i, this->iters[i]->__next__()), this->key);
            } catch (StopIteration *) {
            }
        }

        if (!this->heap.size()) {
            this->exhausted = true;
            throw new StopIteration();
        }
    }

    iter_heap it;
    if(reverse)
        it = heappop<InvCmpSecond>(this->heap, this->key);
    else
        it = heappop<CmpSecond>(this->heap, this->key);

    try  {
        if(reverse)
            heappush<InvCmpSecond>(this->heap, iter_heap(it.first, this->iters[it.first]->__next__()), this->key);
        else
            heappush<CmpSecond>(this->heap, iter_heap(it.first, this->iters[it.first]->__next__()), this->key);
    } catch (StopIteration *) {
        if (!this->heap.size()) {
            this->exhausted = true;
        }
    }

    return it.second;
}

inline mergeiter<void *, long int> *merge(__ss_int /* iterable_count */, __ss_int, __ss_bool) {
    return new mergeiter<void *, long int>();
}
template<class T, class Key, class ... Args> mergeiter<T, Key> *merge(__ss_int, Key key, __ss_bool reverse, pyiter<T> *iterable, Args ... args) {
    mergeiter<T, Key> *iter = new mergeiter<T, Key>(iterable, key, reverse.value);
    (iter->push_iter((pyiter<T> *)args), ...);
    return iter;
}

/* nlargest, nsmallest */

template<class T, template <class Y, class Z> class Cmp, class Key> class nheapiter : public __iter<T> {
public:
    size_t index;
    std::vector<T> values;

    nheapiter();
    nheapiter(__ss_int n, pyiter<T> *iterable, Key key);

    T __next__();
};

template<class T, template <class Y, class Z> class Cmp, class Key> inline nheapiter<T, Cmp, Key>::nheapiter() {
    this->index = 0;
}
template<class T, template <class Y, class Z> class Cmp, class Key> inline nheapiter<T, Cmp, Key>::nheapiter(__ss_int n, pyiter<T> *iterable, Key key) {
    __iter<T> *iter = iterable->__iter__();
    std::vector<T> heap;

    try {
      for (__ss_int i = 0; i < n; ++i)
        heappush<Cmp>(heap, iter->__next__(), key);
      for (; ; ) {
        heappushpop<Cmp>(heap, iter->__next__(), key);
      }
    } catch (StopIteration *) {
        while (!heap.empty())
            this->values.push_back(heappop<Cmp>(heap, key));
    }

    this->index = values.size();
}

template<class T, template <class Y, class Z> class Cmp, class Key> T nheapiter<T, Cmp, Key>::__next__() {
    if (!this->index) {
        throw new StopIteration();
    }

    return this->values[--this->index];
}

template<class T, class Key> nheapiter<T, Cmp, Key> *nlargest(Key key, __ss_int n, pyiter<T> *iterable) {
    return new nheapiter<T, Cmp, Key>(n, iterable, key);
}

template<class T, class Key> nheapiter<T, InvCmp, Key> *nsmallest(Key key, __ss_int n, pyiter<T> *iterable) {
    return new nheapiter<T, InvCmp, Key>(n, iterable, key);
}

void __init();

} // module namespace
#endif
