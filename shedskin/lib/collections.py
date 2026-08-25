# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

class deque(pyiter):
    def __init__(self, iterable=None, maxlen=-1):
        self.unit = iter(iterable).__next__()
        self.maxlen = 1

    def append(self, x):
        self.unit = x
    def appendleft(self, x):
        self.unit = x
    def extend(self, b):
        self.unit = b.unit
    def extendleft(self, b):
        self.unit = b.unit

    def rotate(self, n):
        pass

    def pop(self):
        return self.unit
    def popleft(self):
        return self.unit

    def remove(self, e):
        pass
    def clear(self):
        pass

    def count(self, value):
        return 1

    def index(self, value, start=None, stop=None):
        return 1

    def reverse(self):
        pass

    def copy(self):
        d = deque()
        d.unit = self.unit
        return d

    def insert(self, index, value):
        pass

    def __getitem__(self, i):
        return self.unit
    def __setitem__(self, i, e):
        self.unit = e
    def __delitem__(self, i):
        pass

    def __contains__(self, e):
        return True

    def __len__(self):
        return 1
    def __iter__(self):
        return __iter(self.unit)

    def __copy__(self):
        return self
    def __deepcopy__(self):
        return self

class defaultdict(dict):
    def __init__(self, func=None, x=None): # XXX
        self.value = func()

    def __initdict__(self, func, d):
        value = func()
        value = d.value
        self.__setunit__(d.unit, value)

    def __inititer__(self, func, i):
        value = func()
        item = iter(i).__next__()
        value = item[1]
        self.__setunit__(item[0], value)

    def __getitem__(self, key):
        self.__missing__(key)
        return self.value

    def __missing__(self, key):  # TODO not called by get?
        self.__key__(key)
        self.unit = key
        return self.value

    def copy(self):
        d = defaultdict()
        d.__setunit__(self.unit, self.value)
        return d

    def __delete__(self, k):  # TODO difference with delitem?
        self.__key__(k)

    def fromkeys(l, b=None):
        d = defaultdict()
        d.__setunit__(iter(l).__next__(), b)
        return d
    fromkeys = staticmethod(fromkeys) # XXX classmethod

class Counter(dict):
    # Counter.fromkeys is intentionally unsupported, matching CPython
    # (it raises NotImplementedError there too).

    def __init__(self, iterable=None):
        # counts are always int (matches the overwhelmingly common usage,
        # and the counter[k] += 1 idiom needs value's type pinned here,
        # the way defaultdict(int) pins it via the factory call)
        self.value = 1

    def __initdict__(self, d): # Counter(mapping): counts copied as-is
        self.__setunit__(d.unit, d.value)

    def __inititer__(self, i): # Counter(iterable): count occurrences
        item = iter(i).__next__()
        self.__setunit__(item, 1)

    def __missing__(self, key): # unlike defaultdict, never inserts
        self.__key__(key)
        return self.value

    def __getitem__(self, key):
        self.__missing__(key)
        return self.value

    def __addtoitem__(self, key, value): # backs `counter[k] += n`
        self.__setunit__(key, value)

    def __repr__(self):
        self.unit.__repr__()
        self.value.__repr__()
        return ''
    def __str__(self):
        return self.__repr__()

    def copy(self):
        c = Counter()
        c.__setunit__(self.unit, self.value)
        return c
    def __copy__(self):
        return self.copy()
    def __deepcopy__(self, memo):
        return self.copy()

    def update(self, d):
        self.__setunit__(d.unit, d.value)
    def updateiter(self, i):
        item = iter(i).__next__()
        self.__setunit__(item, 1)

    def subtract(self, d):
        self.__setunit__(d.unit, d.value)
    def subtractiter(self, i):
        item = iter(i).__next__()
        self.__setunit__(item, 1)

    def most_common(self, n=-1):
        return [(self.unit, self.value)]

    def elements(self):
        yield self.unit

    def __add__(self, other):
        c = Counter()
        c.__setunit__(self.unit, self.value)
        return c
    def __sub__(self, other):
        c = Counter()
        c.__setunit__(self.unit, self.value)
        return c
    def __and__(self, other):
        c = Counter()
        c.__setunit__(self.unit, self.value)
        return c
    def __or__(self, other):
        c = Counter()
        c.__setunit__(self.unit, self.value)
        return c

    def __pos__(self):
        c = Counter()
        c.__setunit__(self.unit, self.value)
        return c
    def __neg__(self):
        c = Counter()
        c.__setunit__(self.unit, self.value)
        return c

    def __iadd__(self, other): # -> Counter (not None): reassigned by `c += ...`
        self.__setunit__(self.unit, self.value)
        return self
    def __isub__(self, other):
        self.__setunit__(self.unit, self.value)
        return self
    def __iand__(self, other):
        self.__setunit__(self.unit, self.value)
        return self
    def __ior__(self, d):
        self.__setunit__(d.unit, d.value)
        return self
    def __ior__iter(self, i):
        item = iter(i).__next__()
        self.__setunit__(item, 1)
        return self
