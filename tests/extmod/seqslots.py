# extension module under test: compile with 'shedskin build -e seqslots',
# then run seqslots_main.py (see README.md)


class Bag:
    # a list-like class: len(), b[i], b[i] = x, 'in' and bool()
    def __init__(self, n):
        self.items = list(range(n))

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]

    def __setitem__(self, i, x):
        self.items[i] = x

    def __contains__(self, x):
        return x in self.items


class SubBag(Bag):
    # inherits all the slots
    def total(self):
        return sum(self.items)


class Table:
    # a dict-like class, also with del t[key]
    def __init__(self):
        self.d = {}

    def __len__(self):
        return len(self.d)

    def __getitem__(self, key):
        return self.d[key]

    def __setitem__(self, key, value):
        self.d[key] = value

    def __delitem__(self, key):
        del self.d[key]

    def __contains__(self, key):
        return key in self.d


class Squares:
    # only __getitem__: read-only, and iterable through the old sequence
    # protocol (until IndexError)
    def __getitem__(self, i):
        if i >= 4:
            raise IndexError('out of range')
        return i * i


class BadLen:
    def __len__(self):
        return -1


if __name__ == '__main__':
    # make sure everything is called with the types used from seqslots_main.py
    b = Bag(3)
    len(b)
    b[0]
    b[0] = 7
    1 in b
    s = SubBag(2)
    s.total()
    t = Table()
    t['a'] = 1
    t['a']
    'a' in t
    len(t)
    del t['a']
    Squares()[1]
    try:
        len(BadLen())
    except ValueError:
        pass
