# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

def heapify(x):
    __cmp(x[0], x[0])

def heapify_max(x):
    heapify(x)

def heappush(heap, item):
    heap[0] = item
    __cmp(item, item)

def heappush_max(heap, item):
    heappush(heap, item)

def heappop(heap):
    return heap[0]

def heappop_max(heap):
    return heappop(heap)

def heappushpop(heap, item):
    heap[0] = item
    __cmp(item, item)
    return heap[0]

def heappushpop_max(heap, item):
    return heappushpop(heap, item)

def heapreplace(heap, item):
    heap[0] = item
    __cmp(item, item)
    return heap[0]

def heapreplace_max(heap, item):
    return heapreplace(heap, item)

def merge(*iterables):
    item = iter(iterables).__next__()
    __cmp(item, item)
    yield item

def nlargest(n, iterable): # TODO , key = None
    item = iter(iterable).__next__()
    __cmp(item, item)
    #key(elem)
    yield item

def nsmallest(n, iterable): # TODO , key = None
    item = iter(iterable).__next__()
    __cmp(item, item)
    #key(elem)
    yield item
