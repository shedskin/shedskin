
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

    def extend(self, it):
        pass

    def append(self, e):
        pass

    def __getitem__(self, i):
        return self.unit

    def __iter__(self):
        return __iter(self.unit)
