# Copyright 2005-2026 Mark Dufour and contributors; License Expat (See LICENSE)

class deque(pyiter):
    def __init__(self, iterable=None, maxlen=None):
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
        return {self.unit: self.value}  # TODO defaultdict

    def __delete__(self, k):  # TODO difference with delitem?
        self.__key__(k)

    def fromkeys(l, b=None):
        d = defaultdict()
        d.__setunit__(iter(l).__next__(), b)
        return d
    fromkeys = staticmethod(fromkeys) # XXX classmethod
