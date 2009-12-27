#ifndef HEAPQ_HPP
#define HEAPQ_HPP

#include <cassert>

#include "builtin.hpp"

using namespace __shedskin__;

namespace __heapq__ {

/* Local helpers */

template<class T> inline void _siftdown(list<T> *heap, int startpos, int pos) {
    assert(startpos < heap->units.size());
    assert(pos < heap->units.size());

    T item = heap->units[pos];

    while (pos > startpos) {
        int parentpos = (pos - 1) / 2;
	T parent = heap->units[parentpos];

	if (__cmp(item, parent) >= 0) {
	    break;
	}

	heap->units[pos] = parent;
	pos = parentpos;
    }

    heap->units[pos] = item;
}

template<class T> inline void _siftup(list<T> *heap, int pos) {
    assert(pos < heap->units.size());

    int startpos = pos;
    int endpos = heap->units.size();

    T item = heap->units[pos];

    for (; ; ) {
        int leftsonpos = 2 * pos + 1;
        int rightsonpos = leftsonpos + 1;

	if (leftsonpos >= endpos) {
	    break;
	} else if (rightsonpos < endpos) {
	    if (__cmp(heap->units[leftsonpos], heap->units[rightsonpos]) >= 0) {
	        leftsonpos = rightsonpos;
	    }
	}

	heap->units[pos] = heap->units[leftsonpos];
	pos = leftsonpos;
    }

    heap->units[pos] = item;

    _siftdown(heap, startpos, pos);
}

/* Basic operations */

template<class T> void heappush(list<T> *heap, T item) {
    heap->units.push_back(item);
    _siftdown(heap, 0, heap->units.size() - 1);
}

template<class T> T heappop(list<T> *heap) {
    T item = heap->units.front();
    heap->units[0] = heap->units.back();
    _siftup(heap, 0);
    heap->units.pop_back();
    return item;
}

template<class T> T heappushpop(list<T> *heap, T item) {
    if (!heap->units.size() ||
	__cmp(item, heap->units.front()) < 0) {
        return item;
    }

    T item2 = heap->units[0];
    heap->units[0] = item;
    _siftup(heap, 0);
    return item2;
}

template<class T> void heapify(list<T> *heap) {
    for (int i = heap->units.size() / 2 - 1; i > -1; --i) {
        _siftup(heap, i);
    }
}

template<class T> T heapreplace(list<T> *heap, T item) {
  T item2 = heap->units[0];
  heap->units[0] = item;
  _siftup(heap, 0);
  return item2;
}

/* Advanced operations */

// template<class T> T merge(*iterables) {
  // TODO
// }

// template<class T> T nlargest(n, iterable, key = None) {
  // TODO
// }

// template<class T> T nsmallest(n, iterable, key = None) {
  // TODO
// }

void __init();

} // module namespace
#endif
