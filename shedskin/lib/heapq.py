# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

# http://docs.python.org/dev/_sources/library/heapq.txt

def heappush(heap, item):
    heap[0] = item
    cmp(item, item)

def heappop(heap):
    return heap[0]

def heappushpop(heap, item):
    heap[0] = item
    cmp(item, item)
    return heap[0]

def heapify(x):
    cmp(x[0], x[0])

def heapreplace(heap, item):
    heap[0] = item
    cmp(item, item)
    return heap[0]

def merge(*iterables):
    item = iter(iterables).next()
    cmp(item, item)
    yield item

def nlargest(n, iterable): # TODO , key = None
    item = iter(iterable).next()
    cmp(item, item)
    #key(elem)
    yield item

def nsmallest(n, iterable): # TODO , key = None
    item = iter(iterable).next()
    cmp(item, item)
    #key(elem)
    yield item
