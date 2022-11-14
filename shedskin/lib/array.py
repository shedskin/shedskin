# Copyright 2005-2011 Mark Dufour and contributors; License Expat (See LICENSE)


class array:
    def __init__(self, flag, it=None):
        self.typecode = ''
        self.itemsize = 0

    def __init_int__(self, flag, it=None):
        self.unit = 1
        self.__init__(flag)
    def __init_float__(self, flag, it=None):
        self.unit = 1.0
        self.__init__(flag)
    def __init_str__(self, flag, it=None):
        self.unit = ''
        self.__init__(flag)

    def tolist(self):
        return [self.unit]
    def tostring(self):
        return b''
    def tobytes(self):
        return b''

    def fromlist(self, l):
        pass
    def fromstring(self, s):
        pass
    def frombytes(self, s):
        pass

    def extend(self, it):
        pass

    def pop(self, i=-1):
        return self.unit
    def remove(self, e):
        pass

    def __getitem__(self, i):
        return self.unit
    def __setitem__(self, i, e):
        pass
    def __delitem__(self, i):
        pass

    def insert(self, i, e):
        pass
    def append(self, e):
        pass

    def tofile(self, f):
        pass
    def fromfile(self, f, n):
        pass

    def count(self, e):
        return 1
    def index(self, e):
        return 1
    def __contains__(self, e):
        return True

    def byteswap(self):
        pass
    def reverse(self):
        pass

    def __add__(self, b):
        return self
    def __mul__(self, b):
        return self
    def __with_int__(self): # int.__mul__ etc.
        return self

    def __len__(self):
        return 1

    def __iter__(self):
        return __iter(self.unit)

    def __slice__(self, x, lower, upper, step):
        return self
    def __delslice__(self, a, b):
        pass
    def __setslice__(self, x, lower, upper, step, r):
        pass
    def __delete__(self, x, a=1, b=1, s=1):
        pass

    def __copy__(self):
        return self
