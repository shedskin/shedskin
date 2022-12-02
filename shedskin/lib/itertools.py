# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)

# http://docs.python.org/dev/_sources/library/itertools.txt

# Infinite Iterators

def count(start = 0, step = 1):
    yield start

def cycle(iterable):
    yield iter(iterable).__next__()

def repeat(object, times = 0):
    yield object

# Iterators terminating on the shortest input iterableuence

def chain(*iterables):
    yield iter(iterables).__next__()

def compress(data, selectors):
    iter(selectors).__next__()
    yield iter(data).__next__()

def __pred_elem(predicate, iterable):
    elem = iter(iterable).__next__()
    predicate(elem)
    return elem

def dropwhile(predicate, iterable):
    yield __pred_elem(predicate, iterable)

def groupby(iterable, key = lambda x: x):
    yield key(iter(iterable).__next__()), iter(iterable)

def ifilterfalse(predicate, iterable):
    yield __pred_elem(predicate, iterable)

def takewhile(predicate, iterable):
    yield __pred_elem(predicate, iterable)

def islice(iterable, start, stop = -1, step = -1):
    'Known limitations: cannot distinguish between 0 and None for the stop argument'
    yield iter(iterable).__next__()

#def starmap(function, iterable):
#    yield func(*iterable[0])

def tee(iterable, n = 2):
    return iter(iterable), iter(iterable)

def izip_longest(__kw_fillvalue=None, *iterables):
    'Known limitations: iterables must all be of the same type, cannot distinguish between 0 and None for the return value'
    yield iter(iterables).__next__(),
def __izip_longest2(iterable1, iterable2, __kw_fillvalue=None):
    yield iter(iterable1).__next__(), iter(iterable2).__next__()

# Combinatoric generators

def product(__kw_repeat=1, *iterables):
    'Known limitations: iterables must all be of the same type if they are more than two'
    yield iter(iterables).__next__(),
def __product2(iterable1, iterable2, __kw_repeat=1):
    yield iter(iterable1).__next__(), iter(iterable2).__next__()

def permutations(iterable, r = None):
    yield iter(iterable).__next__(),

def combinations(iterable, r):
    yield iter(iterable).__next__(),

def combinations_with_replacement(iterable, r):
    yield iter(iterable).__next__(),
