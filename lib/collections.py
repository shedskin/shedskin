class deque(pyiter):
    def __init__(self, iterable=None):
        self.unit = iterable.unit
    def append(self, x):
        self.unit = x
    def appendleft(self, x):
        self.unit = x
    def __getitem__(self, i):
        return self.unit
    def __setitem__(self, i, e):
        self.unit = e
    def __contains__(self, e):
        return 1
    def pop(self):
        return self.unit
    def popleft(self):
        return self.unit
    def __len__(self):
        return 1
    def __iter__(self):
        return __iter(self.unit)
    def clear(self):
        pass
    def extend(self, b):
        self.unit = b.unit
    def extendleft(self, b):
        self.unit = b.unit
    def remove(self, e):
        pass
    def rotate(self, n):
        pass
    def __delitem__(self, i):
        pass
    def truth(self):
        return 1
    def __copy__(self):
        return self
    def __deepcopy__(self):
        return self


d1 = deque([1])
d2 = deque(['1'])
