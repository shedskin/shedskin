# http://docs.python.org/dev/_sources/library/itertools.txt

# Infinite Iterators

def count(start = 0, step = 1):
    yield start

def cycle(iterable):
    yield iterable[0]

def repeat(object, times = 0):
    yield object

# Iterators terminating on the shortest input iterableuence

def chain(*iterables):
    yield iter(iterables).next()

def compress(data, selectors):
    yield data[0]

def dropwhile(predicate, iterable):
    predicate(iterable[0])
    yield iterable[0]

def groupby(iterable, key = lambda x: x):
    key(iterable[0])
    yield iterable[0], iterable.__iter__()

def ifilter(predicate, iterable):
    predicate(iterable[0])
    yield iterable[0]

def ifilterfalse(predicate, iterable):
    predicate(iterable[0])
    yield iterable[0]

def islice(iterable, start, stop = -1, step = -1):
    'Known limitations: cannot distinguish between 0 and None for the stop argument'
    yield iterable[0]

def imap(function, *iterables):
    yield function(iter(iterables).next())

#def starmap(function, iterable):
#    yield func(*iterable[0])

def tee(iterable, n = 2):
    return iterable, iterable

def takewhile(predicate, iterable):
    predicate(iterable[0])
    yield iterable[0]

def izip(*iterables):
    'Known limitations: iterables must all be of the same type'
    yield iter(iterables).next(),

def izip_longest(*iterables, **kwargs):
    'Known limitations: iterables must all be of the same type, cannot distinguish between 0 and None for the return value'
    __kw_fillvalue = None
    yield iter(iterables).next(),

# Combinatoric generators

def product(*iterables, **kwargs):
    'Known limitations: iterables must all be of the same type'
    __kw_repeat = 1
    yield iter(iterables).next(),

def permutations(iterable, r = None):
    yield iterable[0],

def combinations(iterable, r):
    yield iterable[0],

def combinations_with_replacement(iterable, r):
    yield iterable[0],
