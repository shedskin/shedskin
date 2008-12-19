
class array:
    def __init__(self, flags, arg=None):
        pass

    def fromstring(self, s):
        pass
    def fromlist(self, l):
        pass
    def fromfile(self, f, n):
        pass
    def tolist(self):
        return [1]
    def tofile(self, f):
        pass
    def tostring(self):
        return ''
            
    def __slice__(self, x, l, u, s):  
        return self
    def __len__(self):
        return 1

    def __delete__(self, x, a=1, b=1, s=1):
        pass

    def __setitem__(self, i, e):
        pass
