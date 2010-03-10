# http://docs.python.org/dev/_sources/library/heapq.txt

def heappush(heap, item):
    heap[0] = item

def heappop(heap):
    return heap[0]

def heappushpop(heap, item):
    heap[0] = item
    return heap[0]

def heapify(x):
    pass

def heapreplace(heap, item):
    heap[0] = item
    return heap[0]

def merge(*iterables):
    yield iter(iterables).next()

def nlargest(n, iterable): # TODO , key = None
    elem = iter(iterable).next()
    #key(elem)
    yield elem

def nsmallest(n, iterable): # TODO , key = None
    elem = iter(iterable).next()
    #key(elem)
    yield elem
