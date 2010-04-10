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

template<class T, class U, template <class V, class W> class X, template <class Y> class Cmp> inline void _siftdown(X<T, U>& heap, __ss_int startpos, __ss_int pos) {
    assert(startpos < heap.size());
    assert(pos < heap.size());

    Cmp<T> cmp;

    T item = heap[pos];

    while (pos > startpos) {
        __ss_int parentpos = (pos - 1) / 2;
	T parent = heap[parentpos];

	if (cmp(item, parent) >= 0) {
	    break;
	}

	heap[pos] = parent;
	pos = parentpos;
    }

    heap[pos] = item;
}

template<class T, class U, template <class V, class W> class X> inline void _siftdown(X<T, U>& heap, __ss_int startpos, __ss_int pos) {
    _siftdown<T, U, X, Cmp>(heap, startpos, pos);
}

template<class T> inline void _siftdown(list<T> *heap, __ss_int startpos, __ss_int pos) {
    _siftdown(heap->units, startpos, pos);
}

template<class T, class U, template <class V, class W> class X, template <class Y> class Cmp> inline void _siftup(X<T, U>& heap, __ss_int pos) {
    assert(pos < heap.size());

    Cmp<T> cmp;

    __ss_int startpos = pos;
    __ss_int endpos = heap.size();

    T item = heap[pos];

    for (; ; ) {
        __ss_int leftsonpos = 2 * pos + 1;
        __ss_int rightsonpos = leftsonpos + 1;

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

    _siftdown<T, U, X, Cmp>(heap, startpos, pos);
}

template<class T, class U, template <class V, class W> class X> inline void _siftup(X<T, U>& heap, __ss_int pos) {
    _siftup<T, U, X, Cmp>(heap, pos);
}

template<class T> inline void _siftup(list<T> *heap, __ss_int pos) {
    _siftup(heap->units, pos);
}

/* Basic operations */

template<class T, class U, template <class V, class W> class X, template <class Y> class Cmp> inline void heappush(X<T, U>& heap, T item) {
    heap.push_back(item);
    _siftdown<T, U, X, Cmp>(heap, 0, heap.size() - 1);
}

template<class T, class U, template <class V, class W> class X> inline void heappush(X<T, U>& heap, T item) {
    heappush<T, U, X, Cmp>(heap, item);
}

template<class T> inline void heappush(list<T> *heap, T item) {
    heappush(heap->units, item);
}

template<class T, class U, template <class V, class W> class X, template <class Y> class Cmp> T heappop(X<T, U>& heap) {
    T item = heap.front();
    heap[0] = heap.back();
    _siftup<T, U, X, Cmp>(heap, 0);
    heap.pop_back();
    return item;
}

template<class T, class U, template <class V, class W> class X> T heappop(X<T, U>& heap) {
    return heappop<T, U, X, Cmp>(heap);
}

template<class T> inline T heappop(list<T> *heap) {
    return heappop(heap->units);
}

template<class T, class U, template <class V, class W> class X, template <class Y> class Cmp> T heappushpop(X<T, U>& heap, T item) {
    Cmp<T> cmp;

    if (!heap.size() ||
	cmp(item, heap.front()) < 0) {
        return item;
    }

    T item2 = heap[0];
    heap[0] = item;
    _siftup<T, U, X, Cmp>(heap, 0);
    return item2;
}

template<class T, class U, template <class V, class W> class X> T heappushpop(X<T, U>& heap, T item) {
    return heappushpop<T, U, X, Cmp>(heap, item);
}

template<class T> inline T heappushpop(list<T> *heap, T item) {
    return heappushpop(heap->units, item);
}

template<class T, class U, template <class V, class W> class X, template <class Y> class Cmp> inline void heapify(X<T, U>& heap) {
    for (__ss_int i = heap.size() / 2 - 1; i > -1; --i) {
        _siftup<T, U, X, Cmp>(heap, i);
    }
}

template<class T, class U, template <class V, class W> class X> inline void heapify(X<T, U>& heap) {
    heapify<T, U, X, Cmp>(heap);
}

template<class T> inline void heapify(list<T> *heap) {
    heapify(heap->units);
}

template<class T, class U, template <class V, class W> class X, template <class Y> class Cmp> T heapreplace(X<T, U>& heap, T item) {
    T item2 = heap[0];
    heap[0] = item;
    _siftup<T, U, X, Cmp>(heap, 0);
    return item2;
}

template<class T, class U, template <class V, class W> class X> T heapreplace(X<T, U>& heap, T item) {
    return heapreplace<T, U, X, Cmp>(heap, item);
}

template<class T> inline T heapreplace(list<T> *heap, T item) {
    return heapreplace(heap->units, item);
}

/* Advanced operations */

template<class T> class mergeiter;
template<class T> inline mergeiter<T> *merge(__ss_int iterable_count, pyiter<T> *iterable, ...);

template<class T> class mergeiter : public __iter<T> {
public:
    typedef std::pair<__ss_int, T> iter_heap;
    typedef std::allocator<iter_heap> iter_heapallocator;

    bool exhausted;
    __GC_VECTOR(__iter<T> *) iters;
    std::vector<iter_heap, iter_heapallocator> heap;

    mergeiter();
    mergeiter(pyiter<T> *iterable);

    void push_iter(pyiter<T> *iterable);

    T next();

    friend mergeiter<T> *merge<T>(__ss_int iterable_count, pyiter<T> *iterable, ...);
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

template<class T> T mergeiter<T>::next() {
    if (this->exhausted) {
        throw new StopIteration();
    }

    if (!this->heap.size()) {
        for (__ss_int i = 0; i < this->iters.size(); ++i) {
	  try  {
	      heappush<iter_heap, iter_heapallocator, std::vector, CmpSecond>(this->heap, iter_heap(i, this->iters[i]->next()));
	  } catch (StopIteration *) {
	  }
	}
	if (!this->heap.size()) {
	    this->exhausted = true;
	    throw new StopIteration();
	}
    }

    iter_heap it = heappop<iter_heap, iter_heapallocator, std::vector, CmpSecond>(this->heap);

    try  {
        heappush<iter_heap, iter_heapallocator, std::vector, CmpSecond>(this->heap, iter_heap(it.first, this->iters[it.first]->next()));
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
template<class T> inline mergeiter<T> *merge(__ss_int iterable_count, pyiter<T> *iterable, ...) {
    mergeiter<T> *iter = new mergeiter<T>(iterable);

    va_list ap;
    va_start(ap, iterable);

    while (--iterable_count) {
        iter->push_iter(va_arg(ap, pyiter<T> *));
    }

    va_end(ap);

    return iter;
}

template<class T, template <class Y> class Cmp> class nheapiter : public __iter<T> {
public:
    __ss_int index;
    std::vector<T> values;

    nheapiter();
    nheapiter(__ss_int n, pyiter<T> *iterable);

    T next();
};

template<class T, template <class Y> class Cmp> inline nheapiter<T, Cmp>::nheapiter() {
    this->index = 0;
}
template<class T, template <class Y> class Cmp> inline nheapiter<T, Cmp>::nheapiter(__ss_int n, pyiter<T> *iterable) {
    __iter<T> *iter = iterable->__iter__();
    std::vector<T> heap;

    try {
      for (__ss_int i = 0; i < n; ++i)
        heappush<T, std::allocator<T>, std::vector, Cmp>(heap, iter->next());
      for (; ; ) {
        heappushpop<T, std::allocator<T>, std::vector, Cmp>(heap, iter->next());
      }
    } catch (StopIteration *) {
        while (!heap.empty())
            this->values.push_back(heappop<T, std::allocator<T>, std::vector, Cmp>(heap));
    }

    this->index = values.size();
}

template<class T, template <class Y> class Cmp> T nheapiter<T, Cmp>::next() {
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
