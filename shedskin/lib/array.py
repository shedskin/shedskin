
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
        return ''

    def fromstring(self, s):
        pass

    def extend(self, it):
        pass

    def fromlist(self, l):
        pass

    def append(self, e):
        pass

    def count(self, e):
        return 1

    def index(self, e):
        return 1

    def pop(self, i=-1):
        return self.unit

    def remove(self, e):
        pass

    def byteswap(self):
        pass

    def reverse(self):
        pass

    def __getitem__(self, i):
        return self.unit

    def __setitem__(self, i, e):
        pass

    def insert(self, i, e):
        pass

    def __iter__(self):
        return __iter(self.unit)

    def __add__(self, b):
        return self

    def __mul__(self, b):
        return self

    def __len__(self):
        return 1

    def tofile(self, f):
        pass

    def fromfile(self, f, n):
        pass

    def __contains__(self, e):
        return True

    def __with_int__(self):
        return self
