# conversion of python ints (and floats, complex numbers) at the extension
# module boundary: see intrange_main.py. build with and without --int32.

import sys


def maxint():
    return sys.maxsize


def ident(x):
    return x


def add(a, b):
    return a + b


def ident_float(x):
    return x


def ident_complex(x):
    return x


def first(l):
    return l[0]


def lookup(d, k):
    return d[k]


def pair_sum(t):
    return t[0] + t[1]


def set_sum(s):
    return sum(s)


class Holder:
    def __init__(self, n):
        self.n = n

    def get(self):
        return self.n


if __name__ == '__main__':
    # make sure everything is called with the types used from intrange_main.py
    maxint()
    ident(1)
    add(1, 2)
    ident_float(1.5)
    ident_complex(1j)
    first([1])
    lookup({1: 2}, 1)
    pair_sum((1, 2))
    set_sum({1, 2})
    h = Holder(1)
    h.n = 2
    h.get()
