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

# def merge(*iterables):
#     pass

# def nlargest(n, iterable, key = None):
#     pass

# def nsmallest(n, iterable, key = None):
#     pass
